

from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import websocket_command, async_register_command, async_response
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.http import HomeAssistantView
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.helpers import config_validation as cv
from . import const
from .coordinator import SprinkleCoordinator
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
    vol.Required("type"): "sprinkle/get_zones",
})
@async_response
async def sprinkle_get_zones(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = hass.data[const.DOMAIN]["coordinator"]
    response = [attr.asdict(z) for z in coordinator.store.zones.values()]
    connection.send_result(msg["id"],  response)


@websocket_command(
{
    vol.Required("type"): "sprinkle/get_cycles",
})
@async_response
async def sprinkle_get_cycles(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    coordinator: SprinkleCoordinator = hass.data[const.DOMAIN]["coordinator"]
    response = [attr.asdict(c) for c in coordinator.store.cycles.values()]
    connection.send_result(msg["id"],  response)

@websocket_command(
{
    vol.Required("type"): "sprinkle/get_gs",
})
@async_response
async def sprinkle_get_gs(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict):
    store: SprinkleStorage = hass.data[const.DOMAIN]["coordinator"].store;
    response = attr.asdict(store.settings)
    connection.send_result(msg["id"],  response)


class SprinkleZonesView(HomeAssistantView):

    url = "/api/sprinkle/zones"
    name = "api:sprinkle:zones"

    @RequestDataValidator(
        vol.Schema(
            {
                vol.Required(const.ATTR_ZONE_ID): cv.string,
                vol.Optional(const.ATTR_ZONE_DELETE): cv.boolean,
                vol.Optional(const.ATTR_ZONE_NAME): cv.string,
                vol.Optional(const.ATTR_ZONE_VALVES): vol.All(
                    cv.ensure_list,
                    [cv.entity_id]
                )

            }
        )
    )

    async def post(self, request: Request, data):
        hass: HomeAssistant = request.app["hass"]
        coordinator: SprinkleCoordinator = hass.data[const.DOMAIN]["coordinator"]

        await coordinator.async_update_zone_config(data[const.ATTR_ZONE_ID], data)


class SprinkleCyclesView(HomeAssistantView):

    url = "/api/sprinkle/cycles"
    name = "api:sprinkle:cycles"

    @RequestDataValidator(
        vol.Schema(
            {
                vol.Required(const.ATTR_CYCLE_ID): cv.string,
                vol.Optional(const.ATTR_CYCLE_DELETE): cv.boolean,
                vol.Optional(const.ATTR_CYCLE_NAME): cv.string,
                vol.Optional(const.ATTR_CYCLE_STEPS): cv.ensure_list

            }
        )
    )

    async def post(self, request: Request, data):
        hass: HomeAssistant = request.app["hass"]
        coordinator: SprinkleCoordinator = hass.data[const.DOMAIN]["coordinator"]

        await coordinator.async_update_cycle_config(data[const.ATTR_CYCLE_ID], data)


class SprinkleGeneralSettingsView(HomeAssistantView):

    url = "/api/sprinkle/generalSettings"
    name = "api:sprinkle:general_settings"

    @RequestDataValidator(
        vol.Schema(
            {

                vol.Required(const.ATTR_SETTINGS_USE_MASTER_VALVE): cv.boolean,
                vol.Required(const.ATTR_SETTINGS_MASTER_VALVE_ID): vol.Any(
                    cv.entity_id,
                    ""
                ),
                vol.Required(const.ATTR_SETTINGS_VALVE_TOGGLE_DELAY_MS): cv.positive_int,

            }
        )
    )

    async def post(self, request: Request, data):
        hass: HomeAssistant = request.app["hass"]
        coordinator: SprinkleCoordinator = hass.data[const.DOMAIN]["coordinator"]

        await coordinator.async_update_general_settings(data)




def register_websockets(hass: HomeAssistant):
    async_register_command(hass, handle_subscribe_updates)
    async_register_command(hass, sprinkle_log)
    async_register_command(hass, sprinkle_get_zones)
    async_register_command(hass, sprinkle_get_cycles)
    async_register_command(hass, sprinkle_get_gs)
    hass.http.register_view(SprinkleZonesView)
    hass.http.register_view(SprinkleCyclesView)
    hass.http.register_view(SprinkleGeneralSettingsView)