from datetime import timedelta, datetime

import attr

import homeassistant.helpers.dispatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.event import async_track_point_in_time
from .button import ZoneStartRunButton, CycleStartRunButton, RainDelaySetterButton
from .const import DOMAIN, VERSION
from homeassistant.util import dt
from . import const
import logging

from .number import ZoneRunDurationNumber, RainDelayDurationNumber
from .sensor import ZoneStatusSensor, ZoneIrrigationFinishTime, RainDelayExpiry, CycleRemainingMinutes
from .store import SprinkleStorage, SprinkleZone, SprinkleCycleStep, SprinkleCycle

_LOGGER = logging.getLogger(__name__)

class SprinkleZoneCoordinator:
    def __init__(self, hass, zone_id, zone_name, zone_valves):

        self.hass = hass
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.zone_valves = zone_valves

        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_numbers = self.hass.data[DOMAIN]["add_number_entity"]

        device_info = self.build_zone_device_info(zone_id, zone_name)

        self.zone_status_entity = ZoneStatusSensor(zone_id, zone_name, device_info, self)
        self.zone_run_trigger_entity = ZoneStartRunButton(zone_id, zone_name, device_info, self, zone_valves)
        self.zone_run_timer_entity = ZoneRunDurationNumber(zone_id, zone_name, device_info, self)
        self.zone_finish_time_entity = ZoneIrrigationFinishTime(zone_id, zone_name, device_info, self)

        self.zone_manual_expiry_timestamp: datetime = dt.now()
        self.timer_callback_obj = None

        async_add_buttons([self.zone_run_trigger_entity])
        async_add_sensors([self.zone_status_entity, self.zone_finish_time_entity])
        async_add_numbers([self.zone_run_timer_entity])


    async def async_manual_run_button_pressed(self):
        if self.zone_status_entity.native_value == const.ZONE_IDLE:
            await self.async_start_manual_run()
        elif self.zone_status_entity.native_value == const.ZONE_RUNNING:
            await self.async_stop_run()


    async def async_start_manual_run(self):
        if self.zone_status_entity.native_value == const.ZONE_IDLE:
            #Start a manual run cycle.
            self.zone_status_entity.set_status(const.ZONE_RUNNING)
            run_time = self.zone_run_timer_entity.native_value
            await self.async_start_run(run_time)

    async def async_start_run(self, minutes):
        if self.zone_status_entity.native_value == const.ZONE_IDLE:
            return

        end_time = dt.now() + timedelta(seconds=minutes)
        if self.timer_callback_obj:
            self.timer_callback_obj()
        self.zone_manual_expiry_timestamp = end_time
        self.zone_finish_time_entity.set_finish_timestamp(self.zone_manual_expiry_timestamp)
        self.timer_callback_obj = async_track_point_in_time(self.hass, self.async_zone_timer_end_callback, end_time)


    async def async_stop_run(self):
        if self.timer_callback_obj:
            self.timer_callback_obj()
        self.zone_status_entity.set_status(const.ZONE_IDLE)
        self.zone_finish_time_entity.set_finish_timestamp(None)

    async def async_zone_timer_end_callback(self, now: datetime):
        await self.async_stop_run()

    def build_zone_device_info(self, zone_id: str, zone_name: str):
        return {
            "identifiers": {(DOMAIN, zone_id)},
            "name": zone_name,
            "manufacturer": "bence056",
            "model": "Sprinkle Zone",
            "sw_version": VERSION
        }


class SprinkleCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store):
        self.hass = hass
        self.store: SprinkleStorage = store
        self.id = entry.entry_id
        self.entry = entry
        self.zones: dict[str, SprinkleZoneCoordinator] = {}
        super().__init__(hass, _LOGGER, name=DOMAIN)


    async def load_entities(self):

        await self.async_create_config_entities()

        for key,value in self.store.zones.items():
            await self.async_create_zone(key, attr.asdict(value))
        for key,value in self.store.cycles.items():
            await self.async_create_cycle(key, attr.asdict(value))

    async def async_create_config_entities(self):

        device_info = {
            "identifiers": {(DOMAIN, self.entry.unique_id)},
            "name": const.NAME,
            "model": const.NAME,
            "sw_version": const.VERSION,
            "manufacturer": const.MANUFACTURER
        }

        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_numbers = self.hass.data[DOMAIN]["add_number_entity"]

        rain_delay_number_entity = RainDelayDurationNumber(device_info)
        rain_delay_expiry_entity = RainDelayExpiry(device_info, self.store.config.rain_delay_end_time_seconds)
        rain_delay_setter_entity = RainDelaySetterButton(device_info, rain_delay_number_entity, rain_delay_expiry_entity)

        config_entities = {
            "rain_delay_number": rain_delay_number_entity,
            "rain_delay_expiry": rain_delay_expiry_entity,
            "rain_delay_setter": rain_delay_setter_entity
        }

        self.hass.data[DOMAIN]["config"]["entities"] = config_entities

        async_add_sensors([rain_delay_expiry_entity])
        async_add_numbers([rain_delay_number_entity])
        async_add_buttons([rain_delay_setter_entity])



    def build_cycle_device_info(self, cycle_id: str, cycle_name: str):
        return {
            "identifiers": {(DOMAIN, cycle_id)},
            "name": cycle_name,
            "manufacturer": "bence056",
            "model": "Sprinkle Cycle",
            "sw_version": VERSION
        }

    async def async_get_device_id_from_zone(self, zone_id: str) -> str | None:
        dev_reg = async_get_device_registry(self.hass)
        identifier = (DOMAIN, zone_id)
        for device in dev_reg.devices.values():
            if identifier in device.identifiers:
                return device.id
        return None

    async def async_get_device_id_from_cycle(self, cycle_id: str) -> str | None:
        dev_reg = async_get_device_registry(self.hass)
        identifier = (DOMAIN, cycle_id)
        for device in dev_reg.devices.values():
            if identifier in device.identifiers:
                return device.id
        return None


    async def async_update_zone_config(self, zone_id: str, data: dict):

        if const.ATTR_ZONE_DELETE in data:
            #Delete zone requested
            await self.async_delete_zone(zone_id)
        else:
            if zone_id in self.store.zones.keys():
                #Modify zone
                await self.async_modify_zone(zone_id, data)
            else:
                #Create new zone
                await self.async_create_zone(zone_id, data)

        homeassistant.helpers.dispatcher.async_dispatcher_send(self.hass, "sprinkle_update_dispatch")

    async def async_update_cycle_config(self, cycle_id: str, data: dict):

        if const.ATTR_CYCLE_DELETE in data:
            # Delete cycle requested
            await self.async_delete_cycle(cycle_id)
        else:
            if cycle_id in self.store.cycles.keys():
                # Modify cycle
                await self.async_modify_cycle(cycle_id, data)
            else:
                # Create new cycle
                await self.async_create_cycle(cycle_id, data)

        homeassistant.helpers.dispatcher.async_dispatcher_send(self.hass, "sprinkle_update_dispatch")

    async def async_modify_zone(self, zone_id: str, data: dict):
        if const.ATTR_ZONE_VALVES not in data:
            return
        if zone_id not in self.zones.keys():
            return
        #stop running the zone to prevent softlocks
        await self.zones[zone_id].async_stop_run()
        #edit the data on the toggle entity to represent new valves.
        zone_toggle: ZoneStartRunButton = self.zones[zone_id].zone_run_timer_entity
        zone_toggle.zone_valves = data[const.ATTR_ZONE_VALVES]
        #Edit it in the serializable data as well.
        zone_serializable: SprinkleZone = self.store.zones[zone_id]
        zone_serializable.zone_valves = data[const.ATTR_ZONE_VALVES]
        self.store.async_queue_save()

    async def async_create_zone(self, zone_id: str, data: dict):
        # Create zone requested
        zone_name = data[const.ATTR_ZONE_NAME]
        zone_valves = data[const.ATTR_ZONE_VALVES]

        # create zone coordinator. It will create the entities as well.
        self.zones[zone_id] = SprinkleZoneCoordinator(self.hass, zone_id, zone_name, zone_valves)



        self.store.create_zone(data)



    async def async_delete_zone(self, zone_id: str):

        # stop zone and remove coordinator.
        if zone_id in self.zones.keys():
            await self.zones[zone_id].async_stop_run()
            del self.zones[zone_id]

        device_registry = async_get_device_registry(self.hass)
        device_id = await self.async_get_device_id_from_zone(zone_id)
        _LOGGER.info(device_id)
        if device_id is not None:
            device_registry.async_remove_device(device_id)
            #remove from store.
            self.store.remove_zone(zone_id)

            #check if there are cycles that contain this zone.
            cycle_set = self.hass.data[DOMAIN]["cycles"]
            cycles_to_delete: list[str] = []
            store_modified = False
            for key,value in self.store.cycles.items():

                to_remove: list[SprinkleCycleStep] = []
                for cycle_step in value.cycle_steps:
                    if cycle_step.zone_id == zone_id:
                        to_remove.append(cycle_step)

                for rem in to_remove:
                    value.cycle_steps.remove(rem)
                    store_modified = True

                #if a cycle has no steps left, mark it for removal.
                if len(value.cycle_steps) == 0:
                    cycles_to_delete.append(value.cycle_id)

                #check if we actually removed some zones from the list, if we did, we can follow up with the next modification.
                if len(to_remove) > 0:
                    cycle_run_entity: CycleStartRunButton = cycle_set[value.cycle_id]["run_trigger"]
                    cycle_run_entity._cycle_steps = value.cycle_steps

            if store_modified:
                self.store.async_queue_save()

            for cycle_id in cycles_to_delete:
                await self.async_delete_cycle(cycle_id)



    async def async_create_cycle(self, cycle_id: str, data: dict):

        cycle_name = data[const.ATTR_CYCLE_NAME]
        cycle_steps: data[const.ATTR_CYCLE_STEPS]

        device_info = self.build_cycle_device_info(cycle_id, cycle_name)

        cycle_obj = self.store.create_or_modify_cycle(data)

        cycle_run_entity = CycleStartRunButton(cycle_id, cycle_name, device_info, cycle_obj.cycle_steps)
        cycle_remaining_time_entity = CycleRemainingMinutes(cycle_id, cycle_name, device_info)

        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_buttons([cycle_run_entity])
        async_add_sensors([cycle_remaining_time_entity])

        # store them in hass.data for later reference.

        cycle_structure = {
            "run_trigger": cycle_run_entity,
            "remaining_minutes": cycle_remaining_time_entity
        }
        self.hass.data[DOMAIN]["cycles"][cycle_id] = cycle_structure

    async def async_modify_cycle(self, cycle_id: str, data: dict):
        cycle_set = self.hass.data[DOMAIN]["cycles"]
        if cycle_id not in cycle_set:
            return
        edited_cycle = self.store.create_or_modify_cycle(data)
        #update entity data as well.
        cycle_run_entity: CycleStartRunButton = cycle_set[cycle_id]["run_trigger"]
        cycle_run_entity._cycle_steps = edited_cycle.cycle_steps

    async def async_delete_cycle(self, cycle_id: str):
        device_registry = async_get_device_registry(self.hass)
        device_id = await self.async_get_device_id_from_cycle(cycle_id)
        _LOGGER.info(device_id)
        if device_id is not None:
            device_registry.async_remove_device(device_id)
            #remove from store.
            self.store.remove_cycle(cycle_id)


    async def async_delete_config(self):
        """Wipe storage and config"""
        await self.store.async_delete()

    async def async_update_rain_delay_expiry(self, rain_delay_expiry_timestamp):

        new_time = int(rain_delay_expiry_timestamp.timestamp())
        if self.store.config.rain_delay_end_time_seconds != new_time:
            self.store.config.rain_delay_end_time_seconds = new_time
            self.store.async_queue_save()


