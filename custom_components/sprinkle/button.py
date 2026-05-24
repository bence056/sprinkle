import logging
from typing import Mapping, Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_button_entity"] = async_add_entities
    _LOGGER.info("added to hass.data")



class ZoneStartRunButton(ButtonEntity):
    def __init__(self, zone_id, name, device_info, zone_coordinator, zone_valves: list[str]):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_manual_run"
        self._attr_name = f"{name} Start/Stop Zone"
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
    def __init__(self, device_info, coordinator):
        self._attr_unique_id = f"{DOMAIN}_activate_rain_delay"
        self._attr_name = f"Activate Rain Delay"
        self._attr_device_info = device_info
        self._coordinator = coordinator

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        await self._coordinator.async_rain_delay_setter_pressed()


class CycleStartRunButton(ButtonEntity):
    def __init__(self, cycle_id, name, device_info, coordinator):
        self._attr_unique_id = f"{DOMAIN}_{cycle_id}_cycle_run"
        self._attr_name = f"{name} Start/Stop Cycle"
        self._attr_device_info = device_info
        self.coordinator = coordinator

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        await self.coordinator.async_start_cycle_button_pressed()