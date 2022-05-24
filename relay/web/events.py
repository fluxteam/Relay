import orjson
from relay.web import sio, bp
from relay.commons import BOT_TOKEN, db, GITHUB_BOT_ID, GITHUB_BOT_SECRET, REPORTS_GET, REPORTS_POST, get_server_flags, get_user_flags, translation
from relay.web.helpers import RelayWebException, json, payload, send_error, fetch_users
from sanic import Request
from sanic.response import redirect
from relay.classes import Events
from relay.auth import decrypt_token, oauth_url
from relay.enums import RealtimeEvent, RelayFlags, RelayUserFlags
from relay.utils import load_json, make_run, parse_language_header, send_discord
from socketio.exceptions import ConnectionRefusedError
import httpx
import markupsafe


@sio.event(namespace = "/admin")
async def connect(sid, environ, auth : dict):
    # Check for authentication.
    if auth and (auth == {"username": "Bot", "password": BOT_TOKEN}):
        await sio.emit('relay_transport', data = {}, namespace = "/admin")
    else:
        raise ConnectionRefusedError('Authentication failed.')


@sio.event(namespace = "/user")
async def connect(sid, environ):
    request = environ["sanic.request"]
    request.ctx.languages = parse_language_header(request.headers.get("Accept-Language", "en"))
    request.ctx.tr = translation[request.ctx.languages[0][0]]
    token = decrypt_token(request.cookies.get("access_token"))
    client = httpx.AsyncClient()
    s1, r1 = await send_discord(client, "GET", "/users/@me", ("Bearer", token), )
    s2, r2 = await send_discord(client, "GET", "/users/@me/guilds", ("Bearer", token), )
    await client.aclose()
    if ((s1 != 200) or (s2 != 200)):
        raise ConnectionRefusedError('Authentication failed. Are you sure that you logged with your Discord account?')
    await sio.save_session(sid, {
        "user": r1,
        "guilds": {str(x["id"]) : x for x in r2},
        "token": token,
        "locale": request.ctx.tr.language
    }, namespace = "/user")


@sio.on("relay_workspace_init", namespace = "/user")
async def relay_workspace_init(sid, data : dict):
    async with sio.session(sid, namespace = "/user") as session:
        # Is payload contains a "server" key?
        # Also check if user is in the server.
        server = data.get("server", None)
        if (not server) or (server not in session["guilds"]):
            await send_error(sid, "Invalid server.")
            return
        if not (int(session["guilds"][server]["permissions"]) & 1 << 3):
            await send_error(sid, "Insufficient permissions.", disconnect = True)
            return
        client = httpx.AsyncClient()
        # Check if Relay is in the server, because it would be nonsense to use Relay's dashboard if it is not in the server.
        # We don't care the response, as basic guild information already comes with /users/@me/guilds endpoint.
        s1, r1 = await send_discord(client, "GET", "/guilds/" + server, ("Bot", BOT_TOKEN), )
        await client.aclose()
        if (s1 != 200):
            await send_error(sid, "Insufficient permissions.", disconnect = True)
            return
        # If everything goes well, assign the client to a room - so when client sends a payload,
        # only clients that connected to the same room will receive the payload.
        room = f"room-{server}"
        session["room"] = room
        sio.enter_room(sid, room, namespace = "/user")
        first_sid, users = await fetch_users(room)
        # If fetching blocks has failed from /api/workspaces endpoint, 
        # return blocks over socket for fallback.
        # TODO: Remove this fallback ASAP.
        if data.get("pull_blocks"):
            user_db = db("relay", "users", session["user"]["id"]).read()
            tr = translation[session["locale"]]
            # Add tutorial view state.
            viewed_tutorials = user_db.get("viewed_tutorials") or []
            await sio.emit("relay_workspace", data = payload(
                RealtimeEvent.INIT, 
                workspace = db("relay-actions", "workspaces", server).read(projection = ["blockly"]).get("blockly", {}),
                preferences = user_db.get("blockly_preferences") or {},
                backpack = user_db.get("backpack") or [],
                tutorials = viewed_tutorials
            ), to = sid, namespace = "/user")
        else:
            await sio.emit("relay_workspace", data = payload(RealtimeEvent.INIT), to = sid, namespace = "/user")
        await sio.emit("relay_workspace", data = payload(RealtimeEvent.USER_REFRESH, users = users), to = room, namespace = "/user")
        if first_sid:
            # The first connected user has the latest changes, so we want them to sync (share) their
            # blocks with other users. So, new connected users can see the first user's own unsaved changes too.
            await sio.emit("relay_workspace", data = payload(RealtimeEvent.NEED_SYNC), to = first_sid, namespace = "/user")


@sio.on("relay_workspace_push", namespace = "/user")
async def relay_workspace_push(sid, data : dict):
    # TODO: Delete repeated code and merge events in single event.
    session = await sio.get_session(sid, namespace = "/user")
    # Get the payload from client, and send to other connected clients,
    # except of the sender itself, of course.
    if "room" not in session:
        await send_error(sid, "Room has not created yet.")
        return
    await sio.emit(
        "relay_workspace", 
        data = payload(RealtimeEvent.PAYLOAD, data = data), 
        to = session["room"], 
        skip_sid = sid, 
        namespace = "/user"
    )


@sio.on("relay_workspace_sync", namespace = "/user")
async def relay_workspace_sync(sid, data : dict):
    session = await sio.get_session(sid, namespace = "/user")
    if "room" not in session:
        await send_error(sid, "Room has not created yet.")
        return
    await sio.emit(
        "relay_workspace", 
        data = payload(RealtimeEvent.LOAD_BLOCKS, data = data), 
        to = session["room"], 
        skip_sid = sid, 
        namespace = "/user"
    )


@sio.event(namespace = "/user")
async def disconnect(sid):
    session = await sio.get_session(sid, namespace = "/user")
    if "room" not in session:
        return
    room = session["room"]
    _, users = await fetch_users(room)
    await sio.emit("relay_workspace", data = payload(RealtimeEvent.USER_REFRESH, users = users), to = room, skip_sid = sid, namespace = "/user")


@sio.on("relay_actions_log", namespace = "/admin")
async def store_actions_log(sid, data : dict):
    await sio.emit(
        "relay_workspace", 
        data = payload(RealtimeEvent.WORKFLOW_LOG, 
            log = data["log"], 
            workflow = data["workflow"], 
            event = data["event"], 
            log_type = data["log_type"]
        ),
        to = f"room-{data['server']}",
        namespace = "/user"
    )


@sio.on("relay_exception", namespace = "/admin")
async def send_exception(sid, data : dict):
    auth = httpx.BasicAuth(username = GITHUB_BOT_ID, password = GITHUB_BOT_SECRET)
    # Create new client for sending GitHub requests.
    async with httpx.AsyncClient(
        trust_env = False, 
        auth = auth, 
        headers = {"Accept": "application/vnd.github.v3+json"},
        max_redirects = 3
    ) as client:
        resp1 = await client.get(REPORTS_GET(data["hash"]))
        # Fetch issues.
        issues = load_json(await resp1.aread(), {"items": []})
        # Check if has issues.
        if resp1.status_code != 200:
            print(load_json(await resp1.aread(), {}))
        if ("items" not in issues) or (issues["items"]):
            print("-- Looks like issue has already created, skipping...", data["hash"])
            return
        # Create issue then.
        resp2 = await client.post(REPORTS_POST, json = {
            "title": "[CRASH] [" + data["hash"] + "]",
            "body": \
                "<pre>\n" + data["log"] + "</pre>",
            "assignees": ["ysfchn"]
        })
        if resp2.status_code != 200:
            print(load_json(await resp2.aread(), {}))


@bp.post("/hooks/<server:int>/<webhook:str>")
async def post_webhook(request : Request, server : int, webhook : str):
    is_valid = db("relay-actions", server, make_run("ACTIONS", None, "WEBHOOK", webhook)).exists
    if not is_valid:
        return json({"message": "Invalid webhook."}, status = 404)
    else:
        await sio.emit(
            "relay_remote",
            data = {
                "event": Events.WEBHOOK.value,
                "guild_id": str(server),
                "action_id": webhook,
                "data": orjson.dumps(load_json(request.body)).decode("utf-8")
            },
            namespace = "/admin"
        )
        return json({"message": "Done!"}, status = 200)