from relay.web import bp, sio
from relay.web.helpers import template, RelayWebException, json
from sanic import Request
from relay.commons import db
from relay.package import RelayPackageManager
from relay.utils import group_guilds, load_json, pack_report_url, split_type_value, parse_form_data, get_avatar_url, get_server_icon_url, get_relay_docs_url
from relay.classes import Events
from relay_packages.classes import Empty, ParameterType
from urllib.parse import urlunparse
import orjson


@bp.get("/packages/<server:int>/<pack_code:str>", 
    ctx_auth = "PAGE",
    ctx_auth_perm = 1 << 5,
    ctx_fetch = "USER GUILDS GUILD CHANNELS"
)
async def get_pack(request : Request, server : int, pack_code : str):
    discord = request.ctx.discord
    guild = discord["guild"]
    user = discord["user"]
    channels = discord["channels"]
    # Get manager.
    manager = RelayPackageManager(server)
    manager.fetch()
    # Check if package is valid.
    pack = manager.get_or_fetch(pack_code)
    if pack == None:
        raise RelayWebException(
            message = request.ctx.tr("error.package_not_found.description", pack_code),
            status_code = 404,
            title = request.ctx.tr("error.package_not_found.title")
        )
    # Create async client.
    pack_author = pack.package.author()
    # Get the package translation.
    pack_translation = pack.package.get_localized(request.ctx.tr.language)
    # Get text and voice channels.
    # https://discord.com/developers/docs/resources/channel#channel-object-channel-types
    text_channels = {}
    voice_channels = {}
    roles = {x["name"] : x["id"] for x in guild["roles"] if not x["managed"]}
    for k in channels:
        # Text channels.
        if k["type"] == 0:
            text_channels[k["name"]] = k["id"]
        # Voice channels.
        elif k["type"] == 2:
            voice_channels[k["name"]] = k["id"]
    # Now, render the template.
    return template(
        'package.html',
        200,
        page = "package",
        pack_icon = manager.market.URL + pack.package.pack_icon,
        pack_name = pack_translation.name,
        pack_title = pack_translation.title,
        pack_description = pack_translation.description,
        pack_verified = pack.package.verified,
        pack_author = pack_author.name,
        pack_author_verified = pack_author.verified,
        pack_version = pack.archive.id,
        pack_repo = pack.package.source.service,
        pack_date = None if not pack.package.date else pack.package.date.isoformat(" ").split(" ")[0],
        pack_size = len(orjson.dumps(pack.archive.to_dict(), default = lambda x: None)),
        pack_source = pack.package.source_url(),
        pack_report = pack_report_url(request.ctx.tr, pack.package.id, pack.version),
        is_installed = pack.is_installed,
        server_name = guild['name'],
        server_icon = get_server_icon_url(id = guild["id"], avatar_hash = guild["icon"], size = 64),
        user_icon = get_avatar_url(id = user["id"], discriminator = user["discriminator"], avatar_hash = user["avatar"], size = 64),
        refresh_url = urlunparse((request.scheme, request.host, request.path, None, 'oauth=1', None, )),
        user_name = user['username'],
        user_discriminator = user['discriminator'],
        docs = lambda x = None, y = None: get_relay_docs_url(language = y or request.ctx.tr.language, page = x),
        parameters = pack.archive.parameters,
        post_url = f"{request.scheme}://{request.host}/api/packages/{server}/{pack_code}",
        success_url = f"{request.scheme}://{request.host}/pages/success",
        split_type_value = split_type_value,
        get_input = lambda x:
            "any" if x == ParameterType.ANY else \
            "string" if x == ParameterType.STRING else \
            "number" if x == ParameterType.NUMBER else \
            "choice" if x in [ParameterType.CHOICE, ParameterType.ROLE, ParameterType.TCHANNEL, ParameterType.VCHANNEL] else \
            "boolean" if x == ParameterType.BOOLEAN else \
            "snowflake" if x in [ParameterType.USER, ParameterType.SNOWFLAKE] else \
            "",
        get_input_type = lambda x:
            "mapping" if isinstance(x, dict) else \
            "list" if isinstance(x, list) else \
            "string" if isinstance(x, str) else \
            "boolean" if isinstance(x, bool) else \
            "number" if isinstance(x, (int, float)) else \
            "none",
        get_options = lambda x, y:
            roles if x == ParameterType.ROLE else \
            text_channels if x == ParameterType.TCHANNEL else \
            voice_channels if x == ParameterType.VCHANNEL else \
            y if x == ParameterType.CHOICE else \
            {},
        get_default = lambda x, y:
            {"": None} if x == "mapping" and (not isinstance(y, dict)) else \
            [None] if x == "list" and (not isinstance(y, list)) else y,
        get_name = lambda x:
            None if x == ParameterType.ANY else \
            request.ctx.tr("common.string") if x == ParameterType.STRING else \
            request.ctx.tr("common.number") if x == ParameterType.NUMBER else \
            request.ctx.tr("common.choice") if x == ParameterType.CHOICE else \
            request.ctx.tr("common.none") if x == ParameterType.BOOLEAN else \
            request.ctx.tr("common.role") if x == ParameterType.ROLE else \
            request.ctx.tr("common.channel") if x in [ParameterType.TCHANNEL, ParameterType.VCHANNEL] else \
            "ID" if x in [ParameterType.USER, ParameterType.SNOWFLAKE] else \
            "",
        tr = request.ctx.tr,
        ParameterType = ParameterType,
        Empty = Empty
    )


@bp.post("/api/packages/<server:int>/<pack_code:str>", 
    ctx_auth = "API", 
    ctx_auth_perm = 1 << 5,
    ctx_fetch = "USER GUILDS GUILD"
)
async def post_pack(request : Request, server : int, pack_code : str):
    discord = request.ctx.discord
    user = discord["user"]
    # Get manager.
    manager = RelayPackageManager(server)
    # Check if package is valid.
    pack = manager.get_or_fetch(pack_code, include_user = True)
    if pack == None:
        raise RelayWebException(
            message = request.ctx.tr("error.package_not_found.description", pack_code),
            status_code = 404,
            title = request.ctx.tr("error.package_not_found.title")
        )
    # If everything is okay,
    # install the package.
    user_data = load_json(request.body, {})
    # Parse parameters.
    success, parsed = parse_form_data(user_data, pack.archive.parameters)
    errors = []
    # If parameters are not correct,
    # Convert error codes to their translations.
    if not success:
        errors = [request.ctx.tr("web." + y, "'" + x + "'") for x, y in parsed.items()]
        return json({"title": request.ctx.tr("web.something_wrong"), "description": errors}, status = 400)
    else:
        manager.fetch()
        if pack_code not in manager.packages:
            print("User data:", user_data)
            print("Pack:", pack_code)
            manager.install(pack_code, user_data)
            # Add installation information to the queue,
            # so Relay can receive that data from /packages/events endpoint
            # and execute post installation commands.
            # Don't add to queue if package doesn't contain setup workflows.
            if pack.archive.install_workflow:
                await sio.emit(
                    "relay_remote",
                    data = {
                        "event": Events.PACKAGE_INSTALL.value,
                        "guild_id": str(server),
                        "pack_code": pack_code,
                        "pack_version": pack.version,
                        "user_id": str(user["id"]),
                        "data": orjson.dumps(user_data).decode("utf-8")
                    },
                    namespace = "/admin"
                )
            return json({"title": request.ctx.tr("web.done"), "description": request.ctx.tr("web.completed")}, status = 200)
        return json({"title": request.ctx.tr("web.oops"), "description": request.ctx.tr("web.package_installed_already")}, status = 400)


@bp.get("/packages/<pack_code:str>", 
    ctx_auth = "PAGE", 
    ctx_fetch = "USER GUILDS",
    ctx_auth_require = False
)
async def get_pack_overview(request : Request, pack_code : str):
    discord = request.ctx.discord
    guilds = discord.get("guilds")
    user = discord.get("user")
    # Get manager.
    manager = RelayPackageManager()
    # Check if package is valid.
    pack = manager.get_or_fetch(pack_code, include_user = True)
    if pack == None:
        raise RelayWebException(
            message = request.ctx.tr("error.package_not_found.description", pack_code),
            status_code = 404,
            title = request.ctx.tr("error.package_not_found.title")
        )
    # Create async client.
    pack_author = pack.package.author()
    # Get the package translation.
    pack_translation = pack.package.get_localized(request.ctx.tr.language)
    guilds_id = db("relay", "servers").list_items()
    guilds_items = group_guilds(guilds or {}, guilds_id)
    # Now, render the template.
    return template(
        'package.html',
        200,
        page = "package",
        overview = True,
        pack_icon = manager.market.URL + pack.package.pack_icon,
        pack_name = pack_translation.name,
        pack_title = pack_translation.title,
        pack_description = pack_translation.description,
        pack_verified = pack.package.verified,
        pack_author = \
            pack_author.name if not pack.is_user_package else
            pack.package.source.name.split("-", 1)[0],
        pack_author_image = \
            (pack_author.links.get("github", "/assets/static/user").removesuffix("/") + ".png") if not pack.is_user_package else
            "https://github.com/" + pack.package.source.name.split("-", 1)[0] + ".png",
        pack_author_verified = pack_author.verified,
        pack_author_link = \
            (pack_author.links.get("github", "").removesuffix("/")) if not pack.is_user_package else
            "https://github.com/" + pack.package.source.name.split("-", 1)[0],
        pack_version = pack.archive.id,
        pack_repo = pack.package.source.service,
        pack_service = \
            "fluxteam-relay-packages" if not pack.is_user_package else
            pack.package.source.name,
        pack_date = None if not pack.package.date else pack.package.date.isoformat(" ").split(" ")[0],
        pack_size = len(orjson.dumps(pack.archive.to_dict(), default = lambda x: None)),
        pack_source = pack.package.source_url(),
        pack_report = f"https://github.com/fluxteam/IssueTracker/issues/new?title=[Relay%20Packages]%20Report%20Package:%20{pack.package.id}",
        is_installed = pack.is_installed,
        user_icon = None if not user else get_avatar_url(id = user["id"], discriminator = user["discriminator"], avatar_hash = user["avatar"], size = 64),
        refresh_url = urlunparse((request.scheme, request.host, request.path, None, 'oauth=1', None, )),
        user_name = None if not user else user['username'],
        user_discriminator = None if not user else user['discriminator'],
        docs = lambda x = None, y = None: get_relay_docs_url(language = y or request.ctx.tr.language, page = x),
        parameters = {},
        guilds = guilds_items,
        has_parameters = bool(pack.archive.parameters),
        post_url = f"{request.scheme}://{request.host}/api/packages/{'{}'}/{pack_code}",
        install_url = f"{request.scheme}://{request.host}/packages/{'{}'}/{pack_code}",
        success_url = f"{request.scheme}://{request.host}/pages/success",
        tr = request.ctx.tr
    )