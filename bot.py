from hikari import (
    GatewayBot, 
    Intents,
    ShardPayloadEvent,
    ExceptionEvent,
    Embed,
    Bytes
)
from hikari.errors import HikariError
from hikari.events.lifetime_events import StartedEvent
from relay.listeners import Event
from relay.dispatcher import Dispatcher
from relay.commons import DEPLOY_TYPE, OWNER_ID, db, translation, snowflaked, marketplace, sio, BASE_URL, BOT_TOKEN, CLIENT_ID
from relay.utils import exception_hash
from relay.classes import Events, RelayBot
from socketio.exceptions import SocketIOError
import relay.actions
from datetime import datetime, timezone, timedelta
import os
import io
import textwrap
import json
import traceback
import asyncio
import orjson

if os.name != "nt":
    import uvloop
    uvloop.install()


bot = RelayBot(
    token = BOT_TOKEN,
    intents = \
        Intents.GUILDS |
        Intents.GUILD_MEMBERS |
        Intents.GUILD_BANS |
        Intents.GUILD_EMOJIS |
        Intents.GUILD_INVITES |
        Intents.GUILD_VOICE_STATES |
        Intents.GUILD_MESSAGES |
        Intents.GUILD_MESSAGE_REACTIONS
)

async def socket_reconnect():
    await sio.connect(BASE_URL, auth = {"username": "Bot", "password": BOT_TOKEN}, namespaces = ["/admin", "/"], wait_timeout = 10)


@sio.on("relay_transport", namespace = "/admin")
async def relay_transport(data : dict):
    print(f"-- Connected to Relay Remote Socket.")


@sio.on("relay_remote", namespace = "/admin")
def relay_remote(data : dict):
    event = data["event"]
    payload = {}
    payload.update(data)
    # Inner payload comes as string JSON because of socket.io doesn't accept all JSON types,
    # so we return JSON string in server-side.
    if "data" in payload:
        payload["data"] = orjson.loads(payload["data"])
    if event in [Events.PACKAGE_INSTALL.value, Events.WEBHOOK.value]:
        print(f"-- Received event {event} from server-side events.")
        bot.dispatch(ShardPayloadEvent(name = event, app = bot, shard = bot._get_shard(payload['guild_id']), payload = payload))


@bot.listen()
async def started(event : StartedEvent):
    print("-- Deploy type:", DEPLOY_TYPE)
    if DEPLOY_TYPE != "LOCAL":
        print("-- Waiting 60 seconds before connection to Realtime events.")
        await asyncio.sleep(60)
    await sio.connect(BASE_URL, auth = {"username": "Bot", "password": BOT_TOKEN}, namespaces = ["/admin", "/"], wait_timeout = 10)
    await marketplace.sync()

async def _eval(event, code : str, message_id : int, channel_id : int, guild_id : int, user_id : int, model):
    """
    Eval code.
    """
    f = ""
    if code.startswith("```") and code.endswith("```"):
        f = os.linesep.join(code.splitlines()[1:-1])
    elif code.startswith("`") and code.endswith("`"):
        f = code[1:-1]
    elif not code.strip():
        f = "return None"
    else:
        f = "print(" + code + ")"
    # Method
    execute = f'async def func():\n{textwrap.indent(f, "  ")}'
    print_io = io.StringIO()
    async def upload(data):
        file = None
        if isinstance(data, dict):
            file = Bytes(orjson.dumps(data), "file.json")
        elif isinstance(data, str):
            file = Bytes(data.encode("utf-8"), "file.txt")
        await bot.rest.create_message(855080802207137802, attachment = file)
    # env
    env = {
        "bot": bot,
        "guild": bot.cache.get_guild(guild_id),
        "channel": bot.cache.get_guild_channel(channel_id),
        "message": bot.cache.get_message(message_id),
        "member": bot.cache.get_member(guild_id, user_id),
        "model": model,
        "os": os,
        "event": event,
        "db": db,
        "translation": translation,
        "upload": upload,
        "dump": lambda text: json.dumps(text, indent = 4, ensure_ascii = False),
        "print": lambda text, *args, **kwargs: print(*[text, *args], sep = kwargs.get("sep"), end = kwargs.get("end", "\n"), file = print_io),
    }
    env.update(globals())
    # Compile the method
    try:
        exec(execute, env)
    except Exception as e:
        await bot.rest.create_message(channel = channel_id, content = f'```py\n{os.linesep.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))}\n```')
        return
    # Variables
    method_result = None
    # Get the method itself for executing.
    try:
        method_result = await env['func']()
    except Exception as e:
        print_io.seek(0)
        print_result = print_io.read()
        if print_result:
            await bot.rest.create_message(channel = channel_id, content = ("```py\n" + print_result[:1950] + "\n ...```") if len(print_result) > 1950 else print_result)
        await bot.rest.create_message(channel = channel_id, content = f'```py\n{os.linesep.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))}\n```')  
    else:
        print_io.seek(0)
        print_result = print_io.read()
        # Send output.
        if (method_result == None) and (print_result == ""):
            await bot.rest.create_message(channel = channel_id, content = "> empty")
        else:
            await bot.rest.create_message(channel = channel_id, content = f"**return_value**\n`{type(method_result).__name__}`\n```py\n{method_result if not isinstance(method_result, dict) else env['dump'](method_result)}\n```")
            print_result = print_result[:1950] + "\n ..." if len(print_result) > 1950 else print_result
            await bot.rest.create_message(channel = channel_id, content = f"**output**\n```py\n{None if not print_result else print_result}\n```")


@bot.listen()
async def exception_handler(event: ExceptionEvent):
    if DEPLOY_TYPE == "LOCAL":
        full_trace = traceback.format_exception(etype=type(event.exception), value=event.exception, tb=event.exception.__traceback__)
        print("\n".join(full_trace))
        return
    s = snowflaked()
    exc = event.exception
    type_ = \
        "socket" if isinstance(exc, SocketIOError) else \
        "conduit" if event.failed_event == "pyconduit" else \
        "api" if isinstance(exc, HikariError) else \
        "bot"
    # Create GitHub Issues for new created exception.
    full_trace = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
    if (type_ == "bot") and sio.connected:
        await sio.emit("relay_exception", data = {
            "hash": exception_hash(exc),
            "type": exc.__class__.__name__,
            "log": "".join(full_trace)
        }, namespace = "/admin")
    else:
        if not isinstance(exc, ConnectionError):
            db("relay", "errors", f"{type_}-{str(s)}").write({
                "snowflake": str(s),
                "timestamp": datetime.fromtimestamp(s.timestamp, timezone(timedelta(hours = 3))),
                "type": exc.__class__.__name__,
                "log": full_trace
            })

@bot.listen()
async def listener(event: ShardPayloadEvent):
    # Get event enum.
    exists, ev, m = Event.get(event.name)
    if not exists:
        return
    payload = dict(event.payload)
    model = None if "guild_id" not in payload else m.from_payload(bot = bot, payload = payload)
    # Relay ignores events that triggered by itself.
    if model == None:
        return
    # print("Received", ev)
    # print("Payload", model.from_payload(bot = bot, payload = payload))
    # Copy payload.
    if (ev == ev.MESSAGE_SEND) and payload["content"].startswith("p.eval ") and (str(model.message.author.id) == str(OWNER_ID)):
        await _eval(
            event = event, 
            code = payload["content"].removeprefix("p.eval "), 
            channel_id = payload["channel_id"], 
            guild_id = payload["guild_id"],
            message_id = payload["id"],
            user_id = payload["author"]["id"],
            model = model
        )
    else:
        await dispatcher.create_relay_event()(
            event = ev,
            guild_id = model.guild_id,
            user_id = model.event_author(),
            payload = model.to_dict(),
            model = model
        )

dispatcher = Dispatcher(db, bot, CLIENT_ID)

bot.run()