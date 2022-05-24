# Relay

Relay is a no-code programmable bot that allows you to do _anything_ on your Discord server. Relay both supports interactions and gateway events, and includes built-in blocks to have anything you need. It is written in Python, built on Blockly, served on Sanic, hosted on Railway, uses MongoDB as database, socket.io for collaboration and Mkdocs for documentation.

[![Blockly](https://svgshare.com/i/gjM.svg)](https://developers.google.com/blockly)

> ⚠ Relay is abandoned due to I lost interest in the project, so this repository is in read-only mode. If you want to work on Relay, you can fork and release as a new bot, under the license conditions.

<div align="center">
   <img src="https://i.imgur.com/s6aEhtd.png" width="1000">
</div>
<br>

When you save your blocks, the blocks are converted to a step-by-step workflow format that Relay understands. After, when Relay receives a gateway event or interaction, the workflow is executed for the server that event received for. Workflow execution are managed by [pyconduit](https://github.com/ysfchn/pyconduit), which is a library made for Relay. 

## Features

* Supports interactions, modals, components, context and slash commands
* Gateway events (reaction, message, user, channel, server events)
* Share your blocks on GitHub as installable packages
* Webhooks; do something when Webhook receives an HTTP request
* Debug your listeners

## Limitations

* Relay doesn't has Voice capabilities. Because Voice can degrade the performance, also it may not be possible to play any type of voice without providing any audio sources. Relay of course can have blocks for streaming audio from different sources, but I don't want to deal with copyright/legal stuff. 
* There are no any I/O (file) blocks. I think I/O can be easily abused to fill up the memory of Relay and requires a lot of pre-checks.
* Some gateway events that fires too much are not available (member updates, typing indicator).

Due to nature of Discord bots, they use more and more RAM when they are added in more servers. Also because of Python's inefficency compared to JavaScript etc and because of the code itself, I'm not sure if Relay can handle same number of servers compared to any other bot.

## Development

Relay contains two parts, one is for Web server and other one is for Discord bot. Web server can work alone without needing to launch Discord bot, but Discord bot can't work properly without Web server.

Web server:

```
sanic web.app
```

Bot:

```
python bot.py
```
