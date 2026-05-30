from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
import logging

from .setup_manager import SprinkleSetupManager, try_get_setup_manager
from .websocket import register_websockets
from .store import async_get_registry
from .coordinator import SprinkleCoordinator, try_get_coordinator

from .const import DOMAIN, PLATFORMS

from homeassistant.helpers.device_registry import async_get as async_get_device_registry


_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config):



    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    hass.data.setdefault(const.DOMAIN, {
        "manager": None,
        "config_entries": {},
    })

    if hass.data[const.DOMAIN]["manager"] is None:
        store_obj = await async_get_registry(hass)
        hass.data[const.DOMAIN]["manager"] = SprinkleSetupManager(hass, store_obj)

    # Create the controller device
    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        name="Irrigation Controller",
        model="Irrigation Controller",
        sw_version=const.VERSION,
        manufacturer=const.MANUFACTURER,
    )

    _LOGGER.info(f"Creating configuration entry for {entry.title}")
    # create the default controller entities after controller flow creation.

    await try_get_setup_manager(hass).async_setup(entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info(f"Unloading configuration entry for {entry.title}")
    await try_get_setup_manager(hass).async_unload(entry)
    return True

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Integration removal cleanup"""
    _LOGGER.info(f"Removing configuration entry for {entry.title}")
    await try_get_setup_manager(hass).async_remove(entry)