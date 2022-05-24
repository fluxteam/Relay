"""
Relay Web
"""

from sanic import Blueprint
import socketio
from relay.commons import BASE_URL

# Create new blueprint.
bp = Blueprint("Routes")

# Create new Socket.IO
sio = socketio.AsyncServer(
    async_mode = "sanic",
    cors_allowed_origins = [BASE_URL]
)

import relay.web.helpers
import relay.web.auth
import relay.web.pack
import relay.web.pages
import relay.web.events
import relay.web.blockly
import relay.web.deploy