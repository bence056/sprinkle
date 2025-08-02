from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_button_entity"] = async_add_entities



class ZoneStartRunButton(ButtonEntity):
    def __init__(self, zone_id, name, device_info, duration_entity, status_entity, zone_valves: list[str]):
        self._attr_unique_id = f"{zone_id}_start_run"
        self._attr_name = f"{name} Start Run"
        self._attr_device_info = device_info
        self._duration_entity = duration_entity
        self._status_entity = status_entity
        self._zone_valves = zone_valves

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        minutes = self._duration_entity.native_value
        self._status_entity.set_status("running")
        self._status_entity.set_status("idle")


