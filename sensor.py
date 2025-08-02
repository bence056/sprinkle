from datetime import timedelta
from typing import Mapping, Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
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
        self._attr_unique_id = f"{zone_id}_status"
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
        self._attr_unique_id = f"{zone_id}_next_schedule"
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
        self._attr_unique_id = f"{zone_id}_expiry"
        self._attr_name = f"{name} Expiry"
        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._next_time = dt.now() + timedelta(hours=rain_delay_input.native_value)

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._next_time

