from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .websocket import register_websockets
from .store import async_get_registry
from .coordinator import SprinkleCoordinator

from .const import DOMAIN, PLATFORMS
from .panel import (
    async_register_panel,
    async_unregister_panel
)

from homeassistant.helpers.device_registry import async_get as async_get_device_registry


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:


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


    hass.data.setdefault(const.DOMAIN, {
        "coordinator": None,
        "config": {
            "entities": {}
        },
        "zones":{},
        "cycles": {}
    })

    # create the default controller entities after controller flow creation.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    store_obj = await async_get_registry(hass)
    coordinator = SprinkleCoordinator(hass, entry, store_obj)
    await coordinator.async_setup()
    hass.data[const.DOMAIN]["coordinator"] = coordinator



    # Setup the side panel.
    await async_register_panel(hass)
    #Register the websockets.
    register_websockets(hass)

    #load the saved config from storage and create entities.


    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    #stop all zones and cycles.
    coordinator: SprinkleCoordinator = hass.data[const.DOMAIN]["coordinator"]
    await coordinator.async_stop_all_cycles_and_zones()
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Integration removal cleanup"""
    await async_unregister_panel(hass)
    coordinator: SprinkleCoordinator = hass.data[DOMAIN]["coordinator"]
    await coordinator.async_delete_config()
    del hass.data[DOMAIN]