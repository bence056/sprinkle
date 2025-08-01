from datetime import timedelta

from homeassistant.util import dt
from ..const import VERSION, DOMAIN
from homeassistant.components.button import ButtonEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant

def build_zone_device_info(zone_id: str, zone_name: str):
    return {
        "identifiers": {("sprinkler", zone_id)},
        "name": zone_name,
        "manufacturer": "bence056",
        "model": "Sprinkle Virtual Irrigation",
        "sw_version": VERSION
    }

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



class ZoneStartRunButton(ButtonEntity):
    def __init__(self, zone_id, name, device_info, duration_entity, status_entity):
        self._attr_unique_id = f"{zone_id}_start_run"
        self._attr_name = f"{name} Start Run"
        self._attr_device_info = device_info
        self._duration_entity = duration_entity
        self._status_entity = status_entity

    @property
    def device_info(self):
        return self._attr_device_info

    async def async_press(self):
        minutes = self._duration_entity.native_value
        self._status_entity.set_status("running")
        self._status_entity.set_status("idle")



class RainDelaySwitch(SwitchEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{zone_id}_rain_delay"
        self._attr_name = f"{name} Rain Delay"
        self._attr_device_info = device_info
        self._enabled = True

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


class RainDelayDurationNumber(NumberEntity):
    def __init__(self, zone_id, name, device_info):
        self._attr_unique_id = f"{zone_id}_rain_delay_duration"
        self._attr_name = f"{name} Rain Delay Duration"
        self._attr_device_info = device_info
        self._attr_min_value = 12
        self._attr_max_value = 72  # hours
        self._attr_step = 12
        self._attr_unit_of_measurement = UnitOfTime.HOURS
        self._attr_value = 12

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._attr_value

    async def async_set_native_value(self, value):
        self._attr_value = value
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


async def async_create_zone_device(hass: HomeAssistant, zone_name: str, zone_id: str, zone_valves: list[str]):

    device_info = build_zone_device_info(zone_id, zone_name)
    zone_status_entity = ZoneStatusSensor(zone_id, zone_name, device_info)
    run_time_entity = ZoneRunDurationNumber(zone_id, zone_name, device_info)
    run_button_entity = ZoneStartRunButton(zone_id, zone_name, device_info, run_time_entity, zone_status_entity)
    rain_delay_time_entity = RainDelayDurationNumber(zone_id, zone_name, device_info)
    rain_delay_switch_entity = RainDelaySwitch(zone_id, zone_name, device_info)
    zone_next_schedule_entity = ZoneNextScheduleSensor(zone_id, zone_name, device_info)

    async_add_entities = hass.data[DOMAIN]["entity_registry"]
    async_add_entities([zone_status_entity, run_time_entity, run_button_entity, rain_delay_time_entity, rain_delay_switch_entity, zone_next_schedule_entity])



