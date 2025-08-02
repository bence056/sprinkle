from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from .button import ZoneStartRunButton
from .const import DOMAIN, VERSION
import logging

from .number import ZoneRunDurationNumber, RainDelayDurationNumber
from .sensor import ZoneStatusSensor, ZoneNextScheduleSensor
from .switch import RainDelaySwitch

_LOGGER = logging.getLogger(__name__)

class SprinkleCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store):
        self.hass = hass
        self.store = store
        self.id = entry.entry_id
        self.entry = entry
        super().__init__(hass, _LOGGER, name=DOMAIN)

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

    async def async_create_zone(self,  zone_name: str, zone_id: str, zone_valves: list[str]):
        device_info = self.build_zone_device_info(zone_id, zone_name)

        zone_status_entity = ZoneStatusSensor(zone_id, zone_name, device_info)
        run_time_entity = ZoneRunDurationNumber(zone_id, zone_name, device_info)
        run_button_entity = ZoneStartRunButton(zone_id, zone_name, device_info, run_time_entity, zone_status_entity, zone_valves)
        rain_delay_time_entity = RainDelayDurationNumber(zone_id, zone_name, device_info)
        rain_delay_switch_entity = RainDelaySwitch(zone_id, zone_name, device_info)
        zone_next_schedule_entity = ZoneNextScheduleSensor(zone_id, zone_name, device_info)

        async_add_switches = self.hass.data[DOMAIN]["add_switch_entity"]
        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_numbers = self.hass.data[DOMAIN]["add_number_entity"]

        async_add_switches([rain_delay_switch_entity])
        async_add_buttons([run_button_entity])
        async_add_sensors([zone_status_entity, zone_next_schedule_entity])
        async_add_numbers([rain_delay_time_entity])


    async def async_delete_zone(self, zone_id: str):
        device_registry = async_get_device_registry(self.hass)
        device_id = await self.async_get_device_id_from_zone(zone_id)
        if device_id is not None:
            device_registry.async_remove_device(device_id)
