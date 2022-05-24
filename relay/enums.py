__all__ = [
    "InteractionType",
    "ButtonStyle",
    "RelayFlags",
    "RelayUserFlags",
    "AuthCode",
    "RoleMember",
    "RealtimeEvent",
    "ModelExportOptions",
    "TextInputStyle",
    "DiscordLanguage"
]

from collections import namedtuple
from enum import Enum

# Link to docs:
# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type
class InteractionType(Enum):
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class RoleMember(Enum):
    ROLE = 0
    MEMBER = 1


class ModelExportOptions(Enum):
    EXCLUDE_NONE = 1


class RealtimeEvent(Enum):
    """
    Operation codes to use in Relay Realtime server and client.
    """
    # A new Blockly event sent from other clients to current connected client.
    PAYLOAD = "PAYLOAD"

    # Require the current connected client to send their blocks to other clients. 
    # This is required for preventing sync issues when connecting to a workspace
    # that contains unsaved changes from another user.
    NEED_SYNC = "NEED_SYNC"

    # A new user has joined to or left from a collaboration session.
    # The payload contains a dictionary of all users.
    USER_REFRESH = "USER_REFRESH"

    # Tell the client to re-load their workspace with current blocks.
    LOAD_BLOCKS = "LOAD_BLOCKS"

    # Connected to workspace.
    INIT = "INIT"

    # Abort the operation.
    ERROR = "ERROR"

    # Got a log for workflow.
    WORKFLOW_LOG = "WORKFLOW_LOG"


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#button-object-button-styles
class ButtonStyle(Enum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#text-inputs-text-input-styles
class TextInputStyle(Enum):
    SHORT = 1
    PARAGRAPH = 2


class RelayFlags(Enum):
    # A Relay Action has triggered by a Relay package.
    # https://github.com/fluxteam/relay-packages
    PACKAGE = "PACKAGE"

    # A Relay Action has triggered by a Relay package
    # that made by FluxTeam.
    # https://github.com/fluxteam/relay-packages
    FLUX_PACKAGE = "FLUX_PACKAGE"

    # The server has a relation with FluxTeam.
    # Like Flux, WordBot, KoiosBot... servers.
    FLUX_SERVER = "FLUX_SERVER"

    # The server has appoved to use Relay Actions.
    ACTIONS_ACCESS = "ACTIONS_ACCESS"


class RelayUserFlags(Enum):
    # User can invite Relay to their server.
    PRIVATE_USE = "PRIVATE_USE"

    # User is from FluxTeam.
    FLUX = "FLUX"


class AuthCode(Enum):
    INVALID_FORMAT = 1
    STATE_DIGEST_FAILED = 2
    REDIRECT_DIGEST_FAILED = 3
    MISSING_IDENTIFIER = 4
    NO_REDIRECT = 5
    DONE = 0


_LanguageType = namedtuple("DiscordLanguage", ["name", "native"])

# Available Discord languages.
# https://discord.com/developers/docs/reference#locales
class DiscordLanguage(_LanguageType, Enum):
    EN_US = "English, US", "English, US",
    EN_GB = "English, UK", "English, UK",
    BG	  = "Bulgarian", "български",
    ZH_CN = "Chinese, China", "中文",
    ZH_TW = "Chinese, Taiwan", "繁體中文",
    HR	  = "Croatian", "Hrvatski",
    CS	  = "Czech", "Čeština",
    DA    = "Danish", "Dansk",
    NL	  = "Dutch", "Nederlands",
    FI	  = "Finnish", "Suomi",
    FR	  = "French", "Français",
    DE    = "German", "Deutsch",
    EL	  = "Greek", "Ελληνικά",
    HI	  = "Hindi", "हिन्दी",
    HU	  = "Hungarian", "Magyar",
    IT	  = "Italian", "Italiano",
    JA	  = "Japanese", "日本語",
    KO	  = "Korean", "한국어",
    LT	  = "Lithuanian", "Lietuviškai",
    NO	  = "Norwegian", "Norsk",
    PL	  = "Polish", "Polski",
    PT_BR = "Portuguese, Brazilian", "Português do Brasil",
    RO	  = "Romanian, Romania", "Română",
    RU	  = "Russian", "Pyccкий",
    SV_SE = "Swedish", "Svenska",
    TH	  = "Thai", "ไทย",
    TR	  = "Turkish", "Türkçe",
    UK	  = "Ukrainian", "Українська",
    VI	  = "Vietnamese", "Tiếng Việt",

    def __str__(self) -> str:
        return self.name