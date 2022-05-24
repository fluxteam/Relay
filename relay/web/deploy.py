"""
Routes for "Click to Deploy" feature.
"""

from datetime import datetime
from relay.web import bp
from relay.web.helpers import RelayWebException
from sanic import Request
from sanic.response import redirect
from relay.commons import GITHUB_BOT_ID, GITHUB_BOT_SECRET, db
from relay.utils import make_run, parse_blocks_all, send_http
import httpx


@bp.post("/deploy",
    ctx_auth = "PAGE",
    ctx_fetch = "USER",
    ctx_auth_require = False
)
async def make_deploy(request : Request):
    args = request.get_args()
    # Query args
    deploy_url = str(args.get("repo", ""))
    _ref = str(args.get("branch", ""))
    ref_string = "" if not _ref else f"?ref={_ref}"
    # Parse repository string from URL.
    repo = None
    if deploy_url and (deploy_url.startswith("https://github.com/")) and (deploy_url.removeprefix("https://github.com/").count("/") == 1):
        repo = deploy_url.removeprefix("https://github.com/")
    else:
        return redirect("/")
    pack_id = repo.replace("/", "-", 1)
    # Build client.
    auth = httpx.BasicAuth(username = GITHUB_BOT_ID, password = GITHUB_BOT_SECRET)
    client = httpx.AsyncClient(auth = auth, headers = {"Accept": "application/vnd.github.VERSION.raw"}, follow_redirects = True)
    # Get the relay.toml file
    # from root of the repository.
    _, config = await send_http(client, "GET", f"https://api.github.com/repos/{repo}/contents/relay.toml{ref_string}", None, "TOML", None, None)
    if config == None:
        await client.aclose()
        raise RelayWebException(
            message = request.ctx.tr("error.invalid_source.description"),
            status_code = 400,
            title = request.ctx.tr("error.invalid_source.title")
        )
    # Get the blocks.
    block_source = str(config.get('source', 'blocks.json')).removeprefix('/')
    resp, blocks = await send_http(client, "GET", f"https://api.github.com/repos/{repo}/contents/{block_source}{ref_string}", None, "JSON", None, None)
    if not blocks:
        await client.aclose()
        raise RelayWebException(
            message = request.ctx.tr("error.invalid_source.description"),
            status_code = 400,
            title = request.ctx.tr("error.invalid_source.title")
        )
    # Check if repository package already
    # exists by getting blocks hash.
    pack = db("relay", "packages", pack_id).read()
    new_date = str(resp.headers.get("Last-Modified", ""))
    await client.aclose()
    if pack["date"] != new_date:
        print(f"Indexing {repo}...")
        # Parse the blocks to make sure the file is valid.
        actions = parse_blocks_all(blocks)
        # It is meaningless to have a empty package.
        if not actions:
            raise RelayWebException(
                message = request.ctx.tr("error.invalid_source.description"),
                status_code = 400,
                title = request.ctx.tr("error.invalid_source.title")
            )
        user = request.ctx.discord.get("user")
        # Now save as a new package.
        new_pack = {
            "metadata_version": 1,
            "pack": {
                "name": config.get("name", f"{repo}"),
                "title": config.get("title", f"User package by @{user}"),
                "description": config.get("description"),
                "versions": {"default": 1},
                "date": datetime.now().isoformat()
            },
            "blocks": blocks["blocks"]["blocks"],
            "workflows": {
                make_run(x.metadata.type, x.metadata.content, x.metadata.event, x.id) : {
                    "steps": x.blocks
                } for x in actions
            },
            "date": new_date,
            "user": None if not user else user["id"]
        }
        db("relay", "packages", pack_id).write(new_pack, overwrite = True)
    return redirect(f"/packages/{pack_id}")
