__all__ = [
    "Events",
    "DictPayload",
    "RelayBot"
]

from enum import Enum
from hikari import UNDEFINED, GatewayBot
from hikari.internal.routes import Route
from relay.models import Model


class RelayBot(GatewayBot):
    async def request(self, route : Route, route_params : dict, **kwargs):
        return await self._rest._request(route.compile(**route_params), json = kwargs)

    """
    async def request(self, route : Route, **kwargs):
        # Get keys from route path.
        keys = PARAM_REGEX.findall(route.path_template)
        payload = {x : y for x, y in kwargs.items() if not x.startswith("_")}
        return await self._rest._request(route.compile(**{x for x in }), json = payload)
    """


class Events(Enum):
    # Message
    MESSAGE_SEND = "MESSAGE_SEND"
    MESSAGE_DELETE = "MESSAGE_DELETE"
    MESSAGE_DELETE_BULK = "MESSAGE_DELETE_BULK"
    MESSAGE_EDIT = "MESSAGE_EDIT"
    # Reaction
    REACTION_ADD = "REACTION_ADD"
    REACTION_REMOVE = "REACTION_REMOVE"
    REACTION_REMOVE_ALL = "REACTION_REMOVE_ALL"
    REACTION_REMOVE_EMOJI = "REACTION_REMOVE_EMOJI"
    # Channel
    CHANNEL_CREATE = "CHANNEL_CREATE"
    CHANNEL_DELETE = "CHANNEL_DELETE"
    CHANNEL_UPDATE = "CHANNEL_UPDATE"
    CHANNEL_PINS_UPDATE = "CHANNEL_PINS_UPDATE"
    # Member
    MEMBER_JOIN = "MEMBER_JOIN"
    MEMBER_REMOVE = "MEMBER_REMOVE"
    MEMBER_BAN = "MEMBER_BAN"
    MEMBER_UNBAN = "MEMBER_UNBAN"
    # Others
    SERVER_UPDATE = "SERVER_UPDATE"
    VOICE_STATE_UPDATE = "VOICE_STATE_UPDATE"
    # Remote
    PACKAGE_INSTALL = "PACKAGE_INSTALL"
    PACKAGE_UNINSTALL = "PACKAGE_UNINSTALL"
    INTERACTION_CREATE = "INTERACTION_CREATE"
    WEBHOOK = "WEBHOOK"

    def is_remote(self):
        return str(self.value) in [
            "PACKAGE_INSTALL",
            "PACKAGE_UNINSTALL",
            "INTERACTION_CREATE",
            "WEBHOOK"
        ]


class DictPayload(dict):
    """
    A subclass of dict that converts pydantic models to dictionaries
    and ignores hikari's UNDEFINED values automatically.
    """
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, item):
        if item == UNDEFINED:
            return
        if isinstance(item, Model):
            dict.__setitem__(self, key, item.to_dict())
        else:
            dict.__setitem__(self, key, item)
    
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v