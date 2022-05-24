---
title: Entities
hide:
  - toc
---

# Entities {: #title }

Entities are Discord objects that users can use to get information from it. Attributes of entities are mostly same with Discord's own documentation, however to making the objects more readable and simplier, Relay uses different names and doesn't have partial objects.

## Server {: #server }

::: relay.models.Server
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Channel {: #channel }

::: relay.models.Channel
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Message {: #message }

::: relay.models.Message
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Interaction {: #interaction }

::: relay.models.Interaction
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Role {: #role }

::: relay.models.Role
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Member {: #member }

::: relay.models.Member
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## User {: #user }

::: relay.models.User
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Overwrites {: #overwrites }

::: relay.models.Overwrites
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Mentions {: #mentions }

::: relay.models.Mentions
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Embed {: #embed }

::: relay.models.Embed
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## EmbedField {: #embed-field }

::: relay.models.EmbedField
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## EmbedFooter {: #embed-footer }

::: relay.models.EmbedFooter
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## EmbedAuthor {: #embed-author }

::: relay.models.EmbedAuthor
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Emoji {: #emoji }

::: relay.models.Emoji
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Reaction {: #reaction }

::: relay.models.Reaction
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
    selection:
      inherited_members: false

## Asset {: #asset }

Relay stores icons, avatars, banners and other Discord assets as `Asset` objects (which builds an Discord URL inside) instead of storing file hash (which Discord API sends to Relay). This decision was made so that people can quickly access the asset instead of creating the URL on their own.

```
188799f53a6e26966d616a5838a4498d --> https://cdn.discordapp.com/icons/.../188799f53a6e26966d616a5838a4498d.png
```

## Snowflake {: #snowflake }

Snowflakes are always represented in strings.

## Permissions {: #permissions }

Normally, permissions are defined in bits, however Relay support every type of permissions; names, bits, list of names and list of bits. 

```py
# Supported:
* ["BAN_MEMBERS", "ADMINISTRATOR"] # List of permission names.
* [1, 8]                           # List of permission bit values.
* "BAN_MEMBERS"                    # A permission name.
* 8                                # A permission bit value.
* ["BAN_MEMBERS", 1]               # Mixed list contains names and bit values.

# Unsupported:
* None
```

To see a list of available permissions, head over to [Discord's own documentation](https://discord.com/developers/docs/topics/permissions#permissions-bitwise-permission-flags){ target="_blank" }.