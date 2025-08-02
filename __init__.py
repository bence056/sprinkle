from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .websocket import register_websockets
from .store import async_get_registry
from .framework.zone import async_create_zone_device
from .coordinator import SprinkleCoordinator

from .const import DOMAIN, PLATFORMS
from .panel import (
    async_register_panel,
    async_unregister_panel
)

from homeassistant.helpers.device_registry import async_get as async_get_device_registry


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:


    store_obj = await async_get_registry(hass)
    coordinator = SprinkleCoordinator(hass, entry, store_obj)

    # Create the controller device
    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        name=const.NAME,
        model=const.NAME,
        sw_version=const.VERSION,
        manufacturer=const.MANUFACTURER,
    )

    hass.data.setdefault(const.DOMAIN, {})
    hass.data[const.DOMAIN] = {
        "coordinator": coordinator
    }


    # create the default controller entities after controller flow creation.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Setup the side panel.
    await async_register_panel(hass)
    #Register the websockets.
    register_websockets(hass)

    return True


