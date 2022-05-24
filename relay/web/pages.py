from relay.utils import get_relay_docs_url
from relay.web import bp
from relay.web.helpers import RelayWebException, template
from sanic import Request
from sanic.response import redirect, text
import orjson


@bp.get("/")
async def home(request : Request):
    return redirect("/workspaces")


@bp.get("/docs")
async def docs(request : Request):
    return redirect(get_relay_docs_url(request.ctx.tr.language))


@bp.get("/docs/<page:path>")
async def docs_path(request : Request, page : str):
    return redirect(get_relay_docs_url(request.ctx.tr.language, "/" + page.removeprefix("/")))


@bp.get("/invite-beta")
async def invite_relay(request : Request):
    args = request.get_args()
    guild_id = args.get("guild_id", None)
    return redirect(
        "https://discord.com/api/oauth2/authorize" + \
        "?client_id=814082318842068993&permissions=1266441252087&scope=bot%20applications.commands" + \
        ("" if not guild_id else f"&guild_id={guild_id}&disable_guild_select=true")
    )


@bp.get("/pages/success")
async def success(request : Request):
    raise RelayWebException(
        message = request.ctx.tr("web.completed"),
        status_code = 200,
        title = request.ctx.tr("web.done"),
        icon = "check"
    )


@bp.get("/strings.js")
async def get_strings(request : Request):
    strings = orjson.dumps(request.ctx.tr.strings).decode("utf-8")
    return text("export const _ = " + strings, content_type = "text/javascript")


@bp.get("/blockly.js")
async def get_blockly_data(request : Request):
    data = {
        "docs_url": get_relay_docs_url()[:-1],
        "blocks": request.app.ctx.blocks,
        "toolbox": {"kind": "categoryToolbox", "contents": request.app.ctx.block_toolbox},
        "theme": request.app.ctx.block_theme,
        "block_names": request.app.ctx.block_names,
        "extra": request.app.ctx.block_extra,
    }
    return text("export const _ = " + orjson.dumps(data).decode("utf-8"), content_type = "text/javascript")