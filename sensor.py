from datetime import timedelta
from typing import Mapping, Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTime
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt
from .const import DOMAIN
import asyncio

from .number import RainDelayDurationNumber


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_sensor_entity"] = async_add_entities


class ZoneStatusSensor(SensorEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_status"
        self._attr_name = f"{name} Status"
        self._attr_icon = "mdi:valve"
        self._attr_device_info = device_info
        self._status = "idle"  # or "running", "rain_delay"

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._status

    def set_status(self, status):
        self._status = status
        self.async_write_ha_state()





class ZoneNextScheduleSensor(SensorEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_next_schedule"
        self._attr_name = f"{name} Next Schedule"
        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._next_time = dt.now() + timedelta(hours=6)

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._next_time


class ZoneRainDelayExpiry(SensorEntity):
    def __init__(self, zone_id, name, device_info, rain_delay_input: RainDelayDurationNumber):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_expiry"
        self._zone_id = zone_id
        self._attr_name = f"{name} Expiry"
        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._next_time = dt.now() + timedelta(hours=rain_delay_input.native_value)
        self._rain_delay_input_entity: RainDelayDurationNumber = rain_delay_input
        rain_delay_input._assigned_expiry_entity = self

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._next_time

    def recalculate_next_time(self):
        self._next_time = dt.now() + timedelta(hours=self._rain_delay_input_entity.native_value)
        self.async_write_ha_state()
        coordinator = self.hass.data[DOMAIN]["coordinator"]
        coordinator.async_save_zone_changes(self.zone_id)

    @property
    def zone_id(self):
        return self._zone_id

    @property
    def rain_delay_input_entity(self):
        return self._rain_delay_input_entity



class CycleRemainingMinutes(SensorEntity):
    def __init__(self, cycle_id, name, device_info):
        self._attr_unique_id = f"{DOMAIN}_{cycle_id}_remaining_minutes"
        self._cycle_id = cycle_id
        self._attr_name = f"{name} Remaining Minutes"
        self._attr_device_info = device_info
        self._remaining_minutes = 3

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._remaining_minutes

    @property
    def native_unit_of_measurement(self):
        return UnitOfTime.MINUTES