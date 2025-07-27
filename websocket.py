from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import websocket_command, async_register_command
from homeassistant.core import callback, HomeAssistant
import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)

@websocket_command(
{
    vol.Required("type"): "sprinkle/log",
    vol.Required("message"): str
})
@callback
def sprinkle_log(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    _LOGGER.info("[Sprinkle log]: %s", msg["message"])




def register_websockets(hass: HomeAssistant):
    async_register_command(hass, sprinkle_log)