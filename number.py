from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_number_entity"] = async_add_entities


class ZoneRunDurationNumber(NumberEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{zone_id}_run_duration"
        self._attr_name = f"{name} Run Duration"
        self._attr_device_info = device_info
        self._attr_min_value = 1
        self._attr_max_value = 60
        self._attr_step = 1
        self._attr_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_value = 5

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._attr_value

    async def async_set_native_value(self, value):
        self._attr_value = value
        self.async_write_ha_state()



class RainDelayDurationNumber(NumberEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{zone_id}_rain_delay_duration"
        self._attr_name = f"{name} Rain Delay Duration"
        self._attr_device_info = device_info
        self._attr_native_min_value = 0
        self._attr_native_max_value = 72  # hours
        self._attr_native_step = 12
        self._attr_unit_of_measurement = UnitOfTime.HOURS
        self._attr_value = 0

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._attr_value

    async def async_set_native_value(self, value):
        self._attr_value = value

        self.async_write_ha_state()