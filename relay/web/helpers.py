import orjson
from typing import Any, Optional, Dict, Tuple
from sanic.helpers import STATUS_CODES
from sanic import Sanic, HTTPResponse
from sanic.response import text, html
from relay.enums import RealtimeEvent
from relay.web import sio


class RelayWebException(Exception):
    def __init__(self, message : str, status_code : int, title : str = None, icon : str = None, secure : bool = False):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.secure = secure
        self.title = title or STATUS_CODES.get(status_code, b"Error").decode()
        self.icon = icon or "octagon"
        self.secure = secure


# A method that reads a template and renders with Jinja2.
def template(tpl, _status = 200, **kwargs):
    templ = Sanic.get_app("relay").ctx.jinja.get_template(tpl)
    if tpl.endswith(".js"):
        return text(templ.render(kwargs), status = _status, content_type = "text/javascript; charset=utf-8")
    elif tpl.endswith(".css"):
        return text(templ.render(kwargs), status = _status, content_type = "text/css; charset=utf-8")
    return html(templ.render(kwargs), status = _status)


def json(
    body: Any,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "application/json",
    **kwargs
):
    """
    Returns JSON response, but uses orjson instead.
    """
    return HTTPResponse(
        orjson.dumps(body, **kwargs),
        headers=headers,
        status=status,
        content_type=content_type,
    )


async def fetch_users(room : str) -> Tuple[str, Dict]:
    """
    Fetches the currently connected users in a room.
    """
    users = {}
    first_sid = ""
    # Get list of connected user names.
    for x, y in sio.manager.get_participants("/user", room):
        user = (await sio.get_session(x, namespace = "/user"))["user"]
        if not first_sid:
            first_sid = x
        users[x] = {
            "id": user["id"],
            "username": user["username"],
            "tag": user["discriminator"],
            "avatar_hash": user["avatar"]
        }
    return first_sid, users,


async def send_error(sid : str, message : str, disconnect : bool = False) -> None:
    """
    Sends an error payload to specified client.
    Also, the client can be optionally disconnected after error.
    """
    await sio.emit(
        "relay_workspace", 
        to = sid, 
        namespace = "/user", 
        data = payload(RealtimeEvent.ERROR, message = message)
    )
    if disconnect:
        await sio.disconnect(sid, namespace = "/user")


def payload(_event : RealtimeEvent, **kwargs):
    """
    A shortcut method to build payload dictionary.
    """
    return {"type": _event.value, **kwargs}