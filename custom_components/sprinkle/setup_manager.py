import asyncio
import logging
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import SprinkleCoordinator, try_get_coordinator
from .panel import async_unregister_panel, async_register_panel
from .const import DOMAIN, PLATFORMS
from .store import SprinkleStorage

_LOGGER = logging.getLogger(__name__)


def try_get_setup_manager(hass: HomeAssistant) -> SprinkleSetupManager:
    return hass.data[DOMAIN]["manager"]


class SprinkleSetupManager:

    def __init__(self, hass: HomeAssistant, store: SprinkleStorage):
        self.hass = hass
        self.store_obj: SprinkleStorage = store
        self._lock = asyncio.Lock()
        self._count = 0

    def get_registered_config_entries(self):
        return_array = []
        entry_set: dict[str, SprinkleCoordinator] = self.hass.data[DOMAIN]["config_entries"]
        for coordinator in entry_set.values():
            return_array.append({
                "entry_id": coordinator.entry.entry_id,
                "entry_name": coordinator.entry.title,
            })
        return return_array


    async def async_setup(self, entry: ConfigEntry):
        from .websocket import register_websockets
        entry.runtime_data = {}
        _LOGGER.error(f"Setting up coordinator for {entry.entry_id}")
        coordinator = SprinkleCoordinator(self.hass, entry, self.store_obj)
        self.hass.data[DOMAIN]["config_entries"][entry.entry_id] = coordinator
        await self.hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        await coordinator.async_setup()

        #
        # FOR SOME REASON, PANEL TRIES TO GET REGISTERED FOR EVERY CONFIG.
        #


        async with self._lock:
            if self._count == 0:
                self._count += 1
                # Register the websockets.
                _LOGGER.info(f"Registering websockets.")
                register_websockets(self.hass)
                # Setup the side panel.
                _LOGGER.info(f"Setting up Sprinkle Panel.")
                await async_register_panel(self.hass)


    async def async_unload(self, entry: ConfigEntry):

        coordinator: SprinkleCoordinator = try_get_coordinator(self.hass, entry)
        await coordinator.async_unload()
        del self.hass.data[DOMAIN]["config_entries"][entry.entry_id]

        async with self._lock:
            self._count -= 1
            if self._count == 0:
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
            self.store_obj.remove_entry(entry)
