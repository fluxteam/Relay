from datetime import datetime
from typing import Any, Callable, Dict, Literal, Tuple, Optional, List, Type
from relay.classes import Events
from relay.enums import InteractionType
from relay.models import Channel, Model, Member, Snowflake, Message, Emoji, Interaction, User
from pydantic import validator, Field
import hikari

# Link to docs:
# https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events
class Listener:
    _check_me : Optional[Callable] = None
    _cachers : List[Tuple[str, str, str, bool]] = []
    _event : Events = None

    def check_listener(self, type : str, content : Any, event : str, workflow : str) -> bool:
        return event == self._event.value

    def event_author(self):
        return None

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        return payload

    @classmethod
    def after_payload(cls, payload : Dict) -> Dict:
        return payload

    @classmethod
    def from_payload(cls, bot : hikari.GatewayBot, payload : Dict):
        pyld = cls.before_payload(payload)
        cache = bot._cache
        # Check for cachers.
        for from_, to, type_, required in cls._cachers:
            obj = None
            if type_ == "CHANNEL":
                obj = cache.get_guild_channel(pyld[from_])
                if obj: obj = Channel.from_object(obj)
            elif type_ == "MESSAGE":
                obj = cache.get_message(pyld[from_])
                if obj: obj = Message.from_object(obj)
            elif type_ == "LIST_MESSAGE":
                obj = []
                for i in pyld[from_]:
                    x = cache.get_message(i)
                    if x:
                        obj.append(Message.from_object(x))
            if required and (obj == None):
                return None
            # Parse key path
            # TODO: Better key path.
            key_path = to.split(".")
            if len(key_path) > 2: 
                raise ValueError("Key path is not supported for keys longer than 2 levels.")
            elif len(key_path) == 2:
                pyld[key_path[0]][key_path[1]] = obj
            else:
                pyld[key_path[0]] = obj
        return cls(**cls.after_payload(pyld))

    @classmethod
    def add_cacher(cls, metadata) -> None:
        cls._cachers = [*cls._cachers, metadata]


class ListenerBase(Model, Listener):
    """
    A listener model.
    """
    class Config:
        extra = "ignore"

    guild_id : Snowflake = Field(exclude = True)


class Event:
    __events__ : Dict[str, Tuple[Events, Type["ListenerBase"]]] = {}

    @staticmethod
    def listener(
        event : Optional[Events] = None, 
        name : Optional[str] = None, 
        /
    ) -> "Event":
        def prefilled(model):
            model._event = event
            Event.__events__[name] = (event, model, )
            return model
        return prefilled

    @staticmethod
    def add_cache(from_ : str, to : str, type_ : Literal["CHANNEL", "USER"], required : bool = True):
        def prefilled(model):
            model.add_cacher((from_, to or from_, type_, required, ))
            return model
        return prefilled

    @staticmethod
    def get(name : Optional[str]) -> Tuple[bool, Optional[Events], Optional[ListenerBase]]:
        event = Event.__events__.get(name, (None, None, ))
        return (bool(event[0]), event[0], event[1],)


# Relay listeners are defined here.
# When you define a valid class, it will be automatically registered as listener for Relay and 
# will be made available for users.
# Every class must:
#    - Subclass "ListenerBase".
#
#    - Call @Event.listener as last decorator. 
#      It takes two parameters, one is for Relay's own event enum and second is for Discord's own event name.
#      Discord's own event names can be found here:
#      https://discord.com/developers/docs/topics/gateway#list-of-intents


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-create
@Event.listener(Events.MESSAGE_SEND, "MESSAGE_CREATE")
@Event.add_cache("channel_id", "message.channel", "CHANNEL")
class MessageSend(ListenerBase):
    """
    Called when message has sent.

    Attributes:
        message:
            Created [Message](entities#message){ target="_blank" } object.
    """

    message : Message
    
    def event_author(self) -> Snowflake:
        return self.message.author.id

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        payload["message"] = payload
        return payload


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-update
@Event.listener(Events.MESSAGE_EDIT, "MESSAGE_UPDATE")
@Event.add_cache("channel_id", "channel", "CHANNEL")
@Event.add_cache("id", "message", "MESSAGE", required = False)
class MessageUpdate(ListenerBase):
    """
    Called when message has edited.

    Attributes:
        id:
            ID of the message.
        channel:
            Channel that this message updated in.
        message:
            Edited [Message](entities#message){ target="_blank" } object.
    """

    id : Snowflake
    channel : Channel
    message : Optional[Message]
    
    def event_author(self) -> Optional[Snowflake]:
        return None if not self.message else self.message.author.id


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-delete
@Event.listener(Events.MESSAGE_DELETE, "MESSAGE_DELETE")
@Event.add_cache("channel_id", "channel", "CHANNEL")
@Event.add_cache("id", "message", "MESSAGE", required = False)
class MessageDelete(ListenerBase):
    """
    Called when a message is deleted. Due to limitations, it doesn't contain the deleted message content always.
    If message is found in internal cache, you can access it with `message` key.
    Message might not be in cache if the message is too old or the Relay is participating in high traffic guilds.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        id:
            The ID of the message.
        channel:
            The [Channel](entities#channel){ target="_blank" } that this message deleted in.
        message:
            The cached message. Note that it may be `None` if message is not in the cache.
    """

    id : Snowflake
    channel : Channel
    message : Optional[Message]

    def event_author(self) -> Optional[Snowflake]:
        return None if not self.message else self.message.author.id


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-delete-bulk
@Event.listener(Events.MESSAGE_DELETE_BULK, "MESSAGE_DELETE_BULK")
@Event.add_cache("channel_id", "channel", "CHANNEL")
@Event.add_cache("ids", "messages", "LIST_MESSAGE")
class MessageDeleteBulk(ListenerBase):
    """
    Called when messages are bulk deleted. Due to limitations, it doesn't contain the deleted messages' content always.
    If messages is found in internal cache, you can access it with `messages` key.
    Messages might not be in cache if the message is too old or the Relay is participating in high traffic guilds.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        ids:
            IDs of the deleted messages.
        channel:
            The [Channel](entities#channel){ target="_blank" } that messages deleted in.
        messages:
            List of cached [Message](entities#message) objects.
    """

    ids : List[Snowflake]
    channel : Channel
    messages : List[Message]


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-reaction-add
@Event.listener(Events.REACTION_ADD, "MESSAGE_REACTION_ADD")
@Event.add_cache("channel_id", "channel", "CHANNEL", required = True)
@Event.add_cache("message_id", "message", "MESSAGE", required = True)
class ReactionAdd(ListenerBase):
    """
    Called when an reaction has been added to a message.

    Attributes:
        member:
            [Member](entities#member){ target="_blank" } object
        channel:
            The [Channel](entities#channel){ target="_blank" } that message belongs to.
        channel_id:
            ID of the channel.
        message:
            [Message](entities#message){ target="_blank" } object that this reaction made for. If message not found in cache, it will be None.
        message_id:
            ID of the message.
        emoji:
            The reacted emoji.
    """

    member : Member
    channel : Channel
    channel_id : Snowflake
    message : Message
    message_id : Snowflake
    emoji : Emoji

    def event_author(self) -> Snowflake:
        return self.member.user.id

    @validator("member", pre = True)
    def create_member(cls, v, values):
        return Member(guild_id = values["guild_id"], **v)

    @validator("emoji", pre = True)
    def create_emoji(cls, v):
        if "id" in v:
            return Emoji.parse_emoji(f"<:{v['name'] or ''}:{v['id'] or ''}>")
        else:
            return Emoji.parse_emoji(v["name"])


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-reaction-remove
@Event.listener(Events.REACTION_REMOVE, "MESSAGE_REACTION_REMOVE")
@Event.add_cache("channel_id", "channel", "CHANNEL", required = True)
@Event.add_cache("message_id", "message", "MESSAGE", required = True)
class ReactionRemove(ListenerBase):
    """
    Called when an reaction has been removed from a message.

    Attributes:
        user_id:
            ID of the user who removed their reaction.
        channel:
            The [Channel](entities#channel){ target="_blank" } that message belongs to.
        channel_id:
            ID of the channel.
        message:
            [Message](entities#message){ target="_blank" } object that this reaction removed from. If message not found in cache, it will be None.
        message_id:
            ID of the message.
    """

    user_id : Snowflake
    channel : Channel
    channel_id : Snowflake
    message : Message
    message_id : Snowflake
    emoji : Optional[Emoji]

    def event_author(self) -> Snowflake:
        return self.user_id

    @validator("emoji", pre = True)
    def create_emoji(cls, v):
        if "id" in v:
            return Emoji.parse_emoji(f"<:{v['name'] or ''}:{v['id'] or ''}>")
        else:
            return Emoji.parse_emoji(v["name"])


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-reaction-remove-emoji
@Event.listener(Events.REACTION_REMOVE_EMOJI, "MESSAGE_REACTION_REMOVE_EMOJI")
@Event.add_cache("channel_id", "channel", "CHANNEL", required = False)
@Event.add_cache("message_id", "message", "MESSAGE", required = False)
class ReactionRemoveEmoji(ListenerBase):
    """
    Called when all reactions for a emoji has been removed from a message.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        channel:
            The [Channel](entities#channel){ target="_blank" } that message belongs to.
        channel_id:
            ID of the channel.
        message:
            [Message](entities#message){ target="_blank" } object that this reaction removed from. If message not found in cache, it will be None.
        message_id:
            ID of the message.
        emoji:
            [Emoji](entities#emoji){ target="_blank" } object.
    """

    channel : Channel
    channel_id : Snowflake
    message : Message
    message_id : Snowflake
    emoji : Optional[Emoji]

    @validator("emoji", pre = True)
    def create_emoji(cls, v):
        if "id" in v:
            return Emoji.parse_emoji(f"<:{v['name'] or ''}:{v['id'] or ''}>")
        else:
            return Emoji.parse_emoji(v["name"])


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#message-reaction-remove-all
@Event.listener(Events.REACTION_REMOVE_ALL, "MESSAGE_REACTION_REMOVE_ALL")
@Event.add_cache("channel_id", "channel", "CHANNEL", required = False)
@Event.add_cache("message_id", "message", "MESSAGE", required = False)
class ReactionRemoveAll(ListenerBase):
    """
    Called when all reactions has been removed from a message.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        channel:
            The [Channel](entities#channel){ target="_blank" } that message belongs to.
        channel_id:
            ID of the channel.
        message:
            [Message](entities#message){ target="_blank" } object that this reaction removed from. If message not found in cache, it will be None.
        message_id:
            ID of the message.
    """

    channel : Channel
    channel_id : Snowflake
    message : Message
    message_id : Snowflake


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#channel-create
@Event.listener(Events.CHANNEL_CREATE, "CHANNEL_CREATE")
class ChannelCreate(ListenerBase):
    """
    Called when a channel has created.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        channel:
            The created [Channel](entities#channel){ target="_blank" }.
    """

    channel : Channel

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        payload["channel"] = payload
        return payload


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#channel-update
@Event.listener(Events.CHANNEL_UPDATE, "CHANNEL_UPDATE")
class ChannelUpdate(ListenerBase):
    """
    Called when a channel has updated.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        channel:
            The created [Channel](entities#channel){ target="_blank" }.
    """

    channel : Channel

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        payload["channel"] = payload
        return payload


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#channel-delete
@Event.listener(Events.CHANNEL_DELETE, "CHANNEL_DELETE")
class ChannelDelete(ListenerBase):
    """
    Called when a channel has deleted.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        channel:
            The related [Channel](entities#channel){ target="_blank" }.
    """

    channel : Channel

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        payload["channel"] = payload
        return payload


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#channel-pins-update
@Event.listener(Events.CHANNEL_PINS_UPDATE, "CHANNEL_PINS_UPDATE")
@Event.add_cache("channel_id", "channel", "CHANNEL")
class ChannelPinsUpdate(ListenerBase):
    """
    Called when a message is pinned or unpinned in a text channel. This is not sent when a pinned message is deleted.

    !!! warning "If this event triggered by Relay, it won't be ignored."
        That's because this incoming event from Discord doesn't include who did the action,
        so it is not possible to know who triggered this event. So if Relay triggers this event,
        your action that listens for this event will be executed.

    Attributes:
        channel:
            The related [Channel](entities#channel){ target="_blank" }.
        last_pin_timestamp:
            The time at which the most recent pinned message was pinned.
    """

    channel : Channel
    last_pin_timestamp : Optional[datetime] = None


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#guild-member-add
@Event.listener(Events.MEMBER_JOIN, "GUILD_MEMBER_ADD")
class MemberJoin(ListenerBase):
    """
    Called when a member joined to server.

    Attributes:
        member:
            The related [Member](entities#member){ target="_blank" }.
    """

    member : Member

    def event_author(self) -> Snowflake:
        return self.member.user.id

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        payload["member"] = payload
        return payload


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#guild-member-remove
@Event.listener(Events.MEMBER_REMOVE, "GUILD_MEMBER_REMOVE")
class MemberRemove(ListenerBase):
    """
    Called when a user is removed from a server (leave/kick/ban).

    Attributes:
        user:
            The related [User](entities#user){ target="_blank" }.
    """

    user : User

    def event_author(self) -> Snowflake:
        return self.user.id


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#guild-ban-add
@Event.listener(Events.MEMBER_BAN, "GUILD_BAN_ADD")
class MemberBan(ListenerBase):
    """
    Called when a user is banned from a server.

    Attributes:
        user:
            The related [User](entities#user){ target="_blank" }.
    """

    user : User

    def event_author(self) -> Snowflake:
        return self.user.id


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#guild-ban-remove
@Event.listener(Events.MEMBER_UNBAN, "GUILD_BAN_REMOVE")
class MemberUnban(ListenerBase):
    """
    Called when a user is unbanned from a server.

    Attributes:
        user:
            The related [User](entities#user){ target="_blank" }.
    """

    user : User

    def event_author(self) -> Snowflake:
        return self.user.id


# Link to docs:
# https://discord.com/developers/docs/topics/gateway#interaction-create
@Event.listener(Events.INTERACTION_CREATE, "INTERACTION_CREATE")
@Event.add_cache("channel_id", "interaction.channel", "CHANNEL")
class InteractionCreate(ListenerBase):
    """
    Sent when a user in a server uses an Application Command.

    Attributes:
        interaction:
            The interaction object.
    """

    interaction : Interaction

    def event_author(self) -> Snowflake:
        return self.interaction.member.user.id

    @classmethod
    def before_payload(cls, payload : Dict) -> Dict:
        payload["interaction"] = payload
        return payload

    def check_listener(self, type: str, content: Any, event: str, workflow: str) -> bool:
        t = self.interaction.type
        # All Interaction listeners must have "NONE" event.
        if event != "NONE":
            return False
        # Actions that listens interactions doesn't listen for INTERACTION_CREATE events directly,
        # instead they have a "type" and "content" to determine which command to run for.
        # Application Commands checks if interaction ID is same with Actions content.
        if (type in ["SLASH", "CONTEXT"]) and (t == InteractionType.APPLICATION_COMMAND.value):
            if str(content) == str(self.interaction.data.id):
                return True
        # Modal listeners needs to have same ID with interaction's custom_id.
        elif (type == "MODAL") and (t == InteractionType.MODAL_SUBMIT.value):
            if str(content) == str(self.interaction.data.custom_id):
                return True
        # And for Message Components, we check if the command name equals with
        # Actions content.
        elif (type == "COMPONENT") and (t == InteractionType.MESSAGE_COMPONENT.value):
            msg = self.interaction.message
            if msg:
                if str(content) == msg.interaction.name:
                    return True
        return False


@Event.listener(Events.PACKAGE_INSTALL, "PACKAGE_INSTALL")
class PackageInstall(ListenerBase):
    """
    Called when a Relay Package has installed to server.

    !!! error "This event can't be used for Actions"
        This is a non-Discord event made for Relay itself. It is used for communication between dashboard and bot, so users currently
        can't run actions when this event happens.

    Attributes:
        pack_code:
            ID of the installed package.
        pack_version:
            Version name of the installed package.
        user_id:
            ID of the user who installed the package, this comes from current authenticated user in Relay Web.
        data:
            Dictionary of package parameters.
    """

    pack_code : str
    pack_version : str
    user : Snowflake = Field(alias = "user_id")
    data : Dict

    def event_author(self) -> Snowflake:
        return self.user


@Event.listener(Events.WEBHOOK, "WEBHOOK")
class Webhook(ListenerBase):
    """
    Called when a [Relay webhook](../../actions#webhook){ target="_blank" } has executed. 

    Attributes:
        data:
            The request body as dictionary.
    """

    action_id : str = Field(exclude = True)
    data : Dict

    def check_listener(self, type: str, content: Any, event: str, workflow: str) -> bool:
        # Webhook listeners can only run for its associated actions,
        # even if there are multiple Webhook listeners.
        if super().check_listener(type, content, event, workflow):
            if workflow == self.action_id:
                return True
        return False
