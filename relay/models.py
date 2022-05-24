"""
Relay uses its own models instead of using hikari's own models. That's because, having custom models
gives more flexibility, allows defining new attributes without waiting for hikari to add. 

Lastly, hikari doesn't directly allow dumping Discord objects to dictionaries. But as we use pydantic 
for models, we can just use pydantic's own dumping feature without defining dumps() for each model manually.
"""

import orjson
import hikari
from hikari.impl.special_endpoints import ActionRowBuilder
from hikari.users import UserFlag
from hikari import UNDEFINED
from pydantic import BaseModel, validator, HttpUrl, Extra, Field, root_validator, conint, constr, conlist
from pydantic.color import (RGBA, ColorType, ints_to_rgba, parse_str, parse_tuple)
from pydantic.color import Color as PydanticColor
from typing import Dict, List, Optional, Literal, Union, Any, Callable
from datetime import datetime, timedelta
from pydantic.errors import ColorError
from pydantic.fields import ModelField
from pydantic.main import BaseConfig
from pydantic.networks import AnyUrl
from string import ascii_lowercase, digits
from relay.enums import ButtonStyle, InteractionType, ModelExportOptions, RoleMember, TextInputStyle


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default, option=orjson.OPT_NON_STR_KEYS).decode(encoding = "utf-8")


class Model(BaseModel):
    _export_options : List[ModelExportOptions] = []

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.ignore
        copy_on_model_validation = False
        allow_population_by_field_name = True
        underscore_attrs_are_private = True
        use_enum_values = True
        json_encoders = {
            UserFlag: lambda x: int(x),
            HttpUrl: lambda x: str(x)
        }
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    def to_dict(self):
        options = {}
        if self._export_options:
            for i in self._export_options:
                if i == ModelExportOptions.EXCLUDE_NONE:
                    options["exclude_none"] = True
        if options:
            return orjson.loads(self.json(**options))
        return orjson.loads(self.json())


class Snowflake(str):
    """
    Snowflake is a type that used for IDs in Discord. Some places may store Snowflakes as strings or integers.
    However, even Python doesn't have any issues with big integers, databases don't like big integer, so
    Relay stores Snowflakes as strings always.
    """
    _allow_objects = False

    def __new__(cls, obj : object = None):
        if obj == None:
            raise TypeError("Snowflakes can't be null.")
        # If a compatible model has provided, get ID from it.
        elif cls._allow_objects and isinstance(obj, (Channel, Message, Member, User, Overwrites, Role)):
            return super().__new__(cls, obj.id)
        # If an dict object has provided, get ID from it.
        elif cls._allow_objects and isinstance(obj, dict) and ("id" in obj):
            return super().__new__(cls, obj["id"])
        # If an dict Member object has provided, get ID from it.
        elif cls._allow_objects and isinstance(obj, dict) and ("id" in obj.get("user", {})):
            return super().__new__(cls, obj["user"]["id"])
        elif isinstance(obj, (str, int)):
            try:
                return super().__new__(cls, str(int(obj)))
            except ValueError:
                raise TypeError("Snowflakes must only contain numbers.")
        raise ValueError(f"Invalid snowflake compatible type, {type(obj)}.")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return cls(v)


class ObjectOrSnowflake(Snowflake):
    """
    Same as Snowflake, but supports getting ID from existing Discord objects too.
    Instead of typing `Snowflake(message.user.id)`, it is possible to use `ObjectOrSnowflake(message.user)`
    """
    _allow_objects = True


class ExtendedUrl(HttpUrl):
    """
    A wrapper for pydantic.HttpUrl but also supports getting URL from dictionaries with `url` key.
    So this allows user to create image objects for embeds both creating a new object with `url` key
    or by just providing a URL.

    Example:
    - `{"image": {"url": "https://example.com"}}`
    - `{"image": "https://example.com"}`
    """

    @classmethod
    def validate(cls, value: Any, field: 'ModelField', config: 'BaseConfig') -> 'AnyUrl':
        if isinstance(value, dict) and "url" in value:
            return super().validate(value["url"], field, config)
        return super().validate(value, field, config)


class AdaptiveList(list):
    """
    A list type that also wraps single values in lists.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any):
        if value == None:
            return []
        if not isinstance(value, list):
            return [value]
        return value


class ServerGuard(ObjectOrSnowflake):
    """
    A type that executes guard_check() method on current guild and current field.
    """

    @classmethod
    def validate(cls, value: Any, values: dict):
        x = cls(value)
        if "guild__" in values:
            if cls.guard_check(str(x), values["guild__"]):
                return x
            raise ValueError("This object doesn't belong to current server.")
        raise ValueError(f"Other fields doesn't have a 'guild__' field.")
    
    @staticmethod
    def guard_check(value, guild : hikari.Guild):
        return True


class ValidChannel(ServerGuard):
    """
    A type that checks if specified channel is in the server.
    """

    @staticmethod
    def guard_check(value, guild : hikari.Guild):
        return None != guild.get_channel(str(value))


class ValidMember(ServerGuard):
    """
    A type that checks if specified member is in the server.
    """

    @staticmethod
    def guard_check(value, guild : hikari.Guild):
        return None != guild.get_member(str(value))


class Color(PydanticColor):
    """
    A wrapper for pydantic's Color, but also supports integer colors and has methods to
    convert the object between hikari's Color and pydantic's Color in both direction.
    """
    def __init__(self, value: Union[ColorType, int]) -> None:
        self._rgba: RGBA
        self._original: ColorType
        if isinstance(value, (tuple, list)):
            self._rgba = parse_tuple(value)
        elif isinstance(value, str):
            self._rgba = parse_str(value)
        elif isinstance(value, int):
            self._rgba = ints_to_rgba((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF, None)
        elif isinstance(value, PydanticColor):
            self._rgba = value._rgba
            value = value._original
        else:
            raise ColorError(reason='Value must be a tuple, list, integer or string')
        # if we've got here value must be a valid color
        self._original = value

    @classmethod
    def from_object(cls, obj : hikari.Color) -> "Color":
        return cls(obj.hex_code)

    def to_object(self) -> hikari.Color:
        return hikari.Color.from_rgb(*self.as_rgb_tuple(alpha = False))

    @property
    def integer(self) -> int:
        t = self.as_rgb_tuple(alpha = False)
        return (t[0] << 16) + (t[1] << 8) + t[2]


class Permissions(int):
    """
    An integer object that built top on hilari.Permissions.
    This is a more flexible object instead of hikari's own object as this supports
    both names (like "BAN_MEMBERS"), list of names or integers ([1, 2, 4] and ["BAN_MEMBERS", "KICK_MEMBERS"]),
    and integers.
    """
    _validate_perms = True
    
    def __new__(cls, __x = None) -> None:
        if not __x:
            return super().__new__(cls, hikari.Permissions.NONE)
        elif isinstance(__x, (int, hikari.Permissions)):
            if cls._validate_perms:
                return super().__new__(cls, sum([x for x in hikari.Permissions if x & __x]))
            else:
                return super().__new__(cls, int(__x))
        elif isinstance(__x, list):
            return super().__new__(cls, sum([en for en in hikari.Permissions if (en.name in __x) or (en.value in __x)]))
        elif isinstance(__x, str):
            return super().__new__(cls, hikari.Permissions.__members__.get(__x, hikari.Permissions.NONE))
        else:
            raise ValueError(f"An permission integer, name, list of integer, list of name has supported, not {type(__x)}.")

    def split(self) -> List[hikari.Permissions]:
        return hikari.Permissions(int(self)).split()

    def extend(self, other : Union[int, hikari.Permissions, list, str]) -> "Permissions":
        return Permissions(int(self) + int(Permissions(other)))

    def remove(self, other : Union[int, hikari.Permissions, list, str]) -> "Permissions":
        return Permissions(int(self) - int(Permissions(other)))

    def __add__(self, __x: int) -> "Permissions":
        return self.extend(__x)

    def __sub__(self, __x: int) -> int:
        return self.remove(__x)

    def names(self) -> List[str]:
        return [x.name for x in self.split()]

    def values(self) -> List[int]:
        return [x.value for x in self.split()]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return Permissions(v)


# Link to docs:
# https://discord.com/developers/docs/resources/channel#overwrite-object-overwrite-structure
class Overwrites(Model):
    """
    Overwrites defines which users and roles has specified permissions for a channel. 
    This overrides the channel's own permissions.

    Attributes:
        type:
            Either `"ROLE"` or `"MEMBER"`. 
            For backwards compatibility, it also supports using `0` (for role) and `1` (for member).
        id:
            Role or user ID that this overwrite will apply for.
        allow:
            When sending, list of Discord permission names or bit values, or a integer that contains merged permission bit.
            When receiving, this will be a list of Discord permission names.
        deny:
            When sending, list of Discord permission names or bit values, or a integer that contains merged permission bit.
            When receiving, this will be a list of Discord permission names.
    """
    type : RoleMember
    id : Snowflake
    allow : Permissions = 0
    deny : Permissions = 0

    @classmethod
    def from_object(cls, obj : hikari.PermissionOverwrite):
        return cls(
            id = obj.id,
            type = int(obj.type),
            allow = obj.allow,
            deny = obj.deny
        )

    def to_object(self):
        return hikari.PermissionOverwrite(
            id = self.id,
            type = self.type,
            allow = int(self.allow),
            deny = int(self.deny)
        )


# Link to docs:
# https://discord.com/developers/docs/reference#image-formatting-cdn-endpoints
class Asset(str):
    """
    Represents a Discord asset.
    """
    _cdn : str = "https://cdn.discordapp.com"
    _route : str
    _parser : Optional[Callable[[str, dict], list]] = None
    args : List[str]

    def __new__(cls, args, *, ext = None):
        if not args:
            raise ValueError("Asset arguments can't be blank.")
        if cls._route.count("{}") != len(args):
            raise ValueError("Route parameter count is not same with positional argument count.")
        ex = "." + ("gif" if (ext == None) and args[-1].startswith("a_") else ext if ext else "png")
        o = super().__new__(cls, cls._cdn + cls._route.format(*args) + ex)
        o.args = args
        return o

    @classmethod
    def validate(cls, v, field, values):
        p = field.type_._parser
        if p:
            return cls(p(v, values))
        else:
            return cls(v if isinstance(v, list) else [v])

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @property
    def value(self) -> str:
        return self.args[-1]

    @property
    def animated(self):
        return self.value.startswith("a_")

    @classmethod
    def create_type(cls, name : str, route : str, parser : Optional[Callable[[str, dict], list]] = None) -> "Asset":
        # Creates new Asset type that tied to a CDN route.
        return type(name + "Asset", (cls, ), {"_route": route, "_parser": parser})


ROLE_ICON_ASSET         = Asset.create_type("RoleIcon", "/role-icons/{}/{}", lambda v, values: [values["id"], v])
SERVER_ICON_ASSET       = Asset.create_type("ServerIcon", "/icons/{}/{}", lambda v, values: [values["id"], v])
SERVER_SPLASH_ASSET     = Asset.create_type("ServerSplash", "/splashes/{}/{}", lambda v, values: [values["id"], v])
USER_ICON_ASSET         = Asset.create_type("UserIcon", "/avatars/{}/{}", lambda v, values: [values["id"], v])
MEMBER_ICON_ASSET       = Asset.create_type("MemberIcon", "/guilds/{}/users/{}/avatars/{}", lambda v, values: [values["guild_id"], values["user"].id, v])
DEFAULT_USER_ICON_ASSET = Asset.create_type("DefaultUserIcon", "/embed/avatars/{}")


# Link to docs:
# https://discord.com/developers/docs/resources/channel#allowed-mentions-object
class Mentions(Model):
    """
    The allowed mention field allows for more granular control over mentions without various hacks to the message content. 
    This will always validate against message content to avoid phantom pings (e.g. to ping everyone, you must still have `@everyone` in the message content), 
    and check against user/bot permissions.

    Attributes:
        roles:
            Controls the roles being mentioned. If `True` (the default) then roles are mentioned based on the message content. 
            If `False` then roles are not mentioned at all. If a list of role IDs is given, then only the roles provided will be mentioned, 
            provided those roles are in the message content.
        users:
            Controls the users being mentioned. If `True` (the default) then users are mentioned based on the message content. 
            If `False` then users are not mentioned at all. If a list of role IDs is given, then only the users provided will be mentioned, 
            provided those users are in the message content.
        everyone:
            Whether to allow everyone and here mentions. Defaults to `False`.
        replied_user:
            Whether to mention the author of the message being replied to. Defaults to `False`.
    """

    roles : Union[bool, List[ObjectOrSnowflake]] = True
    users : Union[bool, List[ObjectOrSnowflake]] = True
    everyone : bool = False
    replied_user : bool = False

    def to_dict(self):
        output = {"parse": []}
        # Add roles
        if self.roles == True: 
            output["parse"].append("roles")
        elif self.roles: 
            output["roles"] = self.roles
        # Add users
        if self.users == True:
            output["parse"].append("users")
        elif self.users:
            output["users"] = self.users
        # Add everyone
        if self.everyone:
            output["parse"].append("everyone")
        # Add replied user.
        if self.replied_user:
            output["replied_user"] = self.replied_user
        return output


# Link to docs:
# https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure
class EmbedField(Model):
    """
    A Discord embed field object.

    Attributes:
        name:
            Field name.
        value:
            Field value.
        inline:
            Whether or not this field should display inline. Defaults to `False`.
    """

    name : str
    value : str
    inline : bool = False

    @classmethod
    def from_object(cls, obj : hikari.EmbedField):
        return cls(
            name = obj.name,
            value = obj.value,
            inline = obj.is_inline
        )


# Link to docs:
# https://discord.com/developers/docs/resources/channel#embed-object-embed-footer-structure
class EmbedFooter(Model):
    """
    A Discord footer object.

    Attributes:
        text:
            Footer text.
        icon_url:
            URL of footer icon (only supports http(s))
    """
    _export_options = [ModelExportOptions.EXCLUDE_NONE]

    text : str
    icon_url : Optional[HttpUrl] = None

    @classmethod
    def from_object(cls, obj : hikari.EmbedFooter):
        return cls(
            text = obj.text,
            icon_url = None if not obj.icon else obj.icon.url
        )

    def to_dict(self):
        return {"text": self.text} if not self.icon_url else {"text": self.text, "icon_url": str(self.icon_url)}


# Link to docs:
# https://discord.com/developers/docs/resources/channel#embed-object-embed-author-structure
class EmbedAuthor(Model):
    """
    A Discord author object.

    Attributes:
        name:
            Author text.
        url:
            URL of author.
        icon_url:
            URL of author icon (only supports http(s))
    """
    _export_options = [ModelExportOptions.EXCLUDE_NONE]

    name : str
    url : Optional[HttpUrl] = None
    icon_url : Optional[HttpUrl] = None

    @classmethod
    def from_object(cls, obj : hikari.EmbedAuthor):
        return cls(
            name = obj.name,
            url = obj.url,
            icon_url = None if not obj.icon else obj.icon.url
        )


# Link to docs:
# https://discord.com/developers/docs/resources/channel#embed-object
class Embed(Model):
    """
    A Discord embed object. Embed objects are same as Discord embeds, however you can also use Relay-flavored 
    embeds which is much easier to create a new embed as it doesn't require nested objects. 
    You can both create embeds in old and Relay style and they all will create same result.
    
    Attributes:
        title:
            Title of the embed.
        description:
            Description of the embed.
        url:
            URL of the embed.
        color:
            Color code of embed in integer. 
            If you are creating a new embed, you can set HEX, RGB and color names (etc. "red", "brown") in this field and they will be converted automatically.
        timestamp:
            A timestamp of embed content.
        image:
            URL of the embed image.
        thumbnail:
            URL of the embed thumbnail.
        fields:
            List of [embed field objects](entities#embed-field) in this embed.
        footer:
            A [footer object](entities#embed-footer) for this embed.
        author:
            A [author object](entities#embed-author) for this embed.

    ??? example "Difference between Discord and Relay-flavored embeds"

        === "Discord"
            ```json
            {
                "title": "Embed Title",
                "description": "Description",
                "color": 16711680,
                "image": {
                    "url": "https://picsum.photos/200.jpg",
                }
                "fields": [
                    { "name": "Field 1", "value": "Field value 1", "inline": false }
                ]
            }
            ```

            * Discord embeds only accepts integer colors in `color` key.
            * If you want to add an image, you need to create an object in `image` and set `url` key.

        === "Relay-flavored"
            ```json
            {
                "title": "Embed Title",
                "description": "Description",
                "color": "red",
                "image": "https://picsum.photos/200.jpg",
                "fields": [
                    { "name": "Field 1", "value": "Field value 1", "inline": false }
                ]
            }
            ```

            * Relay-flavored embeds accepts all types of color; name (like "red", "brown"), HEX, RGB and integer.
            * It doesn't require adding object in `image`, instead you can provide a URL directly. But you can add another object with `url` key as always.
    """
    _export_options = [ModelExportOptions.EXCLUDE_NONE]

    title : Optional[str] = None
    description : Optional[str] = None
    url : Optional[HttpUrl] = None
    color : Optional[Color] = None
    timestamp : Optional[datetime] = None
    # TODO: Support attachments in future.
    image : Optional[ExtendedUrl] = None
    thumbnail : Optional[ExtendedUrl] = None
    fields : Optional[List[EmbedField]] = None
    footer : Optional[EmbedFooter] = None
    author : Optional[EmbedAuthor] = None

    @classmethod
    def from_object(cls, obj : hikari.Embed):
        return cls(
            title = obj.title,
            description = obj.description,
            url = obj.url,
            color = None if not obj.color else obj.color.hex_code,
            timestamp = obj.timestamp,
            image = None if not obj.image else obj.image.url,
            thumbnail = None if not obj.thumbnail else obj.thumbnail.url,
            fields = [EmbedField.from_object(x) for x in obj.fields],
            footer = None if not obj.footer else EmbedFooter.from_object(obj.footer),
            author = None if not obj.author else EmbedAuthor.from_object(obj.author)
        )

    def to_object(self) -> hikari.Embed:
        embed = hikari.Embed(
            title = self.title,
            description = self.description,
            url = None if not self.url else str(self.url),
            color = None if not self.color else self.color.integer,
            timestamp = self.timestamp
        )
        if self.image:
            embed.set_image(str(self.image))
        if self.thumbnail:
            embed.set_thumbnail(str(self.thumbnail))
        for field in (self.fields or []):
            embed.add_field(name = field.name, value = field.value, inline = field.inline)
        if self.footer:
            embed.set_footer(text = self.footer.text, icon = None if not self.footer.icon_url else str(self.footer.icon_url))
        if self.author:
            embed.set_author(
                name = self.author.name, 
                icon = None if not self.author.icon_url else str(self.author.icon_url), 
                url = None if not self.author.url else str(self.author.url)
            )
        return embed


# Link to docs:
# https://discord.com/developers/docs/resources/channel#channels-resource
class Channel(Model):
    """
    Represents a channel in a server. Channel can be any type of channel.

    Attributes:
        id:
            The ID of this entity.
        position:
            The sorting position of the channel. Higher numbers appear further down the channel list.
        type:
            The channel's [type](https://discord.com/developers/docs/resources/channel#channel-object-channel-types){ target="_blank" }.
        name:
            The name of the channel. (1-100 characters)
        topic:
            The channel topic. (0-1024 characters)
        nsfw:
            Whether the channel is NSFW.
        parent_id:
            For server channels: ID of the parent category for a channel (each parent category can contain up to 50 channels), 
            for threads: ID of the text channel this thread was created.
        permissions:
            A dictionary of ID and [Overwrites](entities#overwrites).
        last_message_id:
            The ID of the last message sent in this channel (may not point to an existing or valid message).
        last_pin_timestamp:
            When the last pinned message was pinned.
        bitrate:
            The bitrate (in bits) of the voice channel.
        cooldown:
            Amount of seconds a user has to wait before sending another message (0-21600); 
            Bots, as well as users with the permission `MANAGE_MESSAGES` or `MANAGE_CHANNEL`, are unaffected.
            If channel is not a text channel, then this will be `0`.
        user_limit:
            The user limit of the voice channel. 
            If there is no user limit or channel is not a text channel then this will be `0`.
    """

    id : Snowflake
    position : int
    type : int
    name : str
    topic : Optional[str]
    nsfw : bool = False
    parent_id : Optional[Snowflake]
    permissions : Dict[Snowflake, Overwrites] = Field(alias = "permission_overwrites")
    last_message_id : Optional[Snowflake]
    last_pin_timestamp : Optional[datetime]
    bitrate : Optional[int]
    cooldown : Optional[int] = Field(None, alias = "rate_limit_per_user")
    user_limit : Optional[int] = None

    @validator("permissions", always = True, pre = True, check_fields = False)
    def set_permission_overwrites(cls, v):
        if isinstance(v, list):
            return {x["id"] : Overwrites(**x) for x in v}
        return v or {}

    @classmethod
    def from_object(cls, obj : hikari.GuildChannel):
        return cls(
            id = obj.id,
            position = obj.position,
            type = int(obj.type),
            name = obj.name,
            topic = getattr(obj, "topic", None),
            nsfw = obj.is_nsfw or False,
            parent_id = obj.parent_id,
            permissions = {x : Overwrites.from_object(y) for x, y in obj.permission_overwrites.items()},
            last_message_id = getattr(obj, "last_message_id", None),
            last_pin_timestamp = getattr(obj, "last_pin_timestamp", None),
            bitrate = getattr(obj, "bitrate", None),
            cooldown = getattr(obj, "rate_limit_per_user", timedelta(seconds = 0)).seconds,
            user_limit = getattr(obj, "user_limit", 0)
        )


# Link to docs:
# https://discord.com/developers/docs/topics/permissions#role-object
class Role(Model):
    """
    A role in a server.

    Attributes:
        id:
            The ID of this entity.
        name:
            The role's name.
        color:
            The colour of this role. This will be applied to a member's name in chat if it's their top coloured role.
        hoist:
            Whether this role is hoisting the members it's attached to in the member list.
            Members will be hoisted under their highest role where this is set to `True`
        position:
            The position of this role in the role hierarchy.
            This will start at `0` for the lowest role (@everyone) and increase as you go up the hierarchy.
        permissions:
            List of Discord permissions.
        managed:
            Whether this role is managed by an integration.
        mentionable:
            Whether this role can be mentioned by all regardless of permissions.
        boost_role:
            Whether this is the server's Server Booster role.
        icon:
            Hash of the role icon, if there is one.
    """

    id : Snowflake
    name : str
    color : Color
    hoist : bool
    position : int
    permissions : Permissions
    managed : bool
    mentionable : bool
    boost_role : bool
    icon : Optional[ROLE_ICON_ASSET]

    @classmethod
    def from_object(cls, obj : hikari.Role):
        return cls(
            id = obj.id,
            name = obj.name,
            color = obj.color,
            hoist = obj.is_hoisted,
            position = obj.position,
            permissions = obj.permissions,
            managed = obj.is_managed,
            mentionable = obj.is_mentionable,
            boost_role = obj.is_premium_subscriber_role,
            icon = obj.icon_hash
        )


# Link to docs:
# https://discord.com/developers/docs/resources/guild#guild-object-guild-structure
class Server(Model):
    """
    Represents a server.

    Attributes:
        id:
            The ID of this entity.
        name:
            The name of the server.
        description:
            The server's description. Only Community servers has a description, so if server is not a Community server,
            then this will be always `None`.
        icon:
            The hash for the server icon, if there is one.
        splash:
            The hash of the splash for the server, if there is one.
        owner_id:
            The ID of the owner of this server.
        boost_level:
            The boost level of the server (0-3).
        channels:
            A mapping of IDs and [Channel](entities#channel) objects.
        roles:
            A mapping of IDs and [Role](entities#role) objects.
        features:
            List of [server features](https://discord.com/developers/docs/resources/guild#guild-object-guild-features){ target="_blank" }.
        nsfw_level:
            Server [NSFW level](https://discord.com/developers/docs/resources/guild#guild-object-guild-nsfw-level){ target="_blank" }.
    """

    id : Snowflake
    name : str
    description : Optional[str]
    icon : Optional[SERVER_ICON_ASSET]
    splash : Optional[SERVER_SPLASH_ASSET]
    owner_id : Snowflake
    boost_level : int
    channels : Dict[Snowflake, Channel]
    roles : Dict[Snowflake, Role]
    features : List[str]
    nsfw_level : hikari.GuildNSFWLevel

    @classmethod
    def from_object(cls, obj : hikari.Guild):
        return cls(
            id = obj.id,
            name = obj.name,
            description = obj.description,
            icon = obj.icon_hash,
            splash = obj.splash_hash,
            owner_id = obj.owner_id,
            boost_level = int(obj.premium_tier),
            channels = {x : Channel.from_object(y) for x, y in obj.get_channels().items()},
            roles = {x : Role.from_object(y) for x, y in obj.get_roles().items()},
            features = obj.features,
            nsfw_level = obj.nsfw_level
        )


# Link to docs:
# https://discord.com/developers/docs/resources/user#user-object
class User(Model):
    """
    Represents a user in Discord.

    Attributes:
        id:
            The ID of this entity.
        username:
            Username for the user.
        discriminator:
            The user's 4-digit discord-tag.
        avatar:
            Avatar hash for the user, if they have one, otherwise `None`.
        default_avatar:
            Default avatar shown for user, this will be always filled even if user has a avatar.
        bot:
            `True` if this user is a bot account, `False` otherwise.
        system:
            `True` if this user is a system account, `False` otherwise.
        flags:
            List of [user flags](https://discord.com/developers/docs/resources/user#user-object-user-flags){ target="_blank" }.
    """

    id : Snowflake
    username : str
    discriminator : str
    avatar : Optional[USER_ICON_ASSET]
    default_avatar : DEFAULT_USER_ICON_ASSET = UNDEFINED
    bot : bool = False
    system : bool = False
    flags : List[hikari.UserFlag] = Field([], alias = "public_flags")

    @validator("default_avatar", always = True, pre = True, check_fields = False)
    def get_default_avatar(cls, v, values):
        if v != UNDEFINED:
            raise ValueError("User.default_avatar is read-only field, it is generated automatically")
        return str(int(values["discriminator"]) % 5)

    @validator("flags", pre = True)
    def parse_flags(cls, v):
        if isinstance(v, int):
            return [x for x in hikari.UserFlag if x & v]
        return v

    @classmethod
    def from_object(cls, obj : hikari.User):
        return cls(
            id = obj.id,
            username = obj.username,
            discriminator = obj.discriminator,
            avatar = obj.avatar_hash,
            bot = obj.is_bot,
            system = obj.is_system,
            flags = obj.flags
        )


# Link to docs:
# https://discord.com/developers/docs/resources/guild#guild-member-object
class Member(Model):
    """
    Represents a valid member in server.

    Attributes:
        guild_id:
            ID of the server that this member data came from.
        user:
            The user this server member represents.
        avatar:
            A member avatar that set for this server, `None` if not set.
        nickname:
            This member's nickname. This will be `None` if not set.
        roles:
            List of role IDs the user has.
        joined_at:
            The datetime of when this member joined the server they belong to.
        boosting_since:
            When the member started boosting the server.
        deaf:
            If this member is deafened in the current voice channel.
        mute:
            If this member is muted in the current voice channel.
        pending:
            Whether the user has passed the server's membership screening requirements.
        permissions:
            Total permissions of the member in the channel, including overwrites, returned when in the Interaction object.
        timeout:
            When the user's timeout will expire and the user will be able to communicate in the server again.
    """

    guild_id : Snowflake = Field(exclude = True)
    user : User
    avatar : Optional[MEMBER_ICON_ASSET]
    nickname : Optional[str] = Field(None, alias = "nick")
    roles : List[Snowflake]
    joined_at : Optional[datetime]
    boosting_since : Optional[datetime] = Field(None, alias = "premium_since")
    deaf : Optional[bool] = None
    mute : Optional[bool] = None
    pending : bool = False
    permissions : Optional[Permissions] = None
    timeout : Optional[datetime] = Field(None, alias = "communication_disabled_until")

    @classmethod
    def from_object(cls, obj : hikari.Member):
        return cls(
            guild_id = obj.guild_id,
            user = User.from_object(obj.user),
            avatar = obj.guild_avatar_hash,
            nickname = obj.nickname,
            roles = obj.role_ids,
            joined_at = obj.joined_at,
            boosting_since = obj.premium_since,
            deaf = obj.is_deaf,
            mute = obj.is_mute,
            # In GUILD_ events, pending will always be included as true or false. 
            # In non GUILD_ events which can only be triggered by non-pending users, pending will not be included.
            pending = obj.is_pending or True,
            timeout = obj.communication_disabled_until()
        )


# Link to docs:
# https://discord.com/developers/docs/resources/guild#ban-object
class Ban(Model):
    """
    Represents a ban in server.

    Attributes:
        reason:
            The reason of the ban.
        user:
            The banned [User](entities#user).
    """

    user : User
    reason : Optional[str]

    @classmethod
    def from_object(cls, obj : hikari.GuildBan):
        return cls(
            user = User.from_object(obj.user),
            reason = obj.reason
        )


# Link to docs:
# https://discord.com/developers/docs/resources/emoji#emoji-object
class Emoji(Model):
    """
    Represents a emoji.

    !!! warning "Warning"
        Discord will not provide information on whether these emojis are
        animated or not when a reaction is removed and an event is fired. This
        is problematic if you need to try and determine the emoji that was
        removed. The side effect of this means that mentions for animated emojis
        will not be correct.

    Attributes:
        id:
            The ID of this entity. It will be `None` for non-custom emojis.
        name:
            Name of the emoji.
        is_animated:
            Whether this emoji is animated.
        is_unicode:
            Whether this emoji is a unicode emoji.
    """

    id : Optional[Snowflake] = None
    name : str
    is_animated : bool = Field(False, alias = "animated")
    is_unicode : bool = Field(False, alias = "unicode")

    @classmethod
    def parse_emoji(cls, emoji : str) -> "Emoji":
        parsed = emoji.strip("<>").replace(":", " ").strip().replace(" ", ":")
        if not parsed:
            raise ValueError("Not a valid emoji.")
        if parsed.count(":") == 0:
            # Learn if emoji is a unicode or represented as emoji name.
            chars = ascii_lowercase + digits + "_"
            is_unicode = any((x for x in parsed if x not in chars))
            return cls(id = None, name = parsed, is_animated = False, is_unicode = is_unicode)
        elif parsed.count(":") == 1:
            name, id = parsed.split(":")
            return cls(id = id or None, name = name.removeprefix("a_"), is_animated = name.startswith("a_"), is_unicode = False)
        raise ValueError("Not a valid emoji.")

    @property
    def mention(self) -> str:
        if self.id:
            return "<:" + ("a_" if self.is_animated else "") + self.name + ":" + self.id + ">"
        return (":" + self.name + ":") if not self.is_unicode else self.name

    @classmethod
    def from_object(cls, obj : hikari.Emoji):
        return cls.parse_emoji(obj.mention)

    def to_object(self):
        if self.id:
            return hikari.CustomEmoji(id = self.id, name = self.name, is_animated = self.is_animated)
        return hikari.UnicodeEmoji(self.name)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "animated": self.is_animated}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, Emoji):
            return v
        return cls.parse_emoji(v)


# Link to docs:
# https://discord.com/developers/docs/resources/channel#reaction-object
class Reaction(Model):
    """
    Represents a reaction in a message.

    Attributes:
        count:
            Times this emoji has been used to react.
        me:
            If Relay reacted using this emoji.
        emoji:
            The [Emoji](entities#emoji) object.
    """

    count : int
    me : bool
    emoji : Emoji

    @classmethod
    def from_object(cls, obj : hikari.Reaction):
        return cls(
            count = obj.count,
            me = obj.is_me,
            emoji = Emoji.from_object(obj.emoji)
        )


# Link to docs:
# https://discord.com/developers/docs/interactions/receiving-and-responding#message-interaction-object-message-interaction-structure
class MessageInteraction(Model):
    guild_id : Snowflake = Field(exclude = True)
    id : Snowflake
    type : int
    name : str
    user : User
    # TODO: Include member properties.


# Link to docs:
# https://discord.com/developers/docs/resources/channel#message-object
class Message(Model):
    """
    Represents a sent message.

    Attributes:
        id:
            The ID of the entity.
        channel:
            Represents a channel in a server.
        author:
            The author of this message as [User](entities#user){ target="_blank" } object. (not guaranteed to be a valid user)
        member:
            Member properties for this message's author.
        content:
            Contents of the message.
        timestamp:
            When this message was sent.
        edited_timestamp:
            When this message was edited (or `None` if never).
        embeds:
            List of [Embed](entities#embed){ target="_blank" } objects.
        reactions:
            List of [Reaction](entities#reaction){ target="_blank" } objects.
        mention_everyone:
            Whether this message mentions @everyone.
        mention_roles:
            Role IDs specifically mentioned in this message.
        mentions:
            Users specifically mentioned in the message.
        pinned:
            Whether this message is pinned.
        interaction:
            An [MessageInteraction](entities#message-interaction){ target="_blank" } object if the message is a response to an interaction.
    """

    guild_id : Snowflake = Field(exclude = True)
    id : Snowflake
    channel : Channel
    author : User
    member : Optional[Member]
    content : Optional[str]
    timestamp : datetime
    edited_timestamp : Optional[datetime] = None
    embeds : List[Embed]
    reactions : List[Reaction] = []
    # TODO: Maybe use Mentions object here instead of defining new attributes?
    mention_everyone : bool = False
    mention_roles : List[Snowflake]
    mentions : Any
    # TODO: Mentions gives lists and sometimes dictionary, it is currently better to mark as "Any" until the reason has discovered.
    pinned : bool
    interaction : Optional[MessageInteraction] = None

    @validator("interaction", pre = True)
    def create_interaction(cls, v, values):
        if v == None:
            return None
        if isinstance(v, dict):
            return MessageInteraction(guild_id = values["guild_id"], **v)
        return v

    @validator("member", pre = True)
    def create_member(cls, v, values):
        # If member properties has provided, create Member from message user.
        if isinstance(v, dict):
            return Member(guild_id = values["guild_id"], user = values["author"], **v)
        return v

    @classmethod
    def from_object(cls, obj : hikari.Message):
        ch : hikari.GuildChannel = obj.app.cache.get_guild_channel(obj.channel_id)
        return cls(
            guild_id = obj.guild_id or ch.guild_id,
            id = obj.id,
            channel = Channel.from_object(ch),
            author = User.from_object(obj.author),
            member = None if obj.member == None else Member.from_object(obj.member),
            content = obj.content,
            timestamp = obj.timestamp,
            edited_timestamp = obj.edited_timestamp,
            embeds = [Embed.from_object(x) for x in obj.embeds],
            reactions = [Reaction.from_object(x) for x in obj.reactions],
            mention_everyone = obj.mentions.everyone,
            mention_roles = obj.mentions.role_ids or [],
            mentions = obj.mentions.user_ids or [],
            pinned = obj.is_pinned
        )


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#component-object-component-structure
class Component(Model):
    _export_options = [ModelExportOptions.EXCLUDE_NONE]
    _type : int

    def add_object(self, row : ActionRowBuilder):
        raise NotImplementedError("Component not implemented.")

    def to_dict(self):
        return {**super().to_dict(), "type": self._type}


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#select-menu-object-select-option-structure
class SelectOption(Component):
    _export_options = [ModelExportOptions.EXCLUDE_NONE]
    label : str
    value : str
    description : Optional[str] = None
    emoji : Optional[Emoji] = None
    default : bool = False


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#button-object-button-structure
class Button(Component):
    """
    Buttons are interactive components that render on messages. 
    They can be clicked by users, and send an interaction to your Action when clicked.
    """
    _type : int = 2
    custom_id : Optional[str] = None
    label : Optional[str] = None
    style : ButtonStyle = ButtonStyle.PRIMARY.value
    emoji : Optional[Emoji] = None
    url : Optional[str] = None
    disabled : bool = False

    def add_object(self, row : ActionRowBuilder):
        btn = row.add_button(self.style, self.url if self.style == ButtonStyle.LINK.value else self.custom_id)
        btn.set_is_disabled(self.disabled)
        if self.label: btn.set_label(self.label)
        if self.emoji: btn.set_emoji(self.emoji.to_object())
        btn.add_to_container()


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#select-menu-object-select-menu-structure
class Select(Component):
    """
    Select menus are another interactive component that renders on messages. 
    On desktop, clicking on a select menu opens a dropdown-style UI; on mobile, 
    tapping a select menu opens up a half-sheet with the options.
    """
    _type : int = 3
    custom_id : str
    options : conlist(SelectOption, max_items = 25)
    placeholder : Optional[constr(max_length = 100)] = None
    min_values : conint(ge = 0, le = 25) = 1
    max_values : conint(ge = 0, le = 25) = 1
    disabled : bool = False

    def add_object(self, row : ActionRowBuilder):
        cmp = row.add_select_menu(self.custom_id)
        cmp.set_is_disabled(self.disabled)
        if self.placeholder: cmp.set_placeholder(self.placeholder)
        if self.max_values: cmp.set_max_values(self.max_values)
        if self.min_values: cmp.set_min_values(self.min_values)
        for o in self.options:
            opt = cmp.add_option(o.label, o.value)
            opt.set_is_default(o.default)
            if o.emoji: opt.set_emoji(o.emoji.to_object())
            if o.description: opt.set_description(o.description)
            opt.add_to_menu()
        cmp.add_to_container()


# Link to docs:
# https://discord.com/developers/docs/interactions/message-components#text-inputs-text-input-structure
class TextInput(Component):
    """
    Text inputs. They can be only used in Modals right now.
    """
    _type : int = 4
    custom_id : str
    label : str
    style : TextInputStyle = TextInputStyle.SHORT.value
    min_length : Optional[conint(ge = 0, le = 4000)] = None
    max_length : Optional[conint(ge = 1, le = 4000)] = None
    required : bool = True
    value : Optional[constr(max_length = 4000)] = None
    placeholder : Optional[constr(max_length = 4000)] = None

    def add_object(self, row : ActionRowBuilder):
        # TODO: Wait hikari to add their own text input methods.
        raise Exception("TextInputs are not ready yet!")


ActionRow = Literal["ROW"]
ComponentType = Union[Button, Select, ActionRow]
ComponentStore = Union[List[ComponentType], None, ComponentType]

# Modals can only have text inputs at the moment, so they have own type.
ModalComponentType = Union[TextInput, ActionRow]
ModalComponentStore = Union[List[ModalComponentType], None, ModalComponentType]


class Components(Model):
    """
    A class that allows to create hikari's own Message Components but as a pydantic model.
    Unlike Discord and hikari, we don't have ActionRows, instead we use "ROW" string value to add components to new line. 
    This allows us to create components in simplier and more readable way without dealing with nested lists.

    [Button1, "ROW", Button2, Button3] -> ActionRow(Button1), ActionRow(Button2, Button3)
    """
    __root__ : ComponentStore

    def to_object(self):
        rows : List[ActionRowBuilder] = []
        if not self.__root__:
            return None
        rows.append(ActionRowBuilder())
        # If value is a single item instead of a list, then add it directly to list.
        if isinstance(self.__root__, Component):
            self.__root__.add_object(rows[-1])
            return rows
        # If value is a list, loop items and add them to components.
        for comp in self.__root__:
            if comp == "ROW":
                rows.append(ActionRowBuilder())
                continue
            comp.add_object(rows[-1])
        # If there are empty rows, delete them.
        for item in rows.copy():
            if len(item.components) == 0:
                rows.remove(item)
        return rows

    def to_dict(self):
        rows : List[Dict] = []
        if not self.__root__:
            return []
        rows.append({"type": 1, "components": []})
        # If value is a single item instead of a list, then add it directly to list.
        if isinstance(self.__root__, Component):
            rows[-1]["components"].append(self.__root__.to_dict())
            return rows
        # If value is a list, loop items and add them to components.
        for comp in self.__root__:
            if comp == "ROW":
                rows.append({"type": 1, "components": []})
                continue
            rows[-1]["components"].append(comp.to_dict())
        # If there are empty rows, delete them.
        for item in rows.copy():
            if len(item["components"]) == 0:
                rows.remove(item)
        return rows

    @staticmethod
    def build(components : ComponentStore) -> Optional[List[ActionRowBuilder]]:
        """
        A shortcut method that creates an instance of this class and converts to hikari's own components.
        """
        return Components(__root__ = components).to_object()


class ModalComponents(Components):
    """
    Same as Components, but for Modals as they only support text inputs.
    """
    __root__ : ModalComponentStore


# Link to docs:
# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-resolved-data-structure
class Resolved(Model):
    members : Dict[Snowflake, Member] = {}
    roles : Dict[Snowflake, Role] = {}
    # TODO: Add "channels" and "messages".

    @root_validator(pre = True)
    def add_users_to_members(cls, values):
        if "guild_id" not in values:
            raise ValueError("Resolved model requires guild_id for providing Members.")
        resolved = {}
        # Merge members with users.
        if "member" in values:
            resolved["members"] = {}
            for k, v in values.get("member", {}).items():
                resolved["members"][k] = Member(
                    guild_id = resolved["guild_id"],
                    user = resolved["users"][k], 
                    **v
                )
        if "roles" in values:
            resolved["roles"] = values["roles"]
        return resolved


# Link to docs:
# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-data-structure
class InteractionDataCommand(Model):
    id : Snowflake
    name : str
    type : int
    resolved : Optional[Resolved] = None
    options : Optional[Dict[str, Any]] = None
    target_id : Optional[Snowflake] = None

    @validator("options", pre = True)
    def create_options(cls, v):
        if v == None:
            return None
        return {x["name"] : x for x in v}

class InteractionDataComponent(Model):
    custom_id : str
    component_type : int
    values : Optional[List[Any]] = None

class InteractionDataModal(Model):
    custom_id : str
    # TODO: Change Dict type to Component.
    components : List[Dict] = []


# Link to docs:
# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-structure
class Interaction(Model):
    """
    An Interaction is the message that Relay receives when a user uses an application command or a message component.
    
    !!! note "Interaction tokens are handled automatically."
        Interaction objects also have a hidden `token` field that not readable by users which is used for responding the interactions, 
        but you won't need that as Relay sets the `token` automatically for you in Interaction blocks.

    Attributes:
        id:
            ID of the interaction.
        application_id:
            ID of the application this interaction is for.
        type:
            The type of interaction.
        data:
            The command data payload.
        guild_id:
            The guild it was sent from.
        member:
            Guild member data for the invoking user.
        channel:
            The channel that the interaction invoked in.
        message:
            For components, the message they were attached to.
        locale:
            The selected language of the invoking user. This is available on all interaction types except PING.
        server_locale:
            The guild's preferred locale, if invoked in a guild.
    """

    id : Snowflake
    application_id : Snowflake = Field(exclude = True)
    type : InteractionType
    guild_id : Snowflake = Field(exclude = True)
    data : Union[None, InteractionDataModal, InteractionDataCommand, InteractionDataComponent] = None
    member : Member
    channel : Channel
    message : Optional[Message] = None
    locale : Optional[str] = None
    server_locale : str = Field(alias = "guild_locale")
    # This is not included in dictionary output because we are not sure if showing interaction tokens to users
    # causes unwanted access to other servers. Also, Relay already sets the token when responding to interactions.
    # Users won't even need that.
    token : str = Field(exclude = True)
    version : int = Field(exclude = True)

    @validator("member", pre = True)
    def create_member(cls, v, values):
        return Member(guild_id = values["guild_id"], **v)

    @validator("message", pre = True)
    def create_message(cls, v, values):
        if v:
            return Message(guild_id = values["guild_id"], channel = values["channel"], **v)

    @validator("data", pre = True)
    def create_data(cls, v, values):
        if values["type"] == InteractionType.APPLICATION_COMMAND.value:
            d = v
            if "resolved" in d:
                d["resolved"]["guild_id"] = values["guild_id"]
            return InteractionDataCommand(**d)
        elif values["type"] == InteractionType.MODAL_SUBMIT.value:
            return InteractionDataModal(**v)
        elif values["type"] == InteractionType.MESSAGE_COMPONENT.value:
            return InteractionDataComponent(**v)
        # From Discord docs:
        # `data` is always present on application command and message component interaction types. 
        # It is optional for future-proofing against new interaction types.
        if v == None:
            return None
        raise ValueError("Invalid data.")
