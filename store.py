import logging
import attr
from typing import List, cast

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import storage
from homeassistant.helpers.storage import Store
from .const import STORAGE_KEY, STORAGE_VERSION, DOMAIN, DATA_REGISTRY

@attr.s(slots=True, frozen=True)
class ZoneData:

    id = attr.field(type=str, default="")
    name = attr.field(type=str, default="Unnamed Zone")
    assigned_valves = attr.field(type=List[str], default=[])



class SprinkleStorage:
    """Storage Object for the integration"""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.zones: List[ZoneData] = []
        self.save_key: int = -1


    async def async_load(self):

        zones: List[ZoneData] = []
        save_key = -1

        data = await self._store.async_load()

        if "save_key" in data:
            save_key = data["save_key"]

        if "zones" in data:
            for zone in data["zones"]:
                zones.append(ZoneData(
                    id = zone["id"],
                    name = zone["name"],
                    assigned_valves = zone["valves"]
                ))

        self.zones = zones
        self.save_key = save_key

        if save_key == -1:
            await self.async_factory_default()

    async def async_factory_default(self):
        self.save_key = 1

    async def async_save(self):
        await self._store.async_save(self.parse_save_data())


    @callback
    def parse_save_data(self) -> dict:
        self.save_key += 1
        store_data = {"save_key": self.save_key, "zones": [
            attr.asdict(zone) for zone in self.zones
        ]}
        return store_data

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