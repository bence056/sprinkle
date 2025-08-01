from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .framework.zone import async_create_zone_device
import logging

_LOGGER = logging.getLogger(__name__)

class SprinkleCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store):
        self.hass = hass
        self.store = store
        self.id = entry.entry_id
        self.entry = entry
        super().__init__(hass, _LOGGER, name=DOMAIN)

    async def async_create_zone(self,  zone_name: str, zone_id: str, zone_valves: list[str]):
        await async_create_zone_device(self.hass, zone_name, zone_id, zone_valves)
        _LOGGER.info(f"Zone device and entities created for {zone_name}")