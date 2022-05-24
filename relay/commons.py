from pathlib import Path
from typing import Any, Dict, List, Tuple
from relay.database import MongoDBClient
from relay.enums import RelayFlags, RelayUserFlags
from relay.strings import Strings, StringsStore
from snowflake import Generator, Snowflake
from relay_packages import Marketplace
from os import environ
from dotenv import dotenv_values
from urllib.parse import quote_plus
import socketio

_cur_dir = Path(".").resolve()

env = dotenv_values(".env") or environ
translation = Strings(_cur_dir / "strings", "en")
emojis = translation["emojis"]
sf = Generator(epoch = 157783680000, process_id = 1, worker_id = 1)
marketplace = Marketplace()
sio = socketio.AsyncClient(
    ssl_verify = False,
    reconnection = True,
    reconnection_delay = 6,
    reconnection_attempts = 0,
    reconnection_delay_max = 48
)

MKDOCS_ENABLED = bool(env.get("MKDOCS_ENABLED", False))
# If MKDOCS has enabled, push dummy values to env.
# Because as mkdocstrings plugin actually runs the Python code, it rasies exception because keys are not defined in env.
if MKDOCS_ENABLED:
    env.update({x : "" for x in [
        "BASE_URL", 
        "BOT_TOKEN", 
        "CLIENT_ID", 
        "CLIENT_SECRET", 
        "DEPLOY_TYPE", 
        "GITHUB_BOT_SECRET",
        "MONGODB_URL",
        "OWNER_ID"
    ]})

def bool_env(k, d = None):
    return d if k not in env else (env[k] in ["1", "t", "true"])

# ------------------
# Environment variables
# ------------------

BASE_URL          = env["BASE_URL"].removesuffix("/")
# Base URL specifies the domain that Relay Web 
# is currently hosted on. It is used for connecting to Websocket
# and for generating links in dashboard.

BOT_TOKEN         = env["BOT_TOKEN"]
# Obviously, for connecting to bot.

CLIENT_ID         = env["CLIENT_ID"]
# ID of the bot, used for OAuth and registering Application Commands.

CLIENT_SECRET     = env["CLIENT_SECRET"]
# Secret of OAuth application.

DEPLOY_TYPE       = env["DEPLOY_TYPE"]
# Can be "LOCAL", "PRODUCTION".

OWNER_ID = env["OWNER_ID"]

GITHUB_BOT_ID = "fluxteambot"
GITHUB_BOT_SECRET = env["GITHUB_BOT_SECRET"]
REPORTS_GET = lambda x: f"https://api.github.com/search/issues?q={quote_plus(x)}+in:title+repo:fluxteam/relay-reports&per_page=1"
REPORTS_POST = "https://api.github.com/repos/fluxteam/relay-reports/issues"
MONGODB_URL = env["MONGODB_URL"]

db = MongoDBClient.get(MONGODB_URL, MKDOCS_ENABLED)

def snowflaked() -> Snowflake:
    return sf.generate()

def emoji(k : str) -> str:
    return f"<:{k}:{emojis[k]}>"

def get_server_config(guild_id : str) -> Tuple[StringsStore, Dict[str, Any]]:
    config = db("relay", "servers", guild_id).read()
    return translation[config.get("language", "en_us")], config

def get_server_flags(guild_id : str) -> List[RelayFlags]:
    return [RelayFlags[x] for x in db("relay", "servers", guild_id).read().get("flags") or [] if x in RelayFlags.__members__]

def get_user_flags(user_id : str = None, flags = None) -> List[RelayUserFlags]:
    return [RelayUserFlags[x] for x in ((flags or db("relay", "users", user_id).read().get("flags")) or []) if x in RelayUserFlags.__members__]