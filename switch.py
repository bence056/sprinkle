from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_switch_entity"] = async_add_entities


class RainDelaySwitch(SwitchEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{zone_id}_rain_delay"
        self._attr_name = f"{name} Rain Delay"
        self._attr_device_info = device_info
        self._enabled = False

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def is_on(self):
        return self._enabled

    async def async_turn_on(self, **kwargs):
        self._enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._enabled = False
        self.async_write_ha_state()

