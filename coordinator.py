import logging
from datetime import timedelta, datetime

import attr

import homeassistant.helpers.dispatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt
from . import const
from .button import ZoneStartRunButton, CycleStartRunButton, RainDelaySetterButton
from .const import DOMAIN, VERSION, CYCLE_RUNNING, CYCLE_IDLE
from .number import ZoneRunDurationNumber, RainDelayDurationNumber
from .sensor import ZoneStatusSensor, ZoneIrrigationFinishTime, RainDelayExpiry, CycleRemainingMinutes, \
    CycleStatusSensor
from .store import SprinkleStorage, SprinkleZone, SprinkleCycleStep

_LOGGER = logging.getLogger(__name__)

class SprinkleZoneCoordinator:
    def __init__(self, hass, main_coordinator, zone_id, zone_name, zone_valves):

        self.hass = hass
        self.coordinator: SprinkleCoordinator = main_coordinator
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.zone_valves = zone_valves
        self.controlling_cycle = None
        self.zone_running = False

        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_numbers = self.hass.data[DOMAIN]["add_number_entity"]

        device_info = self.build_zone_device_info()

        self.zone_status_entity = ZoneStatusSensor(zone_id, zone_name, device_info, self)
        self.zone_run_trigger_entity = ZoneStartRunButton(zone_id, zone_name, device_info, self, zone_valves)
        self.zone_run_timer_entity = ZoneRunDurationNumber(zone_id, zone_name, device_info, self)
        self.zone_finish_time_entity = ZoneIrrigationFinishTime(zone_id, zone_name, device_info, self)

        self.zone_manual_expiry_timestamp: datetime = dt.now()
        self.timer_callback_obj = None

        async_add_buttons([self.zone_run_trigger_entity])
        async_add_sensors([self.zone_status_entity, self.zone_finish_time_entity])
        async_add_numbers([self.zone_run_timer_entity])

    async def async_update_rain_delay_status(self):
        if self.coordinator.rain_delay_active:
            await self.async_stop_run()
            self.zone_status_entity.set_status(const.ZONE_RAIN_DELAY)
        else:
            self.zone_status_entity.set_status(const.ZONE_IDLE)

    @property
    def is_manually_running(self):
        return self.zone_running and self.controlling_cycle is None

    @property
    def is_running_from_cycle(self):
        return self.zone_running and self.controlling_cycle is not None

    @property
    def is_running(self):
        return self.zone_running


    async def async_manual_run_button_pressed(self):
        #TODO fix call order, zone start needs to cancel all active cycles, not just the assigned one.
        if self.is_manually_running:
            #stop the zone manual run.
            await self.async_stop_run()
        else:
            #stop active cycle and zone.
            await self.coordinator.async_stop_active_cycle()
            await self.coordinator.async_stop_active_zone()
            #run this zone manually.
            await self.async_start_manual_run()


    async def async_start_manual_run(self):
        if not self.is_running:
            if self.coordinator.rain_delay_active:
                return
            #Start a manual run cycle.
            self.zone_status_entity.set_status(const.ZONE_RUNNING_MANUAL)
            self.zone_running = True
            run_time = self.zone_run_timer_entity.native_value
            await self.async_start_run(run_time)

    async def async_start_run_from_cycle(self, cycle_coordinator, minutes):
        if self.coordinator.rain_delay_active:
            return
        self.controlling_cycle = cycle_coordinator
        self.zone_running = True
        self.zone_status_entity.set_status(const.ZONE_RUNNING_CYCLE)
        await self.async_start_run(minutes)

    async def async_start_run(self, minutes):
        if self.zone_status_entity.native_value == const.ZONE_IDLE:
            return
        end_time = dt.now() + timedelta(minutes=minutes)
        if self.timer_callback_obj:
            self.timer_callback_obj()
        self.zone_manual_expiry_timestamp = end_time
        self.zone_finish_time_entity.set_finish_timestamp(self.zone_manual_expiry_timestamp)
        self.coordinator.active_zone = self
        self.timer_callback_obj = async_track_point_in_time(self.hass, self.async_zone_timer_end_callback, end_time)
        await self.hass.services.async_call(
            "valve",  # domain
            "open_valve",  # service
            {"entity_id": self.zone_valves},  # service data
            blocking=True
        )


    async def async_stop_run(self):
        if self.timer_callback_obj:
            self.timer_callback_obj()
        self.zone_status_entity.set_status(const.ZONE_IDLE)
        self.zone_finish_time_entity.set_finish_timestamp(None)
        await self.hass.services.async_call(
            "valve",  # domain
            "close_valve",  # service
            {"entity_id": self.zone_valves},  # service data
            blocking=True
        )
        self.zone_running = False
        if self.controlling_cycle is not None:
            #notify the cycle that the zone finished its run.
            await self.controlling_cycle.async_advance_cycle_zone()
            self.controlling_cycle = None
        self.coordinator.active_zone = None

    async def async_zone_timer_end_callback(self, now: datetime):
        await self.async_stop_run()

    def build_zone_device_info(self):
        return {
            "identifiers": {(DOMAIN, self.zone_id)},
            "name": self.zone_name,
            "manufacturer": "bence056",
            "model": "Sprinkle Zone",
            "sw_version": VERSION
        }

class SprinkleCycleCoordinator:
    def __init__(self, hass, main_coordinator, cycle_id, cycle_name, cycle_steps: list[SprinkleCycleStep]):
        self.hass = hass
        self.coordinator: SprinkleCoordinator = main_coordinator
        self.cycle_id = cycle_id
        self.cycle_name = cycle_name
        self.cycle_steps: list[SprinkleCycleStep] = []
        self.current_step_index = -1

        device_info = self.build_cycle_device_info()

        self.cycle_status_entity = CycleStatusSensor(cycle_id, cycle_name, device_info, self)
        self.cycle_run_entity = CycleStartRunButton(cycle_id, cycle_name, device_info, self)
        self.cycle_end_timestamp_entity = CycleRemainingMinutes(cycle_id, cycle_name, device_info, self)

        async_add_buttons = self.hass.data[DOMAIN]["add_button_entity"]
        async_add_sensors = self.hass.data[DOMAIN]["add_sensor_entity"]
        async_add_buttons([self.cycle_run_entity])
        async_add_sensors([self.cycle_end_timestamp_entity, self.cycle_status_entity])

        self.assigned_zones: list[SprinkleZoneCoordinator] = []
        #load the zone coordinator references into an array.
        self.update_cycle_steps(cycle_steps)


    async def async_update_rain_delay_status(self):
        if self.coordinator.rain_delay_active:
            await self.async_stop_cycle()
            self.cycle_status_entity.set_status(const.CYCLE_RAIN_DELAY)
        else:
            self.cycle_status_entity.set_status(const.CYCLE_IDLE)


    @property
    def is_running(self):
        return self.current_step_index >= 0

    async def async_start_cycle_button_pressed(self):
        if self.is_running:
            await self.async_stop_cycle()
        else:
            #We need to stop the active cycle and zone before starting this.
            await self.coordinator.async_stop_active_cycle()
            await self.coordinator.async_stop_active_zone()
            await self.async_start_cycle()

    async def async_start_cycle(self):

        if self.current_step_index == -1 and len(self.assigned_zones) > 0:
            if self.coordinator.rain_delay_active:
                return
            #start a cycle.
            self.coordinator.active_cycle = self
            #set the estimated end timestamp on the cycle.
            total_minutes = 0
            for cycle_step in self.cycle_steps:
                total_minutes += cycle_step.zone_minutes
            self.cycle_end_timestamp_entity.set_finish_timestamp(dt.now() + timedelta(minutes=total_minutes))
            self.cycle_status_entity.set_status(CYCLE_RUNNING)
            await self.async_advance_cycle_zone()


    async def async_advance_cycle_zone(self):

        self.current_step_index+=1
        if self.current_step_index < len(self.assigned_zones):
            #start new zone run.
            await (self.assigned_zones[self.current_step_index]
                   .async_start_run_from_cycle(self, self.cycle_steps[self.current_step_index].zone_minutes))
        else:
            #No more zones to run, stop the cycle.
            await self.async_stop_cycle()




    async def async_stop_cycle(self):
        #first check if the index of the cycle step is still within bounds.
        # if it is, it means that the cycle was interrupted, so we need to manually stop the currently active zone.
        # if it isn't, it means that the last zone has ended its cycle, no need to manually stop it.
        if self.current_step_index < len(self.assigned_zones):
            if self.assigned_zones[self.current_step_index].is_running:
                #forcefully set the cycle to none, so the zone won't call back to go to the next step.
                self.assigned_zones[self.current_step_index].controlling_cycle = None
                await self.assigned_zones[self.current_step_index].async_stop_run()
        self.current_step_index = -1
        self.coordinator.active_cycle = None
        self.cycle_end_timestamp_entity.set_finish_timestamp(None)
        self.cycle_status_entity.set_status(CYCLE_IDLE)

    def update_cycle_steps(self, cycle_steps: list[SprinkleCycleStep]):
        self.cycle_steps = cycle_steps
        self.assigned_zones.clear()
        for cycle_step in self.cycle_steps:
            zone_coordinator = self.coordinator.zones[cycle_step.zone_id]
            if cycle_step is not None:
                self.assigned_zones.append(zone_coordinator)


    def build_cycle_device_info(self):
        return {
            "identifiers": {(DOMAIN, self.cycle_id)},
            "name": self.cycle_name,
            "manufacturer": "bence056",
            "model": "Sprinkle Cycle",
            "sw_version": VERSION
        }


class SprinkleCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, store):
        self.hass = hass
        self.store: SprinkleStorage = store
        self.id = entry.entry_id
        self.entry = entry
        self.rain_delay_setter_entity = None
        self.rain_delay_number_entity = None
        self.rain_delay_expiry_entity = None
        self.zones: dict[str, SprinkleZoneCoordinator] = {}
        self.cycles: dict[str, SprinkleCycleCoordinator] = {}
        self.active_zone = None
        self.active_cycle = None
        self.rain_delay_callback_obj = None
        self.rain_delay_active = False
        super().__init__(hass, _LOGGER, name=DOMAIN)


    async def async_setup(self):

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


        self.rain_delay_number_entity = RainDelayDurationNumber(device_info, self)
        self.rain_delay_expiry_entity = RainDelayExpiry(device_info, self)
        self.rain_delay_setter_entity = RainDelaySetterButton(device_info, self)

        async_add_sensors([self.rain_delay_expiry_entity])
        async_add_numbers([self.rain_delay_number_entity])
        async_add_buttons([self.rain_delay_setter_entity])

        for key,value in self.store.zones.items():
            await self.async_create_zone(key, attr.asdict(value))
        for key,value in self.store.cycles.items():
            await self.async_create_cycle(key, attr.asdict(value))

        #handle rain delay configuration upon starting.
        await self.async_process_rain_delay()

    async def async_rain_delay_setter_pressed(self):

        hours = self.rain_delay_number_entity.native_value
        self.rain_delay_expiry_entity.recalculate_next_time(hours)
        await self.async_update_rain_delay_expiry(self.rain_delay_expiry_entity.native_value)

    async def async_process_rain_delay(self):
        expiry_timestamp: datetime = dt.as_local(dt.utc_from_timestamp(self.store.config.rain_delay_end_time_seconds))
        #if we have a rain delay callback set, just end it, we will set it again
        if self.rain_delay_callback_obj:
            self.rain_delay_callback_obj()
        if expiry_timestamp > dt.now():
            #we set rain delay to on, and we create a callback for expiry.
            await self.async_activate_rain_delay()
            self.rain_delay_callback_obj = async_track_point_in_time(self.hass, self.async_rain_delay_expiry_callback, expiry_timestamp)
        else:
            await self.async_deactivate_rain_delay()

    async def async_rain_delay_expiry_callback(self, now: datetime):
        # we deactivate rain delay.
        await self.async_deactivate_rain_delay()

    async def async_activate_rain_delay(self):
        self.rain_delay_active = True
        for zone in self.zones.values():
            await zone.async_update_rain_delay_status()
        for cycle in self.cycles.values():
            await cycle.async_update_rain_delay_status()



    async def async_deactivate_rain_delay(self):
        #we cancel callbacks again just in case.
        if self.rain_delay_callback_obj:
            self.rain_delay_callback_obj()
        self.rain_delay_active = False
        for zone in self.zones.values():
            await zone.async_update_rain_delay_status()
        for cycle in self.cycles.values():
            await cycle.async_update_rain_delay_status()



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

    async def async_update_general_settings(self, data: dict):
        await self.async_stop_all_cycles_and_zones()
        self.store.settings.use_master_valve = data[const.ATTR_SETTINGS_USE_MASTER_VALVE];
        self.store.settings.master_valve_entity_id = data[const.ATTR_SETTINGS_MASTER_VALVE_ID]
        if(self.store.settings.use_master_valve == False):
            self.store.settings.master_valve_entity_id = ""
        self.store.settings.valve_toggle_delay_ms = data[const.ATTR_SETTINGS_VALVE_TOGGLE_DELAY_MS]
        self.store.async_queue_save();
        homeassistant.helpers.dispatcher.async_dispatcher_send(self.hass, "sprinkle_update_dispatch")


    async def async_update_zone_config(self, zone_id: str, data: dict):

        #stop any cycle and zone to be able to safely modify data.
        await self.async_stop_all_cycles_and_zones()

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

        # stop any cycle and zone to be able to safely modify data.
        await self.async_stop_all_cycles_and_zones()

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
        zone_toggle: ZoneStartRunButton = self.zones[zone_id].zone_run_trigger_entity
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
        self.zones[zone_id] = SprinkleZoneCoordinator(self.hass, self, zone_id, zone_name, zone_valves)
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
                    self.cycles[value.cycle_id].update_cycle_steps(value.cycle_steps)

            if store_modified:
                self.store.async_queue_save()

            for cycle_id in cycles_to_delete:
                await self.async_delete_cycle(cycle_id)



    async def async_create_cycle(self, cycle_id: str, data: dict):

        stored_cycle = self.store.create_or_modify_cycle(data)
        if cycle_id not in self.cycles.keys():
            #create the cycle coordinator and entities
            self.cycles[cycle_id] = SprinkleCycleCoordinator(self.hass, self, cycle_id, stored_cycle.cycle_name, stored_cycle.cycle_steps)



    async def async_modify_cycle(self, cycle_id: str, data: dict):
        if cycle_id not in self.cycles.keys():
            return
        edited_cycle = self.store.create_or_modify_cycle(data)
        #update coordinator data as well.
        self.cycles[cycle_id].update_cycle_steps(edited_cycle.cycle_steps)

    async def async_delete_cycle(self, cycle_id: str):
        device_registry = async_get_device_registry(self.hass)
        device_id = await self.async_get_device_id_from_cycle(cycle_id)
        _LOGGER.info(device_id)
        if device_id is not None:
            device_registry.async_remove_device(device_id)
            #remove from store.
            self.store.remove_cycle(cycle_id)
            #remove its assigned coordinator as well.
            if cycle_id in self.cycles.keys():
                #stop any currently running cycle action
                await self.cycles[cycle_id].async_stop_cycle()
                del self.cycles[cycle_id]


    async def async_delete_config(self):
        """Wipe storage and config"""
        await self.store.async_delete()

    async def async_update_rain_delay_expiry(self, rain_delay_expiry_timestamp):

        new_time = int(rain_delay_expiry_timestamp.timestamp())
        if self.store.config.rain_delay_end_time_seconds != new_time:
            self.store.config.rain_delay_end_time_seconds = new_time
            self.store.async_queue_save()
            await self.async_process_rain_delay()

    async def async_stop_all_cycles_and_zones(self):
        for cycle in self.cycles.values():
            if cycle.is_running:
                await cycle.async_stop_cycle()
        for zone in self.zones.values():
            if zone.is_running:
                await zone.async_stop_run()
        _LOGGER.info("All zones and cycles have been stopped.")

    async def async_stop_active_cycle(self):
        if self.active_cycle is not None:
            await self.active_cycle.async_stop_cycle()

    async def async_stop_active_zone(self):
        if self.active_zone is not None:
            await self.active_zone.async_stop_run()

def try_get_coordinator(hass: HomeAssistant) -> SprinkleCoordinator:
    return hass.data[const.DOMAIN]["coordinator"]

