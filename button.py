from typing import Mapping, Any

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, ZONE_IDLE, ZONE_RUNNING
import asyncio

import logging

from .number import RainDelayDurationNumber
from .sensor import RainDelayExpiry
from .store import SprinkleCycleStep

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_button_entity"] = async_add_entities
    _LOGGER.info("added to hass.data")



class ZoneStartRunButton(ButtonEntity):
    def __init__(self, zone_id, name, device_info, zone_coordinator, zone_valves: list[str]):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_manual_run"
        self._attr_name = f"{name} Start/Stop Run"
        self._attr_device_info = device_info
        self._zone_coordinator = zone_coordinator
        self._zone_valves = zone_valves

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        await self._zone_coordinator.async_manual_run_button_pressed()

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

class RainDelaySetterButton(ButtonEntity):
    def __init__(self, device_info, rain_delay_value_entity: RainDelayDurationNumber, rain_delay_expiry_entity: RainDelayExpiry):
        self._attr_unique_id = f"{DOMAIN}_activate_rain_delay"
        self._attr_name = f"Activate Rain Delay"
        self._attr_device_info = device_info
        self._rain_delay_value = rain_delay_value_entity
        self._rain_delay_expiry = rain_delay_expiry_entity

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        hours = self._rain_delay_value.native_value
        self._rain_delay_expiry.recalculate_next_time(hours)
        coordinator = self.hass.data[DOMAIN]["coordinator"]
        await coordinator.async_update_rain_delay_expiry(self._rain_delay_expiry.native_value)


class CycleStartRunButton(ButtonEntity):
    def __init__(self, cycle_id, name, device_info, coordinator):
        self._attr_unique_id = f"{DOMAIN}_{cycle_id}_start_run"
        self._attr_name = f"{name} Start Run"
        self._attr_device_info = device_info
        self.coordinator = coordinator

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        pass