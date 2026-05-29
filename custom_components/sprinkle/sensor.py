from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from .const import DOMAIN, ZONE_RUNNING_CYCLE, ZONE_IDLE, ZONE_RAIN_DELAY, ZONE_RUNNING_MANUAL, CYCLE_IDLE, CYCLE_RAIN_DELAY, CYCLE_RUNNING

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_sensor_entity"] = async_add_entities


class ZoneStatusSensor(SensorEntity):
    def __init__(self, zone_id, name, device_info, zone_coordinator):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_status"
        self._attr_name = f"{name} Status"
        self._zone_coordinator = zone_coordinator
        self.device_class = SensorDeviceClass.ENUM
        self.options = [ZONE_IDLE, ZONE_RUNNING_MANUAL, ZONE_RUNNING_CYCLE, ZONE_RAIN_DELAY]
        self._attr_icon = "mdi:valve"
        self._attr_device_info = device_info
        self._status = ZONE_IDLE

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._status

    def set_status(self, status):
        self._status = status
        self.async_write_ha_state()


class CycleStatusSensor(SensorEntity):
    def __init__(self, cycle_id, name, device_info, cycle_coordinator):
        self._attr_unique_id = f"{DOMAIN}_{cycle_id}_status"
        self._attr_name = f"{name} Status"
        self._coordinator = cycle_coordinator
        self.device_class = SensorDeviceClass.ENUM
        self.options = [CYCLE_IDLE, CYCLE_RUNNING, CYCLE_RAIN_DELAY]
        self._attr_icon = "mdi:sprinkler-variant"
        self._attr_device_info = device_info
        self._status = CYCLE_IDLE

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._status

    def set_status(self, status):
        self._status = status
        self.async_write_ha_state()







class ZoneIrrigationFinishTime(SensorEntity):
    def __init__(self, zone_id, name, device_info, zone_coordinator):
        self._attr_unique_id = f"{DOMAIN}_{zone_id}_finish_timestamp"
        self._attr_name = f"{name} Zone End Time"
        self._zone_coordinator = zone_coordinator
        self._attr_device_info = device_info
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._finish_time = None

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._finish_time

    def set_finish_timestamp(self, timestamp):
        self._finish_time = timestamp
        self.async_write_ha_state()


class RainDelayExpiry(SensorEntity):
    def __init__(self, device_info, coordinator):
        self._attr_unique_id = f"{DOMAIN}_rain_delay_expiry"
        self._attr_name = f"Rain Delay Expiry"
        self._attr_device_info = device_info
        self._coordinator = coordinator
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._next_time = dt.as_local(dt.utc_from_timestamp(self._coordinator.store.entry(self._coordinator.entry).config.rain_delay_end_time_seconds))

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._next_time

    def recalculate_next_time(self, set_hours):
        self._next_time = dt.now() + timedelta(hours=set_hours)
        self.async_write_ha_state()



class CycleRemainingMinutes(SensorEntity):
    def __init__(self, cycle_id, name, device_info, coordinator):
        self._attr_unique_id = f"{DOMAIN}_{cycle_id}_finish_timestamp"
        self._cycle_id = cycle_id
        self._coordinator = coordinator
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_name = f"{name} Cycle End Time"
        self._attr_device_info = device_info
        self._end_time = None

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def native_value(self):
        return self._end_time

    def set_finish_timestamp(self, timestamp):
        self._end_time = timestamp
        self.async_write_ha_state()