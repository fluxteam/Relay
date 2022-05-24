from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from hikari.impl.rest import RESTClientImpl
from hikari import UNDEFINED, Guild, GuildTextChannel, ResponseType, InteractionType
from pyconduit import Category
from pyconduit import block
from pydantic import conint
from relay.classes import DictPayload as sdict
from relay.classes import RelayBot
from relay.models import (
    Ban,
    Components,
    Interaction,
    ModalComponents, 
    Overwrites, 
    Embed, 
    Mentions, 
    Snowflake, 
    ObjectOrSnowflake, 
    Message, 
    EmbedAuthor, 
    Channel, 
    Member, 
    Server,
    Role,
    Permissions,
    Color,
    Emoji,
    ValidChannel,
    ValidMember,
    AdaptiveList
)
from hikari.internal.routes import (
    POST_INTERACTION_RESPONSE
)
from relay.enums import RelayFlags

# DISCORD
# Contains blocks to interact with Discord.
class Discord(Category):
    """
    You can use these Discord blocks to interact Discord API with Relay Actions. Refer to [Relay Actions](../actions)
    to learn how to use them.
    """

    # ----------------------------
    # MESSAGE
    # ----------------------------

    @block
    @staticmethod
    async def message_pin(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel,
        message : ObjectOrSnowflake
    ) -> None:
        """
        Pin a message in a channel. The max pinned messages is 50.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_MESSAGES` permission to perform this action.

        Args:
            message:
                A message ID that will be pinned.
            channel:
                ID of the channel that message placed in.
        """
        await rest__.pin_message(channel = channel, message = message)

    
    @block
    @staticmethod
    async def message_unpin(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel,
        message : ObjectOrSnowflake
    ) -> None:
        """
        Unpin a message in a channel.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_MESSAGES` permission to perform this action.

        Args:
            message:
                A message ID that will be unpinned.
            channel:
                ID of the channel that message placed in.
        """
        await rest__.unpin_message(channel = channel, message = message)


    @block
    @staticmethod
    async def message_delete(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel,
        message : ObjectOrSnowflake
    ) -> None:
        """
        Deletes a message.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_MESSAGES` permission to delete someone's message. Without this permission,
            Relay only can delete its messages.

        Args:
            message:
                A message ID that will be deleted.
            channel:
                ID of the channel that message placed in.
        """
        await rest__.delete_message(channel = channel, message = message)

    
    @block
    @staticmethod
    async def message_bulk_delete(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel,
        messages : List[ObjectOrSnowflake]
    ) -> None:
        """
        Deletes multiple messages in a single request.
        Any message IDs given that do not exist or are invalid will count towards the minimum and maximum message count (currently 2 and 100 respectively).

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_MESSAGES` permission to perform this action.

        !!! quote "Discord API notes"
            You can only delete messages not older than 2 weeks in bulk.
            Discord will raise an error if any message provided is older than that or if any duplicate message IDs are provided.

        Args:
            messages:
                A list of message IDs that will be deleted.
            channel:
                ID of the channel that these messages placed in.
        """
        await rest__.delete_messages(channel = channel, messages = messages)


    @block
    @staticmethod
    async def message_send(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        reply : Optional[ObjectOrSnowflake] = None,
        mentions : Optional[Mentions] = None,
        components : Components = None
    ) -> Message:
        """
        Sends a message to channel.

        !!! example "Limitations apply"
            We don't want to allow anyone to spam through Relay (even if they want to), so you can only
            send one message per event. You can't send more than one messages in a single event.
            [Relay Packages](../packages){ target="_blank" } doesn't have this limitation.

        Args:
            channel:
                ID of the channel that message will be sent in.
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            reply:
                ID of the message that this message will reply to.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
            components:
                List or a single Component object.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        alm = Mentions() if not mentions else mentions
        components = None if not components else components.to_object()
        msg = await rest__.create_message(
            channel = channel, 
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == None else [x.to_object() for x in embed], 
            mentions_everyone = alm.everyone,
            mentions_reply = alm.replied_user,
            user_mentions = alm.users,
            role_mentions = alm.roles,
            reply = reply or UNDEFINED,
            components = components or UNDEFINED
        )
        msg.guild_id = guild__.id
        return Message.from_object(msg).to_dict()
    

    @block(max_uses = 1)
    @staticmethod
    async def message_dm(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        member : ValidMember,
        content : Optional[str] = None,
        reply : Optional[ObjectOrSnowflake] = None,
        mentions : Optional[Mentions] = None
    ) -> Snowflake:
        """
        Sends a message to a member. Member must be in the server. Note that message content is sent in embed to
        show incoming server name and server icon. So it is not possible to send embeds in direct messages.

        !!! example "Limitations apply"
            We don't want to allow anyone to spam through Relay (even if they want to), so you can only
            send one message per event. You can't send more than one messages in a single event.
            [Relay Packages](../packages){ target="_blank" } doesn't have this limitation.

        Args:
            member:
                ID of the member that message will be sent to.
            content:
                Content of the message.
            reply:
                ID of the message that this message will reply to.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.

        Returns:
            ID of the created message.
        """
        _mentions = Mentions() if not mentions else mentions
        channel = await rest__.create_dm_channel(member.id)
        msg = await rest__.create_message(
            channel = channel.id,
            content = UNDEFINED,
            embed = Embed(
                author = EmbedAuthor(
                    icon_url = None if not guild__.icon_url else str(guild__.icon_url), 
                    name = guild__.name
                ),
                description = content or None
            ).to_object(),
            mentions_everyone = _mentions.everyone,
            mentions_reply = _mentions.replied_user,
            user_mentions = _mentions.users,
            role_mentions = _mentions.roles,
            reply = reply or UNDEFINED
        )
        return msg.id


    @block
    @staticmethod
    async def message_edit(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        message : ObjectOrSnowflake,
        channel : ValidChannel,
        content : Optional[str] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None
    ) -> Message:
        """
        Edits a message that posted by Relay before.

        Args:
            message:
                A message ID that will be edited.
            channel:
                ID of the channel that message belongs to.
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embeds:
                A list of [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embeds` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
        """
        _mentions = Mentions() if not mentions else mentions
        return Message.from_object(await rest__.edit_message(
            channel = channel,
            message = message,
            content = content or UNDEFINED,
            embeds = UNDEFINED if embed == None else [x.to_object() for x in embed], 
            mentions_everyone = _mentions.everyone,
            mentions_reply = _mentions.replied_user,
            user_mentions = _mentions.users,
            role_mentions = _mentions.roles
        )).to_dict()

    
    @block
    @staticmethod
    async def message_add_reaction(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        message : ObjectOrSnowflake,
        channel : ValidChannel,
        emoji : Emoji
    ) -> None:
        """
        Adds a reaction to message.

        Args:
            message:
                A message ID that reaction will be added to.
            channel:
                ID of the channel that message belongs to.
            emoji:
                An emoji that will be added as reaction. Emoji can be a custom emoji (in `<:relay:864239476635992134>` format) or a Unicode emoji.
        """
        await rest__.add_reaction(
            channel = channel, 
            message = message, 
            emoji = emoji.to_object()
        )


    @block
    @staticmethod
    async def message_remove_reaction(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        message : ObjectOrSnowflake,
        channel : ValidChannel,
        emoji : Optional[Emoji] = None,
        user : Optional[ObjectOrSnowflake] = UNDEFINED
    ) -> None:
        """
        Removes a reaction from a message. 

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_MESSAGES` permission to delete someone's reaction other than itself.
        
        * If `emoji` has provided and `user` is blank, removes all reactions for the specified emoji.
        * If `emoji` is blank and `user` has provided, raises error.
        * If both `emoji` and `user` has provided, removes the specified user's reaction for the specified emoji.
        * If both `emoji` and `user` is blank, removes all reactions of all emojis.

        Args:
            message:
                A message ID that reaction will be added to.
            channel:
                ID of the channel that message belongs to.
            emoji:
                An emoji of the reaction that will be removed from message. Emoji can be a custom emoji (in `<:relay:864239476635992134>` format) or a Unicode emoji.
                Set it to `None` to delete all emojis.
            user:
                ID of the user that reaction will be removed from. Set it to `None` to delete all reactions. Don't set a value if you want to
                remove Relay's own reactions.
        """
        if (not emoji) and (user != None):
            raise ValueError("Invalid operation, emoji is None but user is not.")
        # Delete Relay's own reaction.
        elif emoji and (user == UNDEFINED):
            await rest__.delete_my_reaction(channel = channel, message = message, emoji = emoji.to_object())
        # Delete emoji from reaction.
        elif emoji and (user == None):
            await rest__.delete_all_reactions_for_emoji(channel = channel, message = message, emoji = emoji.to_object())
        # Delete emoji from reaction of a user.
        elif emoji and user:
            await rest__.delete_reaction(channel = channel, message = message, user = user, emoji = emoji.to_object())
        # Delete all reactions.
        elif (not emoji) and (user == None):
            await rest__.delete_all_reactions(channel = channel, message = message)

    
    @block
    @staticmethod
    async def message_get_reaction(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        message : ObjectOrSnowflake,
        channel : ValidChannel,
        emoji : Emoji,
        limit : conint(ge = 1, le = 100) = 25,
        after : Optional[Snowflake] = None
    ) -> List[Dict]:
        """
        Get a list of [user objects](../api/actions/entities#user){ target="_blank" } that reacted to the message for a specific emoji.
        
        !!! info "TODO"
            This block is under development.

        Args:
            message:
                A message ID that reactions will get from.
            channel:
                ID of the channel that message belongs to.
            emoji:
                An emoji of the reaction. Emoji can be a custom emoji (in `<:relay:864239476635992134>` format) or a Unicode emoji.
            limit:
                Max number of users to return. (1-100)
            after:
                Get users after this user ID.

        Returns:
            A list of user dictionaries.
        """
        raise ValueError("[TODO] This block is not working yet.")

    # ----------------------------
    # CHANNEL
    # ----------------------------

    @block
    @staticmethod
    def channel(
        guild__ : Guild,
        *,
        channel : ValidChannel
    ) -> Channel:
        """
        Gets a [channel object](../api/actions/entities#channel){ target="_blank" } in the server.
        If no channel is found, raises error.

        Args:
            channel:
                ID of the channel.

        Returns:
            A [channel object](../api/actions/entities#channel){ target="_blank" }.
        """
        ch = guild__.get_channel(channel)
        return Channel.from_object(ch).to_dict()

    
    @block
    @staticmethod
    def channels(
        guild__ : Guild
    ) -> Dict[Snowflake, Channel]:
        """
        Gets a mapping of [channel objects](../api/actions/entities#channel){ target="_blank" } in the server.

        Returns:
            A dictionary of [channel objects](../api/actions/entities#channel){ target="_blank" }.
        """
        return { str(x) : Channel.from_object(y).to_dict() for x, y in guild__.get_channels().items() }

    
    @block(tags = [RelayFlags.PACKAGE.value], max_uses = 1)
    @staticmethod
    async def channel_history(
        guild__ : Guild,
        *,
        channel : ValidChannel,
        limit : Optional[int] = 100,
        after : Optional[Snowflake] = None,
        before : Optional[Snowflake] = None,
        around : Optional[Snowflake] = None,
        oldest_first : bool = False
    ) -> List[Message]:
        """
        Lists [message objects](../api/actions/entities#message){ target="_blank" } in a channel.

        !!! info "TODO"
            This block is under development.

        !!! example "Limitations apply"
            To prevent abuse and performance issues, people can't use this block in their own actions.
            [Relay Packages](../packages){ target="_blank" } doesn't have this limitation. However, this block
            can't be called more than one in a single event.

        Args:
            channel:
                ID of the channel.
            limit:
                The number of messages to retrieve. If `None`, retrieves every message in the channel. Note, however, that this would make it a slow operation.
            before:
                Retrieve messages before specified message ID.
            after:
                Retrieve messages after specified message ID.
            around:
                Retrieve messages around specified message ID.
            oldest_first:
                If set to `True`, return messages in oldest -> newest order. Defaults to `True`, otherwise `False`.

        Returns:
            A list of [message objects](../api/actions/entities#message){ target="_blank" }.
        """
        ch : GuildTextChannel = guild__.get_channel(int(channel))
        messages = []
        async for message in ch.fetch_history(
            after = after if after == None else int(after), 
            before = before if before == None else int(before),
            around = around if around == None else int(around)
        ):
            messages.append(Message.from_object(message).to_dict())
        return messages

    
    @block
    @staticmethod
    async def channel_create(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        name : str,
        type : int = 0,
        position : Optional[int] = None,
        topic : Optional[str] = None,
        nsfw : Optional[bool] = None,
        cooldown : Optional[conint(ge = 0, le = 21600)] = None,
        bitrate : Optional[conint(ge = 8, le = 384)] = None,
        user_limit : Optional[conint(ge = 0, le = 99)] = None,
        permissions : Optional[List[Overwrites]] = None,
        category : Optional[ObjectOrSnowflake] = None,
        reason : Optional[str] = None
    ) -> Channel:
        """
        Creates a channel in the server. Note that some values are only available for specific channel types. Such
        as you can't set `bitrate` for text channels. They are only available for voice channels.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_CHANNELS` permission to perform this action.
            Setting `MANAGE_ROLES` permission in channels is only possible for server administrators.

        Args:
            name:
                The name of the channel. Applies to all channel types.
            type (Literal[0, 2, 4, 5, 10, 12, 13]):
                [Type of the channel in integer.](https://discord.com/developers/docs/resources/channel#channel-channel-types){ target="_blank" }
            position:
                The position of the channel in the left-hand listing. Applies to all channel types.
            topic:
                0-1024 character channel topic. Applies only to News and Text channels.
            nsfw:
                Whether the channel is NSFW. Applies only to News, Text, Store channels.
            cooldown:
                Amount of seconds a user has to wait before sending another message (0-21600).
                Bots, as well as users with the permission `MANAGE_MESSAGES` or `MANAGE_CHANNELS` are unaffected.
                Applies only to Text channels.
            bitrate:
                The bitrate (in bits) of the voice channel. The value multipled by 1000 automatically, so if you want
                to set 64 kbps, just set it to "64". Applies only to Voice channels.
            user_limit:
                The user limit of the voice channel; 0 refers to no limit, 1 to 99 refers to a user limit. Applies only to Voice channels.
            permissions:
                List of channel or category-specific [overwrites object](../api/actions/entities#overwrites){ target="_blank" }. Applies to all channel types.
            category:
                ID of the new parent category for a channel. Applies to Text, News, Store, Voice channels.
            reason:
                Reason of performing the action. May show up in the Audit Log.

        Returns:
            ID of the created channel.
        """
        ch = await rest__._create_guild_channel(
            guild = guild__.id,
            type_ = type,
            name = UNDEFINED if name == None else name,
            position = UNDEFINED if position == None else position,
            topic = UNDEFINED if topic == None else topic,
            nsfw = UNDEFINED if nsfw == None else nsfw,
            rate_limit_per_user = UNDEFINED if cooldown == None else cooldown,
            permission_overwrites = UNDEFINED if permissions == None else [x.to_object() for x in permissions],
            bitrate = UNDEFINED if bitrate == None else bitrate,
            user_limit = UNDEFINED if user_limit == None else user_limit,
            category = UNDEFINED if category == None else category,
            reason = reason or UNDEFINED
        )
        return Channel.from_object(ch).to_dict()


    @block
    @staticmethod
    async def channel_edit(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel,
        name : str,
        position : Optional[int] = None,
        topic : Optional[str] = None,
        nsfw : Optional[bool] = None,
        cooldown : Optional[conint(ge = 0, le = 21600)] = None,
        bitrate : Optional[conint(ge = 8, le = 384)] = None,
        user_limit : Optional[conint(ge = 0, le = 99)] = None,
        permissions : Optional[List[Overwrites]] = None,
        category : Optional[ObjectOrSnowflake] = None,
        reason : Optional[str] = None
    ) -> None:
        """
        Edits a channel in the server. Note that some values are only available for specific channel types. Such
        as you can't set `bitrate` for text channels. They are only available for voice channels.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_CHANNELS` permission to perform this action.
            Modifying permissions requires `MANAGE_ROLES` permission additionally.

        Args:
            channel:
                ID of the channel.
            name:
                The new name of the channel. Applies to all channel types.
            position:
                The position of the channel in the left-hand listing. Applies to all channel types.
            topic:
                0-1024 character channel topic. Applies only to News and Text channels.
            nsfw:
                Whether the channel is NSFW. Applies only to News, Text, Store channels.
            cooldown:
                Amount of seconds a user has to wait before sending another message (0-21600).
                Bots, as well as users with the permission `MANAGE_MESSAGES` or `MANAGE_CHANNELS` are unaffected.
                Applies only to Text channels.
            bitrate:
                The bitrate (in bits) of the voice channel. The value multipled by 1000 automatically, so if you want
                to set 64 kbps, just set it to "64". Applies only to Voice channels.
            user_limit:
                The user limit of the voice channel; 0 refers to no limit, 1 to 99 refers to a user limit. Applies only to Voice channels.
            permissions:
                List of channel or category-specific [overwrites object](../api/actions/entities#overwrites){ target="_blank" }. Applies to all channel types.
            category:
                ID of the new parent category for a channel. Applies to Text, News, Store, Voice channels.
            reason:
                Reason of performing the action. May show up in the Audit Log.
        """
        await rest__.edit_channel(
            channel,
            name = UNDEFINED if name == None else name,
            position = UNDEFINED if position == None else position,
            topic = UNDEFINED if topic == None else topic,
            nsfw = UNDEFINED if nsfw == None else nsfw,
            rate_limit_per_user = UNDEFINED if cooldown == None else cooldown,
            permission_overwrites = UNDEFINED if permissions == None else [x.to_object() for x in permissions],
            bitrate = UNDEFINED if bitrate == None else bitrate,
            user_limit = UNDEFINED if user_limit == None else user_limit,
            parent_category = UNDEFINED if category == None else category,
            reason = reason or UNDEFINED
        )

    
    @block
    @staticmethod
    async def channel_delete(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        channel : ValidChannel
    ) -> None:
        """
        Deletes a channel in the server. For Community server, the Rules or Guidelines channel and the Community Updates channel cannot be deleted.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_CHANNELS` permission to perform this action,
            or `MANAGE_THREADS` if the channel is a thread.

        !!! danger "Potentially destructive action"
            Deleting a channel cannot be undone. Use this with caution, as it is impossible to 
            undo this action when performed on a channel.

        Args:
            channel:
                ID of the channel.
        """
        await guild__.delete_channel(channel)

    # ----------------------------
    # MEMBER
    # ----------------------------

    @block
    @staticmethod
    def member(
        guild__ : Guild,
        *,
        member : ObjectOrSnowflake
    ) -> Optional[Member]:
        """
        Gets a [member object](../api/actions/entities#member){ target="_blank" }. You can only get members from the current server.

        Args:
            member:
                ID of the member.

        Returns:
            A [member object](../api/actions/entities#member){ target="_blank" }.
        """
        mb = guild__.get_member(member)
        return None if not mb else Member.from_object(mb).to_dict()

    
    @block
    @staticmethod
    def member_me(
        guild__ : Guild
    ) -> Member:
        """
        Gets a [member object](../api/actions/entities#member){ target="_blank" } for Relay itself.

        Returns:
            A [member object](../api/actions/entities#member){ target="_blank" } of Relay.
        """
        return Member.from_object(guild__.get_my_member()).to_dict()


    @block
    @staticmethod
    async def member_ban(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        member : ObjectOrSnowflake,
        delete_days : Optional[conint(ge = 0, le = 7)],
        reason : Optional[str] = None
    ) -> None:
        """
        Bans a member from server, and optionally delete previous messages sent by the banned member.

        !!! warning "Privileged permission required"
            Relay needs to have `BAN_MEMBERS` permission to perform this action.

        Args:
            member:
                ID of the member.
            delete_days:
                Number of days to delete messages for (0-7).
            reason:
                Reason of performing the action. May show up in the Audit Log.
        """
        await rest__.ban_user(
            guild = guild__.id,
            user = member,
            delete_message_days = delete_days or UNDEFINED,
            reason = reason or UNDEFINED
        )

    
    @block
    @staticmethod
    async def member_unban(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        member : ObjectOrSnowflake,
        reason : Optional[str] = None
    ) -> None:
        """
        Unbans a member from server.

        !!! warning "Privileged permission required"
            Relay needs to have `BAN_MEMBERS` permission to perform this action.

        Args:
            member:
                ID of the member.
            reason:
                Reason of performing the action. May show up in the Audit Log.
        """
        await rest__.unban_user(
            guild = guild__.id,
            user = member,
            reason = reason or UNDEFINED
        )

    
    @block
    @staticmethod
    async def member_kick(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        member : ObjectOrSnowflake,
        reason : Optional[str] = None
    ) -> None:
        """
        Kicks a member from server.

        !!! warning "Privileged permission required"
            Relay needs to have `KICK_MEMBERS` permission to perform this action.

        Args:
            member:
                ID of the member.
            reason:
                Reason of performing the action. May show up in the Audit Log.
        """
        await rest__.kick_user(
            guild = guild__.id,
            user = member,
            reason = reason or UNDEFINED
        )

    
    @block
    @staticmethod
    async def member_edit(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        member : ObjectOrSnowflake,
        nick : Optional[str] = UNDEFINED,
        roles : Union[List[ObjectOrSnowflake], ObjectOrSnowflake, None] = UNDEFINED,
        mute : Optional[bool] = UNDEFINED,
        deaf : Optional[bool] = UNDEFINED,
        voice_channel : Optional[ValidChannel] = UNDEFINED,
        timeout : Optional[datetime] = UNDEFINED
    ) -> None:
        """
        Edits a member in the server.

        !!! warning "Privileged permission required"
            Relay may need to have `MANAGE_NICKNAMES`, `MANAGE_ROLES`, `MUTE_MEMBERS`, `DEAFEN_MEMBERS`, `MOVE_MEMBERS` or/and `MODERATE_MEMBERS`
            permission(s) to perform this action based on given parameters.

        Args:
            member:
                Member to edit.
            nick:
                Changes the nickname of member. If `None`, it will delete the nickname. Don't fill the value if you don't want to override.
            roles:
                A single role or a list of roles for replacing the roles of the member. Don't fill the value if you don't want to override.
            mute:
                Whether the user is muted in voice channels. Don't fill the value if you don't want to override.
            deaf:
                Whether the user is deafened in voice channels. Don't fill the value if you don't want to override.
            voice_channel:
                A voice channel to move the member to. If set to `None`, the member will be disconnected from the voice channel. Don't fill the value if you don't want to override.
            timeout:
                If provided, the datetime when the timeout (disable communication) of the member expires, up to 28 days in the future, or `None` to remove the timeout from the member. Don't fill the value if you don't want to override.
        """
        await rest__.edit_member(
            guild = guild__.id,
            user = member,
            nick = nick,
            roles = \
                UNDEFINED if roles == UNDEFINED else \
                [] if roles == None else \
                roles if isinstance(roles, list) else \
                [roles],
            mute = mute,
            deaf = deaf,
            voice_channel = voice_channel,
            communication_disabled_until = timeout
        )

    # ----------------------------
    # SERVER
    # ----------------------------

    @block
    @staticmethod
    def server(
        guild__ : Guild
    ) -> Server:
        """
        Gets the current [server object](../api/actions/entities#server){ target="_blank" }.

        Returns:
            A [server object](../api/actions/entities#server){ target="_blank" }.
        """
        return Server.from_object(guild__).to_dict()


    @block
    @staticmethod
    async def server_get_ban(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        user : Optional[ObjectOrSnowflake] = None
    ) -> Union[List[Ban], Ban]:
        """
        Gets a [ban objects](../api/actions/entities#ban){ target="_blank" } of specified user.
        If no user has specified, returns a list of all bans of the server.

        !!! warning "Privileged permission required"
            Relay needs to have `BAN_MEMBERS` permission to perform this action.

        Args:
            user:
                ID of the user. Set it to `None` to get all bans.
        """
        if user:
            return Ban.from_object(await rest__.fetch_ban(guild = guild__.id, user = user)).to_dict()
        else:
            bans = []
            for ban in await rest__.fetch_bans(guild_id = guild__.id):
                bans.append(Ban.from_object(ban).to_dict())
            return bans

    
    @block
    @staticmethod
    async def server_get_prune(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        days : Optional[conint(ge = 1, le = 30)] = None,
        roles : Optional[List[ObjectOrSnowflake]] = None
    ) -> int:
        """
        Returns a number of members that would be removed in a prune operation.

        By default, prune will not remove users with roles. You can optionally include specific roles in your prune by providing the `roles` parameter. 
        Any inactive user that has a subset of the provided role(s) will be counted in the prune and users with additional roles will not.

        !!! warning "Privileged permission required"
            Relay needs to have `KICK_MEMBERS` permission to perform this action.

        Args:
            days:
                Number of days to count prune for. (1-30)
            roles:
                List of role IDs that will be included in prune.

        Returns:
            A number of members that would be removed in a prune operation.
        """
        return await rest__.estimate_guild_prune_count(
            guild = guild__.id,
            days = days or UNDEFINED,
            include_roles = UNDEFINED if roles == None else [str(x) for x in roles]
        )

    
    @block
    @staticmethod
    async def server_begin_prune(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        days : Optional[conint(ge = 1, le = 30)] = None,
        roles : Optional[List[ObjectOrSnowflake]] = None,
        compute_prune_count : bool = True,
        reason : Optional[str] = None
    ) -> Optional[int]:
        """
        Begin a prune operation. Returns a number of members that removed in the prune operation.

        By default, prune will not remove users with roles. You can optionally include specific roles in your prune by providing the `roles` parameter. 
        Any inactive user that has a subset of the provided role(s) will be counted in the prune and users with additional roles will not.

        !!! warning "Privileged permission required"
            Relay needs to have `KICK_MEMBERS` permission to perform this action.

        !!! danger "Potentially destructive action"
            "Pruning" is a action that removes inactive members from the server.
            The inactive members are denoted if they have not logged on in specified number of days.

        Args:
            days:
                Number of days to count prune for. (1-30)
            roles:
                List of role IDs that will be included in prune.
            compute_prune_count:
                Whether to compute the prune count. This defaults to `True` which makes it prone to timeouts in very large guilds. 
                In order to prevent timeouts, you must set this to `False`. If this is set to `False`, then this function will always return `None`.
            reason:
                Reason of performing the action. May show up in the Audit Log.

        Returns:
            A number of members that removed in a prune operation. Returns `None` if `compute_prune_count` is `True`.
        """
        return await rest__.begin_guild_prune(
            guild = guild__,
            days = days,
            include_roles = UNDEFINED if roles == None else [str(x) for x in roles],
            compute_prune_count = compute_prune_count,
            reason = reason
        )

    # ----------------------------
    # ROLE
    # ----------------------------

    @block
    @staticmethod
    def role(
        guild__ : Guild,
        *,
        role : ObjectOrSnowflake
    ) -> Role:
        """
        Gets a [role object](../api/actions/entities#role){ target="_blank" } in the server.
        If no role is found, raises error.

        Args:
            role:
                ID of the role.

        Returns:
            A [role object](../api/actions/entities#role){ target="_blank" }.
        """
        r = guild__.get_role(role)
        return None if not r else Role.from_object(r).to_dict()

    
    @block
    @staticmethod
    def roles(
        guild__ : Guild
    ) -> Dict[Snowflake, Role]:
        """
        Gets a mapping of [role objects](../api/actions/entities#role){ target="_blank" } in the server.

        Returns:
            A dictionary of [role objects](../api/actions/entities#role){ target="_blank" }.
        """
        return { str(x) : Role.from_object(y).to_dict() for x, y in guild__.get_roles().items() }

    
    @block
    @staticmethod
    async def role_create(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        name : str = "new role",
        permissions : Permissions = 0,
        color : Color = 0,
        hoist : bool = False,
        mentionable : bool = False,
        reason : Optional[str] = None
    ) -> Role:
        """
        Creates a role in the server.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_ROLES` permission to perform this action.

        Args:
            name:
                Name of the new role.
            permissions:
                List of [`Discord permission names`](../api/actions/entities#permissions){ target="_blank" }.
            color:
                RGB color value.
            hoist:
                Whether the role should be displayed separately in the sidebar.
            mentionable:
                Whether the role should be mentionable.
            reason:
                Reason of performing the action. May show up in the Audit Log.

        Returns:
            The created [Role](entities#role){ target="_blank" }.
        """
        role = await rest__.create_role(
            guild = guild__.id, 
            reason = reason or UNDEFINED, 
            name = name or UNDEFINED, 
            permissions = int(permissions) or UNDEFINED, 
            color = color or UNDEFINED,
            hoist = hoist,
            mentionable = mentionable
        )
        return Role.from_object(role).to_dict()

    
    @block
    @staticmethod
    async def role_delete(
        guild__ : Guild,
        rest__ : RESTClientImpl,
        *,
        role : ObjectOrSnowflake
    ) -> None:
        """
        Deletes a role from server.

        !!! warning "Privileged permission required"
            Relay needs to have `MANAGE_ROLES` permission to perform this action.

        Args:
            role:
                ID of the role.
        """
        await rest__.delete_role(guild = guild__.id, role = role)

    # ----------------------------
    # INTERACTIONS
    # ----------------------------

    @block
    @staticmethod
    async def interaction_reply_wait(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction] = None,
        *,
        ephemeral : bool = True,
        show_wait : bool = False
    ) -> None:
        """
        Acknowledge an interaction and edit a response later. Normally, Discord requires you to send a message
        in 3 seconds, however you can extend it to 15 minutes by asking for wait.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            show_wait:
                If set to False (the default), user will not see a "Loading..." state. This option can be only used when you receive interaction with
                Message Components. If you are using this block in a Application Command, this will be ignored.
            ephemeral:
                If set to True (the default), only the user who executed the slash command can see the message. If False, everyone can see the created message.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        await rest__.create_interaction_response(
            interaction__.id, 
            interaction__.token, 
            ResponseType.DEFERRED_MESSAGE_CREATE if interaction__.type == int(InteractionType.APPLICATION_COMMAND) else \
            (ResponseType.DEFERRED_MESSAGE_UPDATE if not show_wait else ResponseType.DEFERRED_MESSAGE_CREATE),
            flags = 1 << 6 if ephemeral else UNDEFINED
        )

    
    @block
    @staticmethod
    async def interaction_reply_message(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction] = None,
        *,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None,
        components : Components = None,
        ephemeral : bool = True,
        update : bool = False
    ) -> None:
        """
        Responds to a interaction.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
            ephemeral:
                If set to True (the default), only the user who executed the slash command can see the message. If False, everyone can see the created message.
            update:
                If True, updates the actual message. This only can be used in Component listeners, in other interactions this has no effect. 
            components:
                List or a single Component object.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        alm = Mentions() if not mentions else mentions
        components = None if not components else components.to_object()
        await rest__.create_interaction_response(
            interaction__.id, 
            interaction__.token, 
            ResponseType.MESSAGE_CREATE if interaction__.type == int(InteractionType.APPLICATION_COMMAND) else \
            ResponseType.MESSAGE_UPDATE if update else ResponseType.MESSAGE_CREATE,
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == UNDEFINED else [x.to_object() for x in embed], 
            components = components or UNDEFINED,
            mentions_everyone = alm.everyone,
            user_mentions = alm.users,
            role_mentions = alm.roles,
            flags = 1 << 6 if ephemeral else UNDEFINED
        )

    
    @block
    @staticmethod
    async def interaction_reply_modal(
        bot__ : RelayBot,
        interaction__ : Optional[Interaction] = None,
        *,
        custom_id : str,
        title : str,
        components : ModalComponents
    ) -> None:
        """
        Responds to a interaction with showing a modal.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            custom_id:
                A custom ID for modal, so you can learn which modal has submitted.
            title:
                The title of the popup modal.
            components:
                Between 1 and 5 (inclusive) components that make up the modal.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        await bot__.request(POST_INTERACTION_RESPONSE, sdict(
            interaction = interaction__.id,
            token = interaction__.token
            ),
            type = 9,
            data = sdict(
                title = title,
                custom_id = custom_id,
                components = components
            )
        )


    @block
    @staticmethod
    async def interaction_edit_message(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction],
        *,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None,
        components : Components = None
    ) -> Message:
        """
        Edits the initial interaction response.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
            components:
                List or a single Component object.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        alm = Mentions() if not mentions else mentions
        components = None if not components else components.to_object()
        message = await rest__.edit_interaction_response(
            interaction__.application_id,
            interaction__.token,
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == UNDEFINED else [x.to_object() for x in embed], 
            components = components or UNDEFINED,
            mentions_everyone = alm.everyone,
            user_mentions = alm.users,
            role_mentions = alm.roles
        )
        return Message.from_object(message).to_dict()


    @block
    @staticmethod
    async def interaction_get_message(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction]
    ) -> Message:
        """
        Returns the initial Interaction response.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        message = await rest__.fetch_interaction_response(interaction__.application_id, interaction__.token)
        return Message.from_object(message).to_dict()

    
    @block
    @staticmethod
    async def interaction_delete_message(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction]
    ) -> None:
        """
        Deletes the initial interaction response.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        await rest__.delete_interaction_response(interaction__.application_id, interaction__.token)

    # ----------------------------
    # INTERACTION WEBHOOKS
    # ----------------------------

    @block
    @staticmethod
    async def interaction_create_followup(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction],
        *,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None,
        components : Components = None,
        ephemeral : bool = True
    ) -> Message:
        """
        Create a followup message for an interaction.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
            ephemeral:
                If set to True (the default), only the user who executed the slash command can see the message. If False, everyone can see the created message.
            components:
                List or a single Component object.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        alm = Mentions() if not mentions else mentions
        components = None if not components else components.to_object()
        message = await rest__.execute_webhook(
            int(interaction__.application_id), 
            interaction__.token,
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == UNDEFINED else [x.to_object() for x in embed], 
            components = components or UNDEFINED,
            mentions_everyone = alm.everyone,
            user_mentions = alm.users,
            role_mentions = alm.roles,
            flags = 1 << 6 if ephemeral else UNDEFINED
        )
        return Message.from_object(message).to_dict()

    
    @block
    @staticmethod
    async def interaction_edit_followup(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction],
        *,
        message : ObjectOrSnowflake,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None,
        components : Components = None
    ) -> Message:
        """
        Edit a followup message for an interaction.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            message:
                A message that will be edited.
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
            components:
                List or a single Component object.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        alm = Mentions() if not mentions else mentions
        components = None if not components else components.to_object()
        message = await rest__.edit_webhook_message(
            int(interaction__.application_id), 
            interaction__.token,
            message = message,
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == UNDEFINED else [x.to_object() for x in embed], 
            components = components or UNDEFINED,
            mentions_everyone = alm.everyone,
            user_mentions = alm.users,
            role_mentions = alm.roles
        )
        return Message.from_object(message).to_dict()


    @block
    @staticmethod
    async def interaction_get_followup(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction],
        *,
        message : ObjectOrSnowflake
    ) -> Message:
        """
        Returns a followup message for an interaction.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            message:
                Message that will be fetched.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        message = await rest__.fetch_webhook_message(
            int(interaction__.application_id),
            interaction__.token,
            message = message
        )
        return Message.from_object(message).to_dict()


    @block
    @staticmethod
    async def interaction_delete_followup(
        rest__ : RESTClientImpl,
        interaction__ : Optional[Interaction],
        *,
        message : ObjectOrSnowflake
    ) -> None:
        """
        Deletes a followup message.

        !!! warning "This block only works under interaction"
            This block won't work when action is triggered on a default Discord event.

        Args:
            message:
                Message that will be deleted.
        """
        if not interaction__:
            raise ValueError("This action is not working under an interaction!")
        await rest__.delete_webhook_message(
            int(interaction__.application_id),
            interaction__.token,
            message = message
        )

    # ----------------------------
    # WEBHOOK
    # ----------------------------

    @block
    @staticmethod
    async def webhook_create_message(
        rest__ : RESTClientImpl,
        *,
        webhook_id : str,
        webhook_token : str,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None,
        username : Optional[str] = None,
        avatar_url : Optional[str] = None
    ) -> Message:
        """
        Executes an webhook by providing a webhook ID and webhook token.

        Args:
            webhook_id:
                ID of the webhook.
            webhook_token:
                Token of the webhook.
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
            username:
                A username to override the webhook's own username.
            avatar_url:
                An avatar URL to override the webhook's own avatar.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        alm = Mentions() if not mentions else mentions
        message = await rest__.execute_webhook(
            int(webhook_id),
            webhook_token,
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == UNDEFINED else [x.to_object() for x in embed],
            mentions_everyone = alm.everyone,
            user_mentions = alm.users,
            role_mentions = alm.roles,
            username = username or UNDEFINED,
            avatar_url = avatar_url or UNDEFINED
        )
        return Message.from_object(message).to_dict()


    @block
    @staticmethod
    async def webhook_edit_message(
        rest__ : RESTClientImpl,
        *,
        webhook_id : str,
        webhook_token : str,
        message : ObjectOrSnowflake,
        content : Optional[Any] = None,
        embed : Optional[AdaptiveList[Embed]] = None,
        mentions : Optional[Mentions] = None
    ) -> Message:
        """
        Edits an webhook message by providing a webhook ID and webhook token.

        Args:
            webhook_id:
                ID of the webhook.
            webhook_token:
                Token of the webhook.
            message:
                A message that will be edited.
            content:
                Content of the message, either `content` or `embeds` needs to be filled in.
            embed:
                An [Embed object](../api/actions/entities#embed){ target="_blank" } that will be sent in the message, either `content` or `embed` needs to be filled in.
            mentions:
                An [Mentions object](../api/actions/entities#allowed-mentions){ target="_blank" } that control what mentions are allowed in the message.
        
        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        alm = Mentions() if not mentions else mentions
        message = await rest__.edit_webhook_message(
            int(webhook_id),
            webhook_token,
            message = message,
            content = UNDEFINED if content == None else str(content),
            embeds = UNDEFINED if embed == UNDEFINED else [x.to_object() for x in embed],
            mentions_everyone = alm.everyone,
            user_mentions = alm.users,
            role_mentions = alm.roles
        )
        return Message.from_object(message).to_dict()


    @block
    @staticmethod
    async def webhook_get_message(
        rest__ : RESTClientImpl,
        *,
        webhook_id : str,
        webhook_token : str,
        message : ObjectOrSnowflake
    ) -> Message:
        """
        Gets the message sent by webhook.

        Args:
            webhook_id:
                ID of the webhook.
            webhook_token:
                Token of the webhook.
            message:
                Message that will be fetched.

        Returns:
            A [Message](../api/actions/entities#message){ target="_blank" } object.
        """
        message = await rest__.fetch_webhook_message(
            int(webhook_id),
            webhook_token,
            message = message
        )
        return Message.from_object(message).to_dict()


    @block
    @staticmethod
    async def webhook_delete_message(
        rest__ : RESTClientImpl,
        *,
        webhook_id : str,
        webhook_token : str,
        message : ObjectOrSnowflake
    ) -> None:
        """
        Deletes the message sent by webhook.

        Args:
            webhook_id:
                ID of the webhook.
            webhook_token:
                Token of the webhook.
            message:
                Message that will be deleted.
        """
        await rest__.delete_webhook_message(
            int(webhook_id),
            webhook_token,
            message = message
        )