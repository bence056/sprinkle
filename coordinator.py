from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from .const import DOMAIN, VERSION
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
        device_info = self.build_zone_device_info(zone_id, zone_name)
        await async_create_zone_device(self.hass, zone_name, zone_id, zone_valves, device_info)
        _LOGGER.info(f"Zone device and entities created for {zone_name}")

    async def async_delete_zone(self, zone_id: str):
        device_registry = async_get_device_registry(self.hass)
        device_id = await self.async_get_device_id_from_zone(zone_id)
        if device_id is not None:
            device_registry.async_remove_device(device_id)

    def build_zone_device_info(self, zone_id: str, zone_name: str):
        return {
            "identifiers": {(DOMAIN, zone_id)},
            "name": zone_name,
            "manufacturer": "bence056",
            "model": "Sprinkle Virtual Irrigation",
            "sw_version": VERSION
        }

    async def async_get_device_id_from_zone(self, zone_id: str) -> str | None:
        dev_reg = async_get_device_registry(self.hass)
        identifier = (DOMAIN, zone_id)
        for device in dev_reg.devices.values():
            if identifier in device.identifiers:
                return device.id
        return None