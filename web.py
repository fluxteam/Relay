from sanic import Sanic, Request
from sanic.exceptions import SanicException
from jinja2 import Environment, PackageLoader
from relay.web import bp, sio
from relay.package import RelayPackageManager
from relay.utils import get_relay_docs_url

# Load custom pyconduit blocks
from relay.actions import *
from relay.web.helpers import template
from relay.commons import translation
from sanic.helpers import STATUS_CODES
from relay.blockly import load as install_blockly

# Jinja2
env = Environment(
    loader = PackageLoader("relay.web", "pages"),
    autoescape = True,
    lstrip_blocks = True,
    trim_blocks = True
)

# Sanic
app = Sanic("relay")
app.websocket_enabled = True
app.static("/assets", "./relay/web/assets")
app.static("/assets/blockly", "./relay/web/blockly", content_type = "text/javascript")


@app.exception(SanicException)
async def error_handle(request : Request, exception : SanicException):
    tr = request.ctx.__dict__.get("tr", translation["en"])
    return template(
        "info.html", exception.status_code,
        title = exception.status_code,
        description = exception.message or STATUS_CODES.get(exception.status_code, b"").decode("utf-8"),
        icon = "flag",
        tr = tr,
        docs = lambda x = None, y = None: get_relay_docs_url(language = y or tr.language, page = x),
        no_footer = True
    )


@app.after_server_start
async def sync_packs(app : Sanic, loop):
    # Sync marketplace.
    await RelayPackageManager.market.sync()
    # Fetch all Blockly blocks.
    theme, categories, block_names, blocks, extra_state, colors, icons = install_blockly()
    app.ctx.block_theme = theme
    app.ctx.block_toolbox = [x for x in categories.values()]
    app.ctx.block_names = block_names
    app.ctx.block_extra = extra_state
    app.ctx.block_color = colors
    app.ctx.block_icon = icons
    app.ctx.blocks = []
    for v in blocks.values():
        app.ctx.blocks.extend(v)


# Add Jinja environment to the application context.
app.ctx.jinja = env

# Actions log.
app.ctx.actions_logs = {}

app.config.FALLBACK_ERROR_FORMAT = "json"

# Register blueprint.
app.blueprint(bp)

# Register socket.io
sio.attach(app)