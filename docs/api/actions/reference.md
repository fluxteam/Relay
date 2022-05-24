---
title: Reference
---

## Server {: #server-object }

Server contains all related information about a Discord server. You can get this object by [`DISCORD.SERVER`][relay.actions.discord.Discord.server] function.

| Name | Type | Description |
|:------------|:-------------|:------------|
| id | [`Snowflake`](#snowflake) | ID of the server. |
| name | `str` | Name of the server. |
| icon | `Optional[str]` | Icon hash of the server icon. |
| description | `str` | The description of a Community server. |
| channels | [`Dict[str, Channel]`](#channel-object) | Mapping of [Channel objects](#channel-object) in the server. |
| roles | [`Dict[str, Role]`](#role-object) | Mapping of [Role objects](#role-object) in the server. |
| large | `bool` | Indicates if the server is a 'large' server. A large server is defined as having more than 250 members. |
| features | `List[str|` | Array of [server features](https://discord.com/developers/docs/resources/guild#guild-object-guild-features) |
| splash | `Optional[str]` | Splash hash of the server splash. |
| max_members | `int` | The maximum number of members for the server. |
| boost_tier | `int` | Server boost level. (0-3) |
| boost_role | [`Optional[Role]`](#role-object) | [Role object](#role-object) of the Nitro Booster role. Can be `None` if there is no booster role. |
| boost_count | `int` | The number of boosts this server currently has. |
| afk_timeout | `int` | AFK timeout in seconds. |
| afk_channel | [`Optional[Channel]`](#channel-object) | [Channel object](#channel-object) of the AFK channel. Can be `None` if there is no AFK channel. |
| default_role | [`Optional[Role]`](#role-object) | A [Role object](#role-object) of the `@everyone` role. |

## Role {: #role-object }

To get role in a server, use [`DISCORD.ROLE`][relay.actions.discord.Discord.role] to get a role by an ID or use [`DISCORD.ROLES`][relay.actions.discord.Discord.roles] to get all roles in dictionary.

| Name | Type | Description |
|:------------|:-------------|:------------|
| id | [`Snowflake`](#snowflake) | ID of the role. |
| name | `str` | Name of the role. |
| color | `int` | Integer representation of hexadecimal color code. |
| hoist | `bool` | If this role is pinned in the user listing. |
| position | `int` | Position of this role. |
| managed | `bool` | Whether this role is managed by an integration. |
| mentionable | `bool` | Whether this role is mentionable. |
| permissions | [`List[Permission]`](#permission-object) | List of [permission names.](#permission-object) |

## Channel {: #channel-object }

To get a channel in server, use [`DISCORD.CHANNEL`][relay.actions.discord.Discord.channel] to get a channel by an ID or use [`DISCORD.CHANNELS`][relay.actions.discord.Discord.channels] to get all channels in dictionary.

| Name | Type | Description |
|:------------|:-------------|:------------|
| id | [`Snowflake`](#snowflake) | ID of the channel. |
| name | `str` | Name of the channel. |
| topic | `Optional[str]` | Topic of the channel. It is `None` for non-text channels. |
| nsfw | `Optional[bool]` | `True` if channel has marked as NSFW. Otherwise `False`. It is `None` for non-text channels. |
| category | [`Optional[Channel]`](#channel-object) | [Channel object](#channel-object) of the category. Can be `None` if channel doesn't placed in a category. |
| position | `int` | Sorting position of the channel. |
| slowmode_delay | `Optional[int]` | Amount of seconds a user has to wait before sending another message (0-21600); bots, as well as users with the permission `MANAGE_MESSAGES` or `MANAGE_CHANNELS`, are unaffected. |
| overwrites | [`List[Overwrites]`](#overwrites-object) | Explicit [permission overwrites](#overwrites-object) for members and roles. |
| type | `int` | [Type of the channel.](https://discord.com/developers/docs/resources/channel#channel-object-channel-types){ target="_blank" } |
| last_message | `Optional[int]` | The ID of the last message sent in this channel (may not point to an existing or valid message). It is `None` for non-text channels. |
| bitrate | `Optional[int]` | The bitrate (in bits) of the voice channel. It is `None` for non-voice channels. |
| user_limit | `Optional[int]` | The user limit of the voice channel. It is `None` for non-voice channels. |

## Message {: #message-object }

Message object is sent when a event happens related to messages such as [`MESSAGE_SEND`](events#message_send).

| Name | Type | Description |
|:------------|:-------------|:------------|
| id | [`Snowflake`](#snowflake) | ID of the message. |
| channel | [`Channel`](#channel-object) | [Channel object](#channel-object) of the message. |
| author | [`Member`](#member-object) or [`User`](#user-object) | Author of the message. If author is in the server, then this will be a [Member object](#member-object), otherwise it will be a [User object](#user-object) instead. |
| content | `Optional[str]` | Content of the message. |
| system | `bool` | `True` if message is a system message. Otherwise, `False`. |
| created_at | `datetime` | The message's creation time in UTC. |
| edited_at | `datetime` | A naive UTC datetime object containing the edited time of the message. |
| activity | `Dict` | Sent with Rich Presence-related chat embeds. |
| url | `str` | An URL that points to the message. |
| embeds | [`List[Embed]`](#embed-object) | List of Embed objects. |
| type | `int` | [Type of the message.](https://discord.com/developers/docs/resources/channel#message-object-message-types){ target="_blank" } |
| mentioned_users | `List[int]` | List of user IDs that mentioned in the messages. |
| mentioned_roles | `List[int]` | List of role IDs that mentioned in the messages. |
| mentioned_channels | `List[int]` | List of channel IDs that mentioned in the messages. |

## Mentions {: #allowed-mentions-object }

An object that represents what mentions are allowed in a message.

| Name | Type | Description |
|:------------|:-------------|:------------|
| roles | `Union[bool, List[Snowflake]]` | Controls the roles being mentioned. If `True` (the default) then roles are mentioned based on the message content. If `False` then roles are not mentioned at all. If a list of role IDs is given, then only the roles provided will be mentioned, provided those roles are in the message content. |
| users | `Union[bool, List[Snowflake]]` | Controls the users being mentioned. If `True` (the default) then users are mentioned based on the message content. If `False` then users are not mentioned at all. If a list of role IDs is given, then only the users provided will be mentioned, provided those users are in the message content. |
| everyone | `bool` | Whether to allow everyone and here mentions. Defaults to `False`. |
| replied_user | `bool` | Whether to mention the author of the message being replied to. Defaults to `False`. |

## EmbedField {: #embed-field-object }

Embed field represents a field in [embed](#embed-object).

| Name | Type | Description |
|:------------|:-------------|:------------|
| name | `str` | Name of the field. |
| value | `str` | Value of the field. |
| inline | `bool` | Whether or not this field should display inline. Defaults to `False`. |

## EmbedFooter {: #embed-footer-object }

Embed footer represents a footer in [embed](#embed-object).

| Name | Type | Description |
|:------------|:-------------|:------------|
| text | `str` | Text for footer. |
| icon_url | `Optional[str]` | Url of footer icon (only supports http(s)). |

## Snowflake {: #snowflake }

Represents a Discord ID. Snowflakes are always string (`str`).

## Embed {: #embed-object }

Embed objects are same as Discord embeds, however you can also use Relay styled embeds which is much easier to create a new embed as it doesn't require nested objects. You can both create embeds in old and new style and they all will create same result.

??? example "Difference between Discord and Relay styled embeds"

    === "Discord style"
        ```json
        {
            "title": "Embed Title",
            "description": "Description",
            "color": "16711680",
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

    === "Relay style"
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

        * Relay embeds accepts color names (such as "red", "brown"), HEX, RGB and integer color (but as a string) in `color` key.
        * It doesn't require adding object in `image`, instead you can provide a URL directly.

| Name | Type | Description |
|:------------|:-------------|:------------|
| title | `Optional[str]` | Title of the embed. |
| description | `Optional[str]` | Description of the embed. |
| url | `Optional[str]` | URL of the embed. |
| color | `Optional[str]` | Color code of embed in string. If you are creating a new embed, you can set HEX, RGB and color names (etc. "red", "brown") in this field and they will be converted automatically. |
| timestamp | `Optional[datetime]` | A timestamp of embed content. |
| image | `Optional[str]` | URL of the embed image. |
| thumbnail | `Optional[str]` | URL of the embed thumbnail. |
| fields | [`List[EmbedField]`](#embed-field-object) | List of [embed field objects](#embed-field-object) in this embed. |
| footer | [`Optional[EmbedFooter]`](#embed-footer-object) | A footer object for this embed. |

## Member {: #member-object }

Member means an existing Discord user in the server.

| Name | Type | Description |
|:------------|:-------------|:------------|
| id | [`Snowflake`](#snowflake) | ID of the member. |
| name | `str` | User name of the member. |
| roles | [`Dict[str, Role]`](#role-object) | Mapping of [Role objects](#role-object) with their IDs that this member has. |
| nick | `Optional[str]` | Nickname of the user for current server. |
| display_name | `str` | For regular users this is just their username, but if they have a server specific nickname then that is returned instead. |
| discriminator | `str` | The user's 4-digit discord-tag. |
| tag | `str` | User's name and discriminator joined with "#". |
| avatar | `Optional[str]` | Avatar hash of the user avatar. |
| avatar_url | `str` | URL of avatar. If the user does not have a traditional avatar, an URL for the default avatar is returned instead. |
| bot | `bool` | `True` if user is a bot, `False` otherwise. |
| system | `bool` | Whether the user is an Official Discord System user (part of the urgent message system) |
| permissions | [`List[Permission]`](#permission-object) | List of [permission names](#permission-object) that this member has in guild-level. |

## User {: #user-object }

User means an existing Discord user but not in the server. This will be returned if user is banned, kicked.

| Name | Type | Description |
|:------------|:-------------|:------------|
| id | [`Snowflake`](#snowflake) | ID of the member. |
| name | `str` | User name of the member. |
| roles | `None` | Always `None`. |
| nick | `None` | Always `None`. |
| display_name | `str` | Same as `name`. |
| discriminator | `str` | The user's 4-digit discord-tag. |
| tag | `str` | User's name and discriminator joined with "#". |
| avatar | `Optional[str]` | Avatar hash of the user avatar. |
| avatar_url | `str` | URL of avatar. If the user does not have a traditional avatar, an URL for the default avatar is returned instead. |
| bot | `bool` | `True` if user is a bot, `False` otherwise. |
| system | `bool` | Whether the user is an Official Discord System user (part of the urgent message system) |
| permissions | `None` | Always `None`. |

## Overwrites {: #overwrites-object }

Overwrites defines which users and roles has specified permissions for a channel.

| Name        | Type               | Description                                     |
|:------------|:-------------------|:------------------------------------------------|
| id          | [`Snowflake`](#snowflake)          | Role or User ID                                 |
| type        | `int`                                    | Either 0 (role) or 1 (member).                  |
| allow       | [`List[Permission]`](#permission-object) | List of [permission names.](#permission-object) |
| deny        | [`List[Permission]`](#permission-object) | List of [permission names.](#permission-object) |

## Permissions {: #permission-object }

Just type permission type in places where a Permission object is required.

| Permission                    | Value                      | Description                                                                                                                        | Channel Type |
|:------------------------------|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|:-------------|
| CREATE_INSTANT_INVITE         | `0x0000000001` `(1 << 0)`  | Allows creation of instant invites                                                                                                 | T, V, S      |
| KICK_MEMBERS                  | `0x0000000002` `(1 << 1)`  | Allows kicking members                                                                                                             |              |
| BAN_MEMBERS                   | `0x0000000004` `(1 << 2)`  | Allows banning members                                                                                                             |              |
| ADMINISTRATOR                 | `0x0000000008` `(1 << 3)`  | Allows all permissions and bypasses channel permission overwrites                                                                  |              |
| MANAGE_CHANNELS               | `0x0000000010` `(1 << 4)`  | Allows management and editing of channels                                                                                          | T, V, S      |
| MANAGE_GUILD                  | `0x0000000020` `(1 << 5)`  | Allows management and editing of the guild                                                                                         |              |
| ADD_REACTIONS                 | `0x0000000040` `(1 << 6)`  | Allows for the addition of reactions to messages                                                                                   | T            |
| VIEW_AUDIT_LOG                | `0x0000000080` `(1 << 7)`  | Allows for viewing of audit logs                                                                                                   |              |
| PRIORITY_SPEAKER              | `0x0000000100` `(1 << 8)`  | Allows for using priority speaker in a voice channel                                                                               | V            |
| STREAM                        | `0x0000000200` `(1 << 9)`  | Allows the user to go live                                                                                                         | V            |
| VIEW_CHANNEL                  | `0x0000000400` `(1 << 10)` | Allows guild members to view a channel, which includes reading messages in text channels                                           | T, V, S      |
| SEND_MESSAGES                 | `0x0000000800` `(1 << 11)` | Allows for sending messages in a channel                                                                                           | T            |
| SEND_TTS_MESSAGES             | `0x0000001000` `(1 << 12)` | Allows for sending of `/tts` messages                                                                                              | T            |
| MANAGE_MESSAGES               | `0x0000002000` `(1 << 13)` | Allows for deletion of other users messages                                                                                        | T            |
| EMBED_LINKS                   | `0x0000004000` `(1 << 14)` | Links sent by users with this permission will be auto-embedded                                                                     | T            |
| ATTACH_FILES                  | `0x0000008000` `(1 << 15)` | Allows for uploading images and files                                                                                              | T            |
| READ_MESSAGE_HISTORY          | `0x0000010000` `(1 << 16)` | Allows for reading of message history                                                                                              | T            |
| MENTION_EVERYONE              | `0x0000020000` `(1 << 17)` | Allows for using the `@everyone` tag to notify all users in a channel, and the `@here` tag to notify all online users in a channel | T            |
| USE_EXTERNAL_EMOJIS           | `0x0000040000` `(1 << 18)` | Allows the usage of custom emojis from other servers                                                                               | T            |
| VIEW_GUILD_INSIGHTS           | `0x0000080000` `(1 << 19)` | Allows for viewing guild insights                                                                                                  |              |
| CONNECT                       | `0x0000100000` `(1 << 20)` | Allows for joining of a voice channel                                                                                              | V, S         |
| SPEAK                         | `0x0000200000` `(1 << 21)` | Allows for speaking in a voice channel                                                                                             | V            |
| MUTE_MEMBERS                  | `0x0000400000` `(1 << 22)` | Allows for muting members in a voice channel                                                                                       | V, S         |
| DEAFEN_MEMBERS                | `0x0000800000` `(1 << 23)` | Allows for deafening of members in a voice channel                                                                                 | V, S         |
| MOVE_MEMBERS                  | `0x0001000000` `(1 << 24)` | Allows for moving of members between voice channels                                                                                | V, S         |
| USE_VAD                       | `0x0002000000` `(1 << 25)` | Allows for using voice-activity-detection in a voice channel                                                                       | V            |
| CHANGE_NICKNAME               | `0x0004000000` `(1 << 26)` | Allows for modification of own nickname                                                                                            |              |
| MANAGE_NICKNAMES              | `0x0008000000` `(1 << 27)` | Allows for modification of other users nicknames                                                                                   |              |
| MANAGE_ROLES                  | `0x0010000000` `(1 << 28)` | Allows management and editing of roles                                                                                             | T, V, S      |
| MANAGE_WEBHOOKS               | `0x0020000000` `(1 << 29)` | Allows management and editing of webhooks                                                                                          | T            |
| MANAGE_EMOJIS_AND_STICKERS    | `0x0040000000` `(1 << 30)` | Allows management and editing of emojis and stickers                                                                               |              |
| USE_SLASH_COMMANDS            | `0x0080000000` `(1 << 31)` | Allows members to use slash commands in text channels                                                                              | T            |
| REQUEST_TO_SPEAK              | `0x0100000000` `(1 << 32)` | Allows for requesting to speak in stage channels.                                                                                  | S            |
| MANAGE_THREADS                | `0x0400000000` `(1 << 34)` | Allows for deleting and archiving threads, and viewing all private threads                                                         | T            |
| USE_PUBLIC_THREADS            | `0x0800000000` `(1 << 35)` | Allows for creating and participating in threads                                                                                   | T            |
| USE_PRIVATE_THREADS           | `0x1000000000` `(1 << 36)` | Allows for creating and participating in private threads                                                                           | T            |
| USE_EXTERNAL_STICKERS         | `0x2000000000` `(1 << 37)` | Allows the usage of custom stickers from other servers                                                                             | T            |