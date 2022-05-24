from typing import Dict, List, Tuple
from relay.classes import Events
from relay.enums import RelayUserFlags
from relay.web import bp
from relay.web.helpers import template, RelayWebException, json
from sanic import Request
from relay.commons import BOT_TOKEN, CLIENT_ID, db, get_user_flags
from relay.utils import ActionsData, group_guilds, load_json, make_run, get_avatar_url, get_server_icon_url, parse_blocks_all, parse_run, get_relay_docs_url, send_discord, ListenerData
import httpx
from sanic.response import redirect


@bp.get("/workspaces/<server:int>", 
    ctx_auth = "PAGE", 
    ctx_auth_perm = 1 << 3,
    ctx_fetch = "USER GUILDS GUILD"
)
async def get_blockly(request : Request, server : int):
    args = request.get_args()
    data = request.ctx.discord
    guild = data["guild"]
    user = data["user"]
    # Now, render the template.
    return template(
        "actions_blockly.html",
        200,
        page = "actions_blockly",
        tr = request.ctx.tr,
        no_footer = True,
        no_parent = True,
        no_header = True,
        server_name = guild['name'],
        server_id = guild["id"],
        server_icon = get_server_icon_url(id = guild["id"], avatar_hash = guild["icon"], size = 64),
        user_icon = get_avatar_url(id = user["id"], discriminator = user["discriminator"], avatar_hash = user["avatar"], size = 64),
        user_name = user['username'],
        user_id = str(user["id"]),
        docs_url = get_relay_docs_url(request.ctx.tr.language, "/actions#editor"),
        enable_toast = True,
        enable_animation = bool(args.get("animation", None)),
        endpoint_workspace = f"{request.scheme}://{request.host}/api/workspaces/{server}",
        endpoint_save = f"{request.scheme}://{request.host}/api/workspaces/{server}",
        colors = request.app.ctx.block_color,
        icons = request.app.ctx.block_icon
    )


@bp.get("/workspaces",
    ctx_auth = "PAGE",
    ctx_fetch = "USER GUILDS"
)
async def get_workspaces(request : Request):
    data = request.ctx.discord
    guilds = data["guilds"]
    user = data["user"]
    guilds_id = db("relay", "servers").list_items()
    guilds_items = group_guilds(guilds, guilds_id)
    can_invite = RelayUserFlags.PRIVATE_USE in get_user_flags(user["id"])
    return template(
        "workspaces.html",
        200,
        page = "workspaces",
        tr = request.ctx.tr,
        no_footer = True,
        no_parent = True,
        no_header = True,
        guilds = guilds_items,
        can_invite = can_invite,
        server_icon = lambda x, y : get_server_icon_url(id = x, avatar_hash = y, size = 64)
    )


@bp.get("/api/workspaces/<server:int>", 
    ctx_auth = "API",
    ctx_auth_perm = 1 << 3,
    ctx_fetch = "USER GUILDS GUILD"
)
async def get_blockly_api(request : Request, server : int):
    data = request.ctx.discord
    user = data["user"]
    workspace = db("relay-actions", "workspaces", server).read(projection = ["blockly"])
    user_db = db("relay", "users", user["id"]).read()
    preferences = user_db.get("blockly_preferences") or {}
    # Add tutorial view state.
    viewed_tutorials = user_db.get("viewed_tutorials") or []
    return json({
        "workspace": workspace.get("blockly", {}),
        "backpack": user_db.get("backpack") or [],
        "preferences": preferences,
        "tutorials": viewed_tutorials
    })


@bp.get("/api/workspaces/<server:int>/actions", 
    ctx_auth = "API",
    ctx_auth_perm = 1 << 3,
    ctx_fetch = "GUILDS GUILD"
)
async def get_blockly_source(request : Request, server : int):
    actions = db("relay-actions", server).read(projection = ["steps"])
    return json({x["_id"] : x for x in actions})


@bp.post("/api/workspaces/<server:int>", 
    ctx_auth = "API", 
    ctx_auth_perm = 1 << 3,
    ctx_fetch = "USER GUILDS GUILD"
)
async def post_blockly(request : Request, server : int):
    client = httpx.AsyncClient()
    s, resp = await send_discord(client, "GET", f"/applications/{CLIENT_ID}/guilds/{server}/commands", ("Bot", BOT_TOKEN, ), )
    application_commands = [(x["type"], x["name"], ) for x in ([] if s != 200 else (resp or []))]
    def get_id_from_identity(idt : Tuple):
        for v in resp:
            if (v["type"] == idt[0]) and (v["name"] == idt[1]):
                return v["id"]
    # Load request data.
    user_data = load_json(request.body)
    # TODO: Translate the error.
    if (user_data == None) or \
        (type(user_data.get("workspace", None)) is not dict) or \
        (type(user_data.get("backpack", None)) is not list):
        raise RelayWebException(
            message = "Invalid payload.",
            title = request.ctx.tr("web.oops"),
            status_code = 400
        )
    # Save workspace.
    db("relay-actions", "workspaces", server).write({
        "blockly": user_data["workspace"]
    }, overwrite = True)
    # Backpack data must be saved under user data.
    tutorials = request.app.ctx.block_extra["CHANGELOG"]
    db("relay", "users", request.ctx.discord["user"]["id"]).write({
        "backpack": user_data["backpack"],
        "viewed_tutorials": [x["id"] for x in (tutorials["all"] + tutorials["extra"])]
    })
    actions = parse_blocks_all(user_data["workspace"])
    # Get ID of actions.
    act = [parse_run(x) for x in db("relay-actions", server).list_items()]
    errors = []
    commands : Dict[Tuple[int, str], ActionsData] = {}
    current_commands : List[str] = []
    cur_act = []
    # Get workflows.
    for action in actions:
        if not action.enabled:
            continue
        md : ListenerData = action.metadata
        id = make_run(md.type, md.content, md.event, action.id)
        # Add to current actions list.
        cur_act.append(id)
        # Don't accept remote events.
        if Events.__members__.get(md.event, Events.PACKAGE_INSTALL).is_remote():
            # ...well except Webhooks.
            if (md.type == "ACTIONS") and (md.event == "WEBHOOK"):
                pass
            # and also functions.
            elif (md.type == "ACTIONS") and (md.event == "FUNCTION"):
                pass
            elif not (md.type in ["SLASH", "COMPONENT", "CONTEXT", "MODAL"] and md.event == "NONE"):
                continue
        # If listener is registerable to Discord,
        # save it's payload to commands dictionary.
        if md.definition:
            commands[md.identity] = action
            # A dummy value to check if the command registered already.
            current_commands.append(md.identity)
        else:
            # Write action to database.
            db("relay-actions", server, id).write({
                "steps": action.blocks
            }, overwrite = True)
    commands_same = sorted(current_commands) == sorted(application_commands)
    # Remove all old user actions.
    for t, content, event, workflow in act:
        merge = make_run(t, content, event, workflow)
        if (t != "PACK") and (merge not in cur_act):
            db("relay-actions", server, merge).delete()
    # Check if there are no any new Application Commands listeners.
    if commands_same:
        for identity in current_commands:
            actd = commands.get(identity, None)
            if actd:
                md : ListenerData = actd.metadata
                db("relay-actions", server, make_run(md.type, get_id_from_identity(identity), md.event, actd.id)).write({
                    "steps": actd.blocks
                }, overwrite = True)
    # Register application commands.
    # Application commands returns an ID when they are registered,
    # so we are using it as run ID instead of block ID, so in dispatcher
    # we can check for invoked command ID directly instead of checking the command name.
    elif commands:
        s, resp = await send_discord(
            client, 
            "PUT", 
            f"/applications/{CLIENT_ID}/guilds/{server}/commands", 
            ("Bot", BOT_TOKEN, ),
            data = [x.metadata.definition for x in commands.values()]
        )
        if s != 200:
            errors.append("DISCORD_SAVE_ERROR")
            print(resp)
        else:
            # Now write actions for workflows.
            for i in resp:
                identity = (i["type"], i["name"], )
                actd = commands.get(identity, None)
                if actd:
                    md : ListenerData = actd.metadata
                    id = make_run(md.type, i["id"], md.event, actd.id)
                    # Write action to database.
                    db("relay-actions", server, id).write({
                        "steps": actd.blocks
                    }, overwrite = True)
                    db("relay", "servers", server).write({ "application_commands": {f"{identity[0]}-{identity[1]}": id} })
    await client.aclose()
    return json({
        "title": request.ctx.tr("web.done"), 
        "description": request.ctx.tr("web.done"), 
        "blocks": {x.id : x.blocks for x in actions},
        "errors": errors
    }, status = 200)


@bp.get("/workspaces/settings",
    ctx_auth = "PAGE",
    ctx_fetch = "USER"
)
async def get_settings(request : Request):
    data = request.ctx.discord
    user = data["user"]
    user_settings = db("relay", "users", user["id"]).read(projection = ["blockly_preferences"])
    tmp = template(
        "settings.html",
        200,
        page = "settings",
        tr = request.ctx.tr,
        no_footer = True,
        no_parent = True,
        no_header = True,
        user = user,
        user_icon = get_avatar_url(
            id = user["id"], 
            discriminator = user["discriminator"], 
            avatar_hash = user["avatar"], 
            size = 96
        ),
        settings = request.app.ctx.block_extra["SETTINGS"],
        message = request.cookies.get("settings-form-message", None),
        user_settings = user_settings.get("blockly_preferences", {}) or {}
    )
    del tmp.cookies["settings-form-message"]
    return tmp


@bp.post("/api/workspaces/settings",
    ctx_auth = "API",
    ctx_fetch = "USER"
)
async def post_settings(request : Request):
    data = request.ctx.discord
    settings = load_json(request.body)
    if settings == None:
        raise RelayWebException(
            message = "Invalid payload.",
            title = request.ctx.tr("web.oops"),
            status_code = 400
        )
    db("relay", "users", data["user"]["id"]).write({"blockly_preferences": settings})
    return json({
        "title": request.ctx.tr("web.done")
    })


@bp.post("/workspaces/settings",
    ctx_auth = "PAGE",
    ctx_fetch = "USER"
)
async def post_settings_form(request : Request):
    data = request.ctx.discord
    settings = {}
    for v in request.app.ctx.block_extra["SETTINGS"]:
        for item in v["items"]:
            if item["type"] == "BOOLEAN":
                settings[item["id"]] = request.form.get(item["id"], "off") == "on"
            elif item["type"] == "OPTION":
                settings[item["id"]] = request.form.get(item["id"], item["default"])
    db("relay", "users", data["user"]["id"]).write({"blockly_preferences": settings})
    resp = redirect("/workspaces/settings")
    resp.cookies["settings-form-message"] = request.ctx.tr("web.settings_saved")
    resp.cookies["settings-form-message"]["max-age"] = 5
    return resp