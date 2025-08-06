import logging
import attr
from typing import List, cast, MutableMapping

from homeassistant.components.recorder.queries import attributes_ids_exist_in_states_with_fast_in_distinct
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import storage
from homeassistant.helpers.storage import Store
from tests.components.mqtt.test_diagnostics import default_entry_data
from .const import STORAGE_KEY, STORAGE_VERSION, DOMAIN, DATA_REGISTRY, SAVE_DELAY
from . import const
from homeassistant.util import dt

@attr.s(slots=True, frozen=False)
class SprinkleZone:

    zone_id = attr.field(type=str, default="")
    zone_name = attr.field(type=str, default="Unnamed Zone")
    zone_valves = attr.field(type=List[str], default=[])
    rain_delay_set_value = attr.field(type=int, default=0)
    rain_delay_end_time_seconds = attr.field(type=int, default=0)

@attr.s(slots=True, frozen=False)
class SprinkleCycleStep:
    zone_id = attr.field(type=str, default="")
    zone_minutes = attr.field(type=int, default=0)


@attr.s(slots=True, frozen=False)
class SprinkleCycle:

    cycle_id = attr.field(type=str, default="")
    cycle_name = attr.field(type=str, default="Unnamed Cycle")
    cycle_steps = attr.field(type=List[SprinkleCycleStep], default=[])



class SprinkleStorage:
    """Storage Object for the integration"""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.zones: MutableMapping[str, SprinkleZone] = {}
        self.cycles: MutableMapping[str, SprinkleCycle] = {}
        self.save_key: int = -1


    async def async_load(self):

        zones: MutableMapping[str, SprinkleZone] = {}
        cycles: MutableMapping[str, SprinkleCycle] = {}
        save_key = -1

        data = await self._store.async_load()
        if data is not None:
            if "save_key" in data:
                save_key = data["save_key"]

            if "zones" in data:
                for zone in data["zones"]:
                    zones[zone[const.ATTR_ZONE_ID]] = SprinkleZone(
                        zone_id = zone[const.ATTR_ZONE_ID],
                        zone_name = zone[const.ATTR_ZONE_NAME],
                        zone_valves = zone[const.ATTR_ZONE_VALVES],
                        rain_delay_set_value= zone[const.ATTR_RAIN_DELAY_CURRENT_SETTING],
                        rain_delay_end_time_seconds= zone[const.ATTR_RAIN_DELAY_END_TIME_SECONDS]
                    )

            if "cycles" in data:
                for cycle in data["cycles"]:
                    current_cycle_steps: list[SprinkleCycleStep] = []
                    for cycle_step in cycle[const.ATTR_CYCLE_STEPS]:
                        current_cycle_steps.append(SprinkleCycleStep(**cycle_step))
                    cycles[cycle[const.ATTR_CYCLE_ID]] = SprinkleCycle(
                        cycle_id = cycle[const.ATTR_CYCLE_ID],
                        cycle_name = cycle[const.ATTR_CYCLE_NAME],
                        cycle_steps = current_cycle_steps,
                    )

            self.zones = zones
            self.cycles = cycles
            self.save_key = save_key

            if save_key == -1:
                await self.async_factory_default()

    async def async_factory_default(self):
        self.save_key = 1

    async def async_save(self):
        await self._store.async_save(self.parse_save_data())

    def async_queue_save(self):
        self._store.async_delay_save(self.parse_save_data, SAVE_DELAY)


    @callback
    def parse_save_data(self) -> dict:
        self.save_key += 1
        store_data = {"save_key": self.save_key, "zones": [
            attr.asdict(zoneRaw) for zoneRaw in self.zones.values()
        ],
        "cycles": [
            attr.asdict(cycleRaw) for cycleRaw in self.cycles.values()
        ]}
        return store_data

    def create_zone(self, data: dict) -> SprinkleZone | None:
        if not "zone_id" in data:
            return None
        zone_data = SprinkleZone(**data)
        self.zones[zone_data.zone_id] = zone_data
        self.async_queue_save()
        return zone_data


    def remove_zone(self, zone_id: str) -> bool:
        if zone_id in self.zones:
            del self.zones[zone_id]
            self.async_queue_save()
            return True
        return False

    def create_or_modify_cycle(self, data: dict) -> SprinkleCycle:

        cycle_steps = data[const.ATTR_CYCLE_STEPS]

        cycle_steps_obj: list[SprinkleCycleStep] = []
        for step in cycle_steps:
            cycle_steps_obj.append(SprinkleCycleStep(step["zone_id"], step["zone_minutes"]))

        cycle_id = data[const.ATTR_CYCLE_ID]
        if cycle_id not in self.cycles:
            #Create
            new_cycle = SprinkleCycle(data[const.ATTR_CYCLE_ID], data[const.ATTR_CYCLE_NAME], cycle_steps_obj)
            self.cycles[new_cycle.cycle_id] = new_cycle
        else:
            #Modify
            new_cycle = self.cycles[cycle_id]
            new_cycle.cycle_steps = cycle_steps_obj

        self.async_queue_save()
        return new_cycle

    async def async_delete(self):
        await self._store.async_remove()
        self.zones = {}
        self.save_key = -1

    def remove_cycle(self, cycle_id: str) -> bool:
        if cycle_id in self.cycles:
            del self.cycles[cycle_id]
            self.async_queue_save()
            return True
        return False



async def async_get_registry(hass: HomeAssistant) -> SprinkleStorage:
    """Return the storage instance."""
    task = hass.data.get(DATA_REGISTRY)

    if task is None:

        async def _load_reg() -> SprinkleStorage:
            registry = SprinkleStorage(hass)
            await registry.async_load()
            return registry

        task = hass.data[DATA_REGISTRY] = hass.async_create_task(_load_reg())

    return cast(SprinkleStorage, await task)