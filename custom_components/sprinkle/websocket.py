

from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import websocket_command, async_register_command, async_response
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.helpers import config_validation as cv
from . import const, SprinkleSetupManager, try_get_setup_manager
from .coordinator import SprinkleCoordinator, try_get_coordinator, try_get_coordinator_by_id
import voluptuous as vol
import logging
from aiohttp.web import Request
import attr
from .store import SprinkleStorage

_LOGGER = logging.getLogger(__name__)


@callback
@websocket_command({
    vol.Required("type"): "sprinkle_update_listen",
})
def handle_subscribe_updates(hass, connection: websocket_api.ActiveConnection, msg):
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
    vol.Required("type"): "sprinkle/get_entries",
})
@async_response
async def sprinkle_get_entries(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    manager: SprinkleSetupManager = try_get_setup_manager(hass)
    response = manager.get_registered_config_entries()
    connection.send_result(msg["id"],  response)

@websocket_command(
{
    vol.Required("type"): "sprinkle/get_zones",
    vol.Required("entry"): str,
})
@async_response
async def sprinkle_get_zones(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = try_get_coordinator_by_id(hass, msg["entry"])
    response = [attr.asdict(z) for z in coordinator.substore.zones.values()]
    connection.send_result(msg["id"],  response)


@websocket_command(
{
    vol.Required("type"): "sprinkle/get_cycles",
    vol.Required("entry"): str,
})
@async_response
async def sprinkle_get_cycles(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = try_get_coordinator_by_id(hass, msg["entry"])
    response = [attr.asdict(c) for c in coordinator.substore.cycles.values()]
    connection.send_result(msg["id"],  response)

@websocket_command(
{
    vol.Required("type"): "sprinkle/get_gs",
    vol.Required("entry"): str,
})
@async_response
async def sprinkle_get_gs(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = try_get_coordinator_by_id(hass, msg["entry"])
    response = attr.asdict(coordinator.substore.settings)
    connection.send_result(msg["id"],  response)


@websocket_command(
    {
        vol.Required("type"): "sprinkle/zone",
        vol.Required("entry"): str,
        vol.Required("zone"): {
            vol.Required(const.ATTR_ZONE_ID): cv.string,
            vol.Optional(const.ATTR_ZONE_DELETE): cv.boolean,
            vol.Optional(const.ATTR_ZONE_NAME): cv.string,
            vol.Optional(const.ATTR_ZONE_VALVES): vol.All(
                cv.ensure_list,
                [cv.entity_id]
            )
        }
    })
@async_response
async def sprinkle_update_zone(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = try_get_coordinator_by_id(hass, msg["entry"])
    await coordinator.async_update_zone_config(msg["zone"][const.ATTR_ZONE_ID], msg["zone"])
    connection.send_result(msg["id"], True)


@websocket_command(
    {
        vol.Required("type"): "sprinkle/cycle",
        vol.Required("entry"): str,
        vol.Required("cycle"): {
            vol.Required(const.ATTR_CYCLE_ID): cv.string,
            vol.Optional(const.ATTR_CYCLE_DELETE): cv.boolean,
            vol.Optional(const.ATTR_CYCLE_NAME): cv.string,
            vol.Optional(const.ATTR_CYCLE_STEPS): cv.ensure_list
        }
    })
@async_response
async def sprinkle_update_cycle(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = try_get_coordinator_by_id(hass, msg["entry"])
    await coordinator.async_update_cycle_config(msg["cycle"][const.ATTR_CYCLE_ID], msg["cycle"])
    connection.send_result(msg["id"], True)


@websocket_command(
    {
        vol.Required("type"): "sprinkle/gs",
        vol.Required("entry"): str,
        vol.Required("settings"): {
            vol.Required(const.ATTR_SETTINGS_USE_MASTER_VALVE): cv.boolean,
            vol.Required(const.ATTR_SETTINGS_MASTER_VALVE_ID): vol.Any(
                cv.entity_id,
                ""
            ),
            vol.Required(const.ATTR_SETTINGS_VALVE_TOGGLE_DELAY_MS): cv.positive_int
        }
    })
@async_response
async def sprinkle_update_gs(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = try_get_coordinator_by_id(hass, msg["entry"])
    await coordinator.async_update_general_settings(msg["settings"])
    connection.send_result(msg["id"], True)


def register_websockets(hass: HomeAssistant):
    async_register_command(hass, handle_subscribe_updates)
    async_register_command(hass, sprinkle_log)
    async_register_command(hass, sprinkle_get_zones)
    async_register_command(hass, sprinkle_get_cycles)
    async_register_command(hass, sprinkle_get_gs)
    async_register_command(hass, sprinkle_update_zone)
    async_register_command(hass, sprinkle_update_cycle)
    async_register_command(hass, sprinkle_update_gs)
