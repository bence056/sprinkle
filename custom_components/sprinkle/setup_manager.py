import logging
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import SprinkleCoordinator, try_get_coordinator
from .panel import async_unregister_panel, async_register_panel
from .websocket import register_websockets
from .const import DOMAIN, PLATFORMS
from .store import SprinkleStorage

_LOGGER = logging.getLogger(__name__)


def try_get_setup_manager(hass: HomeAssistant) -> SprinkleSetupManager:
    return hass.data[DOMAIN]["manager"]


class SprinkleSetupManager:

    def __init__(self, hass: HomeAssistant, store: SprinkleStorage):
        self.hass = hass
        self.store_obj: SprinkleStorage = store

    async def async_setup(self, entry: ConfigEntry):
        coordinator = SprinkleCoordinator(self.hass, entry, self.store_obj)
        self.hass.data[DOMAIN]["config_entries"][entry.entry_id] = coordinator
        coordinator.store.load_entry(entry)
        await self.hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        await coordinator.async_setup()
        is_first_entry = len(self.hass.data[DOMAIN]["config_entries"]) == 1

        if is_first_entry:
            # Setup the side panel.
            _LOGGER.info(f"Setting up Sprinkle Panel.")
            await async_register_panel(self.hass)
            # Register the websockets.
            _LOGGER.info(f"Registering websockets.")
            register_websockets(self.hass)


    async def async_unload(self, entry: ConfigEntry):

        coordinator: SprinkleCoordinator = try_get_coordinator(self.hass, entry)
        await coordinator.async_unload()
        del self.hass.data[DOMAIN]["config_entries"][entry.entry_id]
        is_last_entry = len(self.hass.data[DOMAIN]["config_entries"]) == 0
        if is_last_entry:
            async_unregister_panel(self.hass)
        await self.hass.config_entries.async_unload_platforms(entry, PLATFORMS)


    async def async_remove(self, entry: ConfigEntry):

        #cant use try_get_coordinator because at this point the coordinator might not exist.
        # unload always runs before remove, so we can skip those steps.
        all_entries = self.hass.config_entries.async_entries(DOMAIN)
        if len(all_entries) == 0:
            #clear all data.
            _LOGGER.warning("Removing sprinkle configuration data!")
            del self.hass.data[DOMAIN]
            await self.store_obj.async_delete()
        else:
            #We only need to remove the stored data for this config entry.
            pass
