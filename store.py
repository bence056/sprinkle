import logging
import attr
from typing import List, cast, MutableMapping

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



class SprinkleStorage:
    """Storage Object for the integration"""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.zones: MutableMapping[str, SprinkleZone] = {}
        self.save_key: int = -1


    async def async_load(self):

        zones: MutableMapping[str, SprinkleZone] = {}
        save_key = -1

        data = await self._store.async_load()
        if data is not None:
            if "save_key" in data:
                save_key = data["save_key"]

            if "zones" in data:
                for zone in data["zones"]:
                    zones[zone["zone_id"]] = SprinkleZone(
                        zone_id = zone[const.ATTR_ZONE_ID],
                        zone_name = zone[const.ATTR_ZONE_NAME],
                        zone_valves = zone[const.ATTR_ZONE_VALVES],
                        rain_delay_set_value= zone[const.ATTR_RAIN_DELAY_CURRENT_SETTING],
                        rain_delay_end_time_seconds= zone[const.ATTR_RAIN_DELAY_END_TIME_SECONDS]
                    )

            self.zones = zones
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