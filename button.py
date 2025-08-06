from typing import Mapping, Any

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import asyncio

import logging

from .store import SprinkleCycleStep

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_button_entity"] = async_add_entities
    _LOGGER.info("added to hass.data")



class ZoneStartRunButton(ButtonEntity):
    def __init__(self, zone_id, name, device_info, duration_entity, status_entity, zone_valves: list[str]):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_start_run"
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

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "assigned_valves": self._zone_valves
        }

    @property
    def zone_valves(self):
        return self._zone_valves

    @zone_valves.setter
    def zone_valves(self, value):
        self._zone_valves = value
        self.async_write_ha_state()


class CycleStartRunButton(ButtonEntity):
    def __init__(self, cycle_id, name, device_info, cycle_steps: list[SprinkleCycleStep]):
        self._attr_unique_id = f"{DOMAIN}_{cycle_id}_start_run"
        self._attr_name = f"{name} Start Run"
        self._attr_device_info = device_info
        self._cycle_steps = cycle_steps

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        pass