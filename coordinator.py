import attr

import homeassistant.helpers.dispatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from .button import ZoneStartRunButton
from .const import DOMAIN, VERSION
from homeassistant.util import dt
from . import const
import logging

from .number import ZoneRunDurationNumber, RainDelayDurationNumber
from .sensor import ZoneStatusSensor, ZoneNextScheduleSensor, ZoneRainDelayExpiry
from .store import SprinkleStorage, SprinkleZone

_LOGGER = logging.getLogger(__name__)

class SprinkleCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store):
        self.hass = hass
        self.store: SprinkleStorage = store
        self.id = entry.entry_id
        self.entry = entry
        super().__init__(hass, _LOGGER, name=DOMAIN)


    async def load_entities(self):
        for key,value in self.store.zones.items():
            await self.async_create_zone(key, attr.asdict(value))



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


    async def async_update_zone_config(self, zone_id: str, data: dict):

        if const.ATTR_ZONE_DELETE in data:
            #Delete zone requested
            await self.async_delete_zone(zone_id)
        else:
            if zone_id in self.store.zones.keys():
                #Modify zone
                pass
            else:
                #Create new zone
                await self.async_create_zone(zone_id, data)


            homeassistant.helpers.dispatcher.async_dispatcher_send(self.hass, "sprinkle_update_dispatch")



    async def async_create_zone(self, zone_id: str, data: dict):
        # Create zone requested
        zone_name = data[const.ATTR_ZONE_NAME]
        zone_valves = data[const.ATTR_ZONE_VALVES]

        device_info = self.build_zone_device_info(zone_id, zone_name)

        zone_status_entity = ZoneStatusSensor(zone_id, zone_name, device_info)
        run_time_entity = ZoneRunDurationNumber(zone_id, zone_name, device_info)
        run_button_entity = ZoneStartRunButton(zone_id, zone_name, device_info, run_time_entity, zone_status_entity,
                                               zone_valves)
        rain_delay_time_entity = RainDelayDurationNumber(zone_id, zone_name, device_info)
        if const.ATTR_RAIN_DELAY_CURRENT_SETTING in data:
            rain_delay_time_entity._attr_value = data[const.ATTR_RAIN_DELAY_CURRENT_SETTING]
        rain_delay_expiry = ZoneRainDelayExpiry(zone_id, zone_name, device_info, rain_delay_time_entity)
        if const.ATTR_RAIN_DELAY_END_TIME_SECONDS in data:
            rain_delay_expiry._next_time = dt.as_local(dt.utc_from_timestamp(data[const.ATTR_RAIN_DELAY_END_TIME_SECONDS]))
        zone_next_schedule_entity = ZoneNextScheduleSensor(zone_id, zone_name, device_info)

        data[const.ATTR_RAIN_DELAY_CURRENT_SETTING] = rain_delay_time_entity.native_value
        data[const.ATTR_RAIN_DELAY_END_TIME_SECONDS] = int(rain_delay_expiry.native_value.timestamp())
        self.store.create_zone(data)

        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_numbers = self.hass.data[DOMAIN]["add_number_entity"]

        async_add_buttons([run_button_entity])
        async_add_sensors([zone_status_entity, zone_next_schedule_entity, rain_delay_expiry])
        async_add_numbers([rain_delay_time_entity])

    async def async_delete_zone(self, zone_id: str):
        device_registry = async_get_device_registry(self.hass)
        device_id = await self.async_get_device_id_from_zone(zone_id)
        _LOGGER.info(device_id)
        if device_id is not None:
            device_registry.async_remove_device(device_id)
            #remove from store.
            self.store.remove_zone(zone_id)
