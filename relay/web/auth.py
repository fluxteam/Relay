from typing import List, Optional
from relay.web import bp
from sanic import Request
from sanic.response import redirect, html, empty
from relay.auth import decrypt_token, parse_state, encrypt_token, oauth_url
from relay.enums import AuthCode, RelayFlags
from relay.utils import get_relay_docs_url, load_json, parse_language_header, send_discord
import httpx, time, datetime
from relay.commons import get_server_flags, translation, BOT_TOKEN, CLIENT_ID, CLIENT_SECRET
from relay.web.helpers import RelayWebException, json, template

@bp.exception(RelayWebException)
async def print_error(request : Request, exception : RelayWebException):
    auth_mode = request.route.ctx.__dict__.get("auth", None)
    if auth_mode == "API":
        return json({"title": exception.title, "description": exception.message}, status = exception.status_code)
    return template(
        "info.html", exception.status_code, 
        title = exception.title, 
        description = exception.message,
        icon = exception.icon,
        secure = exception.secure,
        tr = request.ctx.tr,
        docs = lambda x = None, y = None: get_relay_docs_url(language = y or request.ctx.tr.language, page = x),
        no_footer = True
    )


@bp.on_request
async def before_request(request : Request):
    ctx = request.route.ctx.__dict__
    # If request comes from Discord Embed bot, return embed preview instead of running route handler.
    if "Discordbot/2.0" in request.headers.get("user-agent", ""):
        embed_prop = ctx.get("embed", "")
        embed_mode = ctx.get("embed_mode", "") or "DEFAULT"
        if embed_prop:
            return html(embed_prop.replace("{0}", request.url))
        else:
            # If embed mode is "PASS", execute route handler normally.
            if embed_mode == "PASS":
                return
            return empty()
    request.ctx.callback_url = request.scheme + "://" + request.host + "/authorize"
    # If Relay is hosted on a server such as Heroku, X-Forwarded-For will point to
    # user's IP address, but if it is started locally, then just get the IP.
    request.ctx.id = request.headers.get("x-forwarded-for", request.ip)
    request.ctx.languages = parse_language_header(request.headers.get("Accept-Language", "en"))
    request.ctx.tr = translation[request.ctx.languages[0][0]]
    # Override language.
    custom_lan = request.get_args().get("language")
    if custom_lan != None:
        request.ctx.tr = translation[custom_lan]
    # Check if route requires authentication.
    auth_mode : Optional[str] = ctx.get("auth") or None
    auth_require : Optional[bool] = False if not auth_mode else bool(ctx.get("auth_require", True))
    auth_permission : Optional[int] = ctx.get("auth_perm") or None
    fetch_routes: List[str] = ctx.get("fetch", "").split(" ")
    if auth_mode:
        request.ctx.token = decrypt_token(request.cookies.get("access_token"))
        if auth_mode == "API":
            # Use custom authorization if Authorization has provided for API. 
            if request.headers.get("Authorization", None):
                request.ctx.token = request.headers["Authorization"]
        else:
            # Unsupported browser check.
            user_agent = request.headers.get("User-Agent", "")
            if any([x in user_agent for x in ["MSIE", "Microsoft Internet Explorer", "Trident"]]):
                raise RelayWebException(
                    message = request.ctx.tr("web.browser_not_supported"),
                    status_code = 400,
                    title = request.ctx.tr("web.oops")
                )
            # If URL contains "oauth" parameter, go to the OAuth URL.
            if bool(request.get_args().get("oauth", None)):
                return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, request.path))
            # As /authorize already created for redirecting the user, don't redirect user to OAuth
            # again, because this will make a endless loop.
            if (auth_mode != "BASE") and (not request.ctx.token) and (auth_require):
                return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, request.path))
    if fetch_routes and auth_mode:
        # TODO: Is it possible to make this part simplier and more readable?
        api_result = {}
        user_signed_in = True
        client = httpx.AsyncClient()
        server = [x for x in request.path.split("/") if x.isnumeric()]
        flags = None
        if server:
            server = server[0]
            flags = get_server_flags(server)
        else:
            server = ""
        # If USER exists in fetch_routes, then make a
        # request for fetching current user.
        if "USER" in fetch_routes:
            s, r = await send_discord(client, "GET", "/users/@me", ("Bearer", request.ctx.token),)
            if s != 200:
                print("USER failed with " + str(s), r)
                user_signed_in = False
            else:
                api_result["user"] = r
        # If GUILDS exists in fetch_routes, then make a
        # request for fetching user's guilds.
        if "GUILDS" in fetch_routes:
            s, r = await send_discord(client, "GET", "/users/@me/guilds", ("Bearer", request.ctx.token),)
            if s != 200:
                print("GUILDS failed with " + str(s), r)
                user_signed_in = False
            else:
                api_result["guilds"] = {str(x["id"]) : x for x in r}
        # If GUILD exists in fetch_routes, then parse server_id from
        # route path and get the guild data.
        if ("GUILD" in fetch_routes) and user_signed_in and ("GUILDS" in fetch_routes):
            s, r = await send_discord(client, "GET", f"/guilds/{server}", ("Bot", BOT_TOKEN),)
            if (server not in api_result["guilds"]) or (s != 200) or ((flags == None)):
                raise RelayWebException(
                    message = request.ctx.tr("error.invalid_server.description"),
                    status_code = 404,
                    title = request.ctx.tr("error.invalid_server.title")
                )
            # Check for guild permissions, and also ignore check
            # if the server has marked as unrestricted.
            if (auth_permission):
                if not (int(api_result["guilds"][server]["permissions"]) & auth_permission):
                    raise RelayWebException(
                        message = request.ctx.tr("error.missing_permissions.description"),
                        status_code = 403,
                        title = request.ctx.tr("error.missing_permissions.title")
                    )
            api_result["guild"] = r
        # If CHANNELS exists in fetch_routes, then get guild channels.
        if ("CHANNELS" in fetch_routes) and user_signed_in and ("GUILD" in fetch_routes):
            s, r = await send_discord(client, "GET", f"/guilds/{server}/channels", ("Bot", BOT_TOKEN),)
            if (server not in api_result["guilds"]) or (s != 200):
                raise RelayWebException(
                    message = request.ctx.tr("error.invalid_server.description"),
                    status_code = 404,
                    title = request.ctx.tr("error.invalid_server.title")
                )
            api_result["channels"] = r
        await client.aclose()
        # If current user doesn't exists, return to OAuth (if auth is required)
        if (not user_signed_in) and auth_require:
            if auth_mode == "API":
                raise RelayWebException(
                    message = request.ctx.tr("error.not_authorized.description"),
                    status_code = 401,
                    title = request.ctx.tr("error.not_authorized.title")
                )
            else:
                return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, request.path))
        if flags != None:
            request.ctx.server_flags = flags
        request.ctx.user_signed_in = user_signed_in
        request.ctx.discord = api_result


# TODO: For an unknown reason, OAuth goes to loop. So fix that asap.
@bp.get("/authorize", ctx_auth = "BASE")
async def authorize(request : Request):
    args = request.get_args()
    result, redirect_url = parse_state(
        state = args.get("state"), 
        ip = request.ctx.id
    )
    print(dict(args))
    oauth_code = args.get("code") or None
    print(result, redirect_url)
    # If user cancelled the request.
    if args.get("error"):
        raise RelayWebException(
            message = request.ctx.tr("web.oauth.cancelled"),
            status_code = 401,
            title = request.ctx.tr("web.oops")
        )
    # Check if auth link contains redirects.
    elif result == AuthCode.NO_REDIRECT:
        return json({"error": request.ctx.tr("web.oauth.no_redirect")})
    # Is state malformed?
    elif result == AuthCode.INVALID_FORMAT:
        return json({"error": request.ctx.tr("web.oauth.tampering_detected")})
    # Does the headers contain the IP? Because we need it to set the state.
    elif result == AuthCode.MISSING_IDENTIFIER:
        return json({"error": request.ctx.tr("web.oauth.missing_identifier")})
    # Is redirect URL malformed?
    elif result == AuthCode.REDIRECT_DIGEST_FAILED:
        return json({"error": request.ctx.tr("web.oauth.tampering_detected")})
    # Is user forced to go to the OAuth URL?
    elif args.get("forced", None):
        return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, redirect_url))
    # If token has found in cookies, redirect to redirect URL.
    # TODO: Disabled temporarily.
    elif False and (request.ctx.token) and (not oauth_code):
        return redirect(redirect_url)
    # Make sure the callback came from Discord.
    elif result == AuthCode.STATE_DIGEST_FAILED:
        return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, redirect_url))
    # Get OAuth code.
    elif not oauth_code:
        print({"error": "OAuth code couldn't found."})
        return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, redirect_url))
    # Unknown error.
    elif result != AuthCode.DONE:
        print({"error": "Unknown error."})
        return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, redirect_url))
    # Check if token is valid.
    client = httpx.AsyncClient()
    response = await client.post(
        "https://discord.com/api/oauth2/token",
        data = {
            "code": oauth_code,
            "grant_type": "authorization_code",
            "redirect_uri": request.ctx.callback_url
        },
        auth = (CLIENT_ID, CLIENT_SECRET)
    )
    data = load_json(await response.aread()) or {}
    scopes = data.get("scope", "").split(" ")
    await client.aclose()
    if not data:
        return json({"error": request.ctx.tr("web.oauth.error_exchange")})
    elif (response.status_code != 200) or (not data.get("access_token")) or (("identify" not in scopes) or ("guilds" not in scopes)):
        print(data)
        print({"error": "Invalid scope, invalid access token or token has expired."})
        return redirect(oauth_url(request.ctx.id, request.ctx.callback_url, redirect_url))
    encrypted = encrypt_token(data["access_token"])
    resp = redirect(redirect_url)
    resp.cookies["access_token"] = encrypted
    # Setting this to "strict" will cause the cookie not to be saved
    # as this is a redirect response.
    resp.cookies["access_token"]["samesite"] = "lax"
    resp.cookies["access_token"]["expires"] = datetime.datetime.fromtimestamp(time.time() + 604800)
    resp.cookies["access_token"]["max-age"] = 604800
    resp.cookies["access_token"]["secure"] = True
    resp.cookies["access_token"]["httponly"] = True
    return resp