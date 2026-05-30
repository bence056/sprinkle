from datetime import timedelta
from typing import List, cast, MutableMapping

import attr
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.util import dt
from . import const
from .const import STORAGE_KEY, STORAGE_VERSION, DATA_REGISTRY, SAVE_DELAY


@attr.s(slots=True, frozen=False)
class SprinkleConfig:

    rain_delay_end_time_seconds = attr.field(type=int, default=int((dt.now() - timedelta(minutes=5)).timestamp()))

@attr.s(slots=True, frozen=False)
class SprinkleZone:

    zone_id = attr.field(type=str, default="")
    zone_name = attr.field(type=str, default="Unnamed Zone")
    zone_valves = attr.field(type=List[str], default=[])

@attr.s(slots=True, frozen=False)
class SprinkleCycleStep:
    zone_id = attr.field(type=str, default="")
    zone_minutes = attr.field(type=int, default=0)


@attr.s(slots=True, frozen=False)
class SprinkleCycle:

    cycle_id = attr.field(type=str, default="")
    cycle_name = attr.field(type=str, default="Unnamed Cycle")
    cycle_steps = attr.field(type=List[SprinkleCycleStep], default=[])


@attr.s(slots=True, frozen=False)
class SprinkleGeneralSettings:

    use_master_valve = attr.field(type=bool, default=False)
    master_valve_entity_id = attr.field(type=str, default="")
    valve_toggle_delay_ms = attr.field(type=int, default=500)


class SprinkleEntryStorage:

    def __init__(self, hass: HomeAssistant, entry_id: str, master: SprinkleStorage):
        self.master = master
        self.hass = hass
        self.entry_id = entry_id
        self.config = SprinkleConfig()
        self.settings = SprinkleGeneralSettings()
        self.zones: MutableMapping[str, SprinkleZone] = {}
        self.cycles: MutableMapping[str, SprinkleCycle] = {}

    async def async_load(self, data):

        if "config" in data:
            self.config = SprinkleConfig(**data["config"])

        if "settings" in data:
            self.settings = SprinkleGeneralSettings(**data["settings"])

        if "zones" in data:
            for zone in data["zones"]:
                self.zones[zone[const.ATTR_ZONE_ID]] = SprinkleZone(
                    zone_id=zone[const.ATTR_ZONE_ID],
                    zone_name=zone[const.ATTR_ZONE_NAME],
                    zone_valves=zone[const.ATTR_ZONE_VALVES],
                )

        if "cycles" in data:
            for cycle in data["cycles"]:
                current_cycle_steps: list[SprinkleCycleStep] = []
                for cycle_step in cycle[const.ATTR_CYCLE_STEPS]:
                    current_cycle_steps.append(SprinkleCycleStep(**cycle_step))
                self.cycles[cycle[const.ATTR_CYCLE_ID]] = SprinkleCycle(
                    cycle_id=cycle[const.ATTR_CYCLE_ID],
                    cycle_name=cycle[const.ATTR_CYCLE_NAME],
                    cycle_steps=current_cycle_steps,
                )


    def async_parse_save(self):
        return_data = {

            "config": attr.asdict(self.config),
            "settings": attr.asdict(self.settings),
            "zones": [
                attr.asdict(zoneRaw) for zoneRaw in self.zones.values()
            ],
            "cycles": [
                attr.asdict(cycleRaw) for cycleRaw in self.cycles.values()
            ]

        }

        return return_data


    def create_zone(self, data: dict) -> SprinkleZone | None:
        if not "zone_id" in data:
            return None
        zone_data = SprinkleZone(**data)
        self.zones[zone_data.zone_id] = zone_data
        self.master.async_queue_save()
        return zone_data


    def remove_zone(self, zone_id: str) -> bool:
        if zone_id in self.zones:
            del self.zones[zone_id]
            self.master.async_queue_save()
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

        self.master.async_queue_save()
        return new_cycle

    def remove_cycle(self, cycle_id: str) -> bool:
        if cycle_id in self.cycles:
            del self.cycles[cycle_id]
            self.master.async_queue_save()
            return True
        return False




class SprinkleStorage:
    """Storage Object for the integration"""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.entries: dict[str, SprinkleEntryStorage] = {}
        self.save_key: int = -1


    async def async_load(self):



        save_key = -1
        entries: dict[str, SprinkleEntryStorage] = {}

        data = await self._store.async_load()
        if data is not None:
            if "save_key" in data:
                save_key = data["save_key"]

            if "entries" in data:
                #We can pass the data to the entryStorage
                entry_dataset: dict = data["entries"]
                for entry_id, entry_data in entry_dataset.items():
                    entry_storage = SprinkleEntryStorage(self.hass, entry_id, self)
                    await entry_storage.async_load(entry_data)
                    entries[entry_id] = entry_storage

            self.entries = entries
            self.save_key = save_key

        else:
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
        store_data = {"save_key": self.save_key,
                      "entries": {
                          entry_id: entry_data.async_parse_save() for entry_id, entry_data in self.entries.items()
                      }
                      }
        return store_data

    def load_entry(self, entry: ConfigEntry) -> SprinkleEntryStorage:
        if not entry.entry_id in self.entries:
            self.entries[entry.entry_id] = SprinkleEntryStorage(self.hass, entry.entry_id, self)
            self.async_queue_save()
        return self.entries[entry.entry_id]

    def remove_entry(self, entry: ConfigEntry):
        if entry.entry_id in self.entries:
            del self.entries[entry.entry_id]
            self.async_queue_save()

    def entry(self, config_entry: ConfigEntry) -> SprinkleEntryStorage:
        return self.entries[config_entry.entry_id]

    def create_zone(self, entry: ConfigEntry, data: dict) -> SprinkleZone | None:
        return self.entry(entry).create_zone(data)


    def remove_zone(self, entry: ConfigEntry, zone_id: str) -> bool:
        return self.entry(entry).remove_zone(zone_id)

    def create_or_modify_cycle(self, entry: ConfigEntry, data: dict) -> SprinkleCycle:
       return self.entry(entry).create_or_modify_cycle(data)

    def remove_cycle(self, entry: ConfigEntry, cycle_id: str) -> bool:
        return self.entry(entry).remove_cycle(cycle_id)

    async def async_delete(self):
        await self._store.async_remove()
        self.save_key = -1

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