from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import websocket_command, async_register_command, async_response
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)


@callback
@websocket_command({
    vol.Required("type"): "sprinkle_update_listen",
})
@async_response
async def handle_subscribe_updates(hass, connection, msg):
    """Handle subscribe updates."""

    @callback
    def async_handle_event():
        """Forward events to websocket."""
        connection.send_message({
            "id": msg["id"],
            "type": "event",
        })

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass,
        "sprinkle_update_dispatch",
        async_handle_event
    )
    connection.send_result(msg["id"])


@websocket_command(
{
    vol.Required("type"): "sprinkle/log",
    vol.Required("message"): str
})
@callback
def sprinkle_log(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    _LOGGER.info("[Sprinkle log]: %s", msg["message"])


@websocket_command(
{
    vol.Required("type"): "sprinkle/create_zone",
    vol.Required("name"): str,
    vol.Required("valves"): list,
})
@callback
def create_zone(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    pass

@websocket_command(
{
    vol.Required("type"): "sprinkle/modify_zone",
    vol.Required("id"): str,
    vol.Required("valves"): list,
})
@callback
def modify_zone(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    pass

@websocket_command(
{
    vol.Required("type"): "sprinkle/delete_zone",
    vol.Required("id"): str,
})
@callback
def delete_zone(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    pass

@websocket_command(
{
    vol.Required("type"): "sprinkle/fetch_data",
    vol.Required("id"): str,
})
@callback
def delete_zone(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    pass

def register_websockets(hass: HomeAssistant):
    async_register_command(hass, sprinkle_log)
    async_register_command(hass, create_zone)
    async_register_command(hass, modify_zone)
    async_register_command(hass, delete_zone)
