from homeassistant.components.device_tracker import config_entry
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
import logging
from .setup_manager import SprinkleSetupManager, try_get_setup_manager
from .websocket import register_websockets
from .store import async_get_registry, SprinkleStorage
from .coordinator import SprinkleCoordinator, try_get_coordinator

from .const import DOMAIN, PLATFORMS

from homeassistant.helpers.device_registry import async_get as async_get_device_registry, DeviceRegistry, DeviceEntry
_LOGGER = logging.getLogger(__name__)

store_obj: SprinkleStorage

async def async_setup(hass: HomeAssistant, config):

    #get the store object once, globally.
    global store_obj
    store_obj = await async_get_registry(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    hass.data.setdefault(const.DOMAIN, {
        "manager": None,
        "config_entries": {},
    })

    if hass.data[const.DOMAIN]["manager"] is None:
        _LOGGER.error("CREATING MANAGER")
        hass.data[const.DOMAIN]["manager"] = SprinkleSetupManager(hass, store_obj)


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

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info(f"Migrating configuration entry for {entry.title}")
    if entry.version > 1:
        # This means the user has downgraded from a future version
        return False
    if entry.version == 1:

        #Not the cleanest solution, but we will just delete the old devices with the old identifier.
        dev_reg: DeviceRegistry =  async_get_device_registry(hass)
        remove_ids: list[str] = []
        for device in dev_reg.devices.values():
            if entry.entry_id in device.config_entries:
                remove_ids.append(device.id)
        for remove_id in remove_ids:
            dev_reg.async_remove_device(remove_id)
        # dev_reg.async_update_device()
        #Migrate from v1 to v2. No data changes happened here, so just pass it down the same way
        hass.config_entries.async_update_entry(entry, data=entry.data, version=2)
        return True
    return False