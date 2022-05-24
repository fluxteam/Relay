import hashlib, hmac, base64
from cryptography.fernet import Fernet
from typing import Optional, Tuple
from relay.enums import AuthCode
from relay.utils import build_url
from relay.commons import CLIENT_ID, CLIENT_SECRET


def create_sha256(
    text : str
) -> str:
    """
    Encodes a ASCII text to SHA256.
    """
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def create_sha1(
    text : str
) -> str:
    """
    Encodes a ASCII text to SHA1.
    """
    return hashlib.sha1(text.encode("ascii")).hexdigest()


def compare(
    text1 : str,
    text2 : str
) -> bool:
    """
    Compares two texts in accordance with cryptography.
    """
    return hmac.compare_digest(text1, text2)


def create_state(
    ip : str,
    redirect_path : str
) -> str:
    """
    Creates a state value that will be inserted in the Discord OAuth link.
    The state contains three values which joined with ":" colon.

    First one is a digest that created from IP. This makes sure the the request is coming from Discord.
    Second one is the redirect path, when Discord OAuth completes, Relay will redirect user to this url. It is encoded in HEX.
    Third one is the digest of the redirect path, so people can't modify the redirect url themselves as this digest will be used to verify redirect_path.
    """
    red = redirect_path.encode("ascii").hex()
    return \
        ":".join([
            create_sha256(CLIENT_SECRET + ip),
            red,
            create_sha256(CLIENT_SECRET + red)
        ])


def parse_state(
    state : str,
    ip : str
) -> Tuple[AuthCode, Optional[str]]:
    """
    Parses a state value that created from create_state() function and returns a redirect URL.
    Redirect URL will be none if auth error is "INVALID_FORMAT", "MISSING_IDENTIFIER", "NO_REDIRECT" or "REDIRECT_DIGEST_FAILED"

    If state doesn't contain two ":" colons (the format is invalid) or state doesn't match,
    or redirect URL is not valid returns a AuthCode enum.
    """
    if (not state) or (state.count(":") != 2):
        return AuthCode.INVALID_FORMAT, None
    elif not ip:
        return AuthCode.MISSING_IDENTIFIER, None
    st, red, red_digest = state.split(":")
    if (not red) or (not red_digest):
        return AuthCode.NO_REDIRECT, None
    red_decoded = parse_hex(red)
    if not compare(create_sha256(CLIENT_SECRET + red), red_digest):
        return AuthCode.REDIRECT_DIGEST_FAILED, None
    if not compare(st, create_sha256(CLIENT_SECRET + ip)):
        return AuthCode.STATE_DIGEST_FAILED, red_decoded
    return AuthCode.DONE, red_decoded


def parse_hex(
    text : str
) -> str:
    """
    Decodes a hex value.
    """
    try:
        return bytes.fromhex(text).decode("ascii", "ignore")
    except Exception:
        return ""


def encrypt_token(
    token : str
) -> str:
    """
    Encrypts a OAuth access token.
    """
    fernet = Fernet(base64.urlsafe_b64encode(CLIENT_SECRET))
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(
    token : str
) -> Optional[str]:
    """
    Decrypts a OAuth access token. If token is not valid, returns None.
    """
    try:
        if not token:
            return None
        fernet = Fernet(base64.urlsafe_b64encode(CLIENT_SECRET))
        return fernet.decrypt(token.encode()).decode()
    except Exception:
        return None


def oauth_url(
    ip : str, 
    discord_redirect : str,
    relay_redirect : str,
    include_bot : bool = False,
    guild_id : Optional[str] = None
):
    """
    Creates a Discord OAuth URL.
    """
    return build_url("https://discord.com/api/oauth2/authorize", {
        "client_id": CLIENT_ID,
        "redirect_uri": discord_redirect,
        "state": create_state(ip = ip, redirect_path = relay_redirect),
        "response_type": "code",
        "scope": "identify guilds bot applications.commands" if include_bot else "identify guilds",
        "permissions": "1503738195030" if include_bot else None,
        "guild_id": guild_id if include_bot else None,
        "disable_guild_select": "true" if include_bot and guild_id else None
    })