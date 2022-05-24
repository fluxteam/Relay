import asyncio
from typing import Dict, List, Any, Optional
from hikari.events.base_events import ExceptionEvent
from pyconduit import block, Job, Node
from relay.classes import Events
from relay.database import MongoDB
from relay.listeners import ListenerBase
from hikari import GatewayBot
from relay.utils import make_run, parse_run
from relay.enums import RelayFlags
from relay.commons import DEPLOY_TYPE, get_server_config, marketplace, sio, snowflaked


@block(tags = ["SKIP"])
async def dummy(**kwargs):
    """
    A dummy ConduitBlock.
    """

@block(label = "WORKFLOW.SELF_GET", tags = ["SKIP"])
async def get_itself(*, value : Any):
    return value


class Dispatcher:
    """
    Relay allows server moderators to do actions that they want when any X event happens,
    however because of this reason, events must be connected to the same listener.
    """

    def __init__(self, db : MongoDB, bot : GatewayBot, id : str) -> None:
        self.db = db
        self.bot = bot
        self.market = marketplace
        self.id = id
    
    def create_relay_event(self):
        """
        Creates a general Relay event and returns it.
        """
        async def on_relay_event(event : Events, guild_id : str, user_id : Optional[str], payload : dict, model : ListenerBase):
            # Ignore if payload is empty or guild_id is blank.
            if (not payload) or (not guild_id):
                return
            # Ignore events that triggered by Relay.
            elif (user_id == self.id):
                return
            print(f"-- Received {'REMOTE' if event.is_remote() else 'DEFAULT'} event named {event.value} for {guild_id}")
            # Fetch workflow IDs from database.
            docs = self.db("relay-actions", guild_id).list_items()
            actions = {}
            functions = {}
            for doc in docs:
                d = parse_run(doc)
                # Allow functions to be defined
                # in every action.
                if d[2] == "FUNCTION":
                    functions[d[3]] = self.db("relay-actions", guild_id, doc).read()
                elif model.check_listener(*d):
                    actions[doc] = self.db("relay-actions", guild_id, doc).read()
            # Check if current action IDs are empty.
            if (not actions) and (not event.is_remote()):
                return
            # Get server config.
            language, config = get_server_config(guild_id = guild_id)
            # Convert server flags names to RelayFlags enum.
            flags = [RelayFlags[x] for x in config.get("flags", []) if x in RelayFlags.__members__]
            # If event is package install/uninstall, run post install jobs.
            # TODO: Refactor.
            if event in [Events.PACKAGE_INSTALL, Events.PACKAGE_UNINSTALL]:
                pack = self.market.pack(payload["pack_code"])
                pack_contents = pack.contents(payload["pack_version"])
                workflow = pack_contents.install_workflow if event == Events.PACKAGE_INSTALL else pack_contents.uninstall_workflow
                if workflow:
                    workflow_data = workflow.export(pack_contents)
                    workflow_data["pack_data"]["parameters"] = payload["data"]
                    actions = {make_run("PACK", (payload["pack_code"], payload["pack_version"], ), event.value, snowflaked()) : workflow_data}
            # If there is no action has set in the server, ignore.
            if not actions:
                return
            else:
                for KEY, VALUE in actions.items():
                    # Check if action is disabled.
                    if VALUE.get("enabled", True) == False:
                        continue
                    # Add blocks.
                    blocks = [
                        dummy
                    ]
                    pack_strings = {}
                    # Check if action triggered by a package.
                    if "pack" in VALUE:
                        flags.append(RelayFlags.PACKAGE)
                        # Check if pack author is Flux.
                        p = self.market.pack(VALUE["pack"]["name"])
                        if p.author_id == "flux":
                            flags.append(RelayFlags.FLUX_PACKAGE)
                        # Get package blocks.
                        c = p.contents(version = VALUE["pack"]["version"])
                        # Add strings to payload.
                        pack_strings = c.strings.get(language.language, {})
                        # Get blocks from package.
                        for x in c.blocks.values():
                            # If method is init(), don't register but execute it instead.
                            if x.__name__ == "init":
                                x()
                            else:
                                blocks.append(block(x, private = True))
                    guild = self.bot.cache.get_available_guild(guild_id)
                    # Create new conduit.
                    conduit = Dispatcher.create_conduit(
                        id = KEY, 
                        name = VALUE.get("name", None),
                        flags = flags,
                        variables = {**VALUE.get("variables", {}), **VALUE.get("pack_data", {}).get("parameters", {})},
                        local_values = payload,
                        global_values = {
                            "guild": guild,
                            "bot": self.bot,
                            "db": self.db,
                            "rest": self.bot.rest,
                            "strings": pack_strings,
                            "interaction": None if event != Events.INTERACTION_CREATE else model.interaction
                        },
                        steps = VALUE.get("steps", []),
                        blocks = blocks,
                        functions = functions
                    )
                    async def run():
                        loop = asyncio.get_event_loop()
                        await loop.create_task(conduit())
                    await asyncio.wait([run()])
        return on_relay_event


    @staticmethod
    def create_conduit(
        *,
        id : str, 
        name : str, 
        flags : List[RelayFlags], 
        variables : Dict[str, Any], 
        local_values : Dict[str, Any],
        global_values : Dict[str, Any],
        steps : List[Dict[str, Any]],
        blocks : List[Any] = [],
        functions : Dict[str, Any] = {}
    ):
        """
        Create a conduit coroutine.
        """
        async def conduit():
            step_limit = \
                None if RelayFlags.PACKAGE in flags else \
                None if RelayFlags.ACTIONS_ACCESS in flags else \
                None
                # TODO: Edit step limits later.
            async def on_job_finish(job : Job, failed_step : Optional[Node] = None):
                t, c, e, w = parse_run(job.id)
                if (t != "PACK"):
                    await sio.emit("relay_actions_log", {
                        "server": global_values["guild"].id, 
                        "workflow": w, 
                        "event": e, 
                        "log": "" if not failed_step else failed_step.action + "\n" + repr(failed_step.return_value),
                        "log_type": "SUCCESS" if job.status else "ERROR"
                    }, namespace = "/admin")
                    # If exception value is empty, log it as Relay exception.
                    if failed_step and failed_step.return_value and (not str(failed_step.return_value).replace("\n", "").strip()):
                        global_values["bot"].dispatch(ExceptionEvent(exception = failed_step.return_value, failed_event = "pyconduit", failed_callback = None))
                if failed_step:
                    print("FAILED_STEP", failed_step, failed_step.return_value)
                # print(str(step.position) + "/" + step.status.name + "/" + step.id, "-", step.block.display_name, "-", step.return_value)
            job = Job(
                id = id,
                name = name,
                variables = variables,
                local_values = local_values,
                global_values = global_values,
                block_limit_overrides = {
                    "DISCORD.MESSAGE_SEND": 5
                },
                on_job_finish = on_job_finish,
                ctx = {
                    "functions": functions
                },
                debug = DEPLOY_TYPE == "LOCAL"
                # TODO: Implement custom blocks again.
                # blocks = blocks
                # tags = [x.value for x in flags]
                # step_limit = step_limit,
            )
            job.nodes_from_array(steps)
            # Execute all steps.
            await job.run()
        return conduit
