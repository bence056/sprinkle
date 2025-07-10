from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    entity = TimedRunEntity("zone_1", "Front Yard", ["switch.valve_01", "switch.valve_02"])
    hass.data[DOMAIN]["entities"].append(entity)
    async_add_entities([entity])


class TimedRunEntity(Entity):

    def __init__(self, zone, name, valves):
        self._attr_unique_id = f"irrigation_zone_{zone}_timed_run"
        self._attr_name = f"{name} {zone} Timed Run"
        self._valves = valves
        self._duration = 0
        self.entity_id = f"{DOMAIN}.{zone}_timed_run"

    @property
    def extra_state_attributes(self):
        return {
            "duration": self._duration,
            "valves": self._valves
        }

    @property
    def state(self):
        return "idle"

    # @property
    # def device_info(self):
    #     return DeviceInfo(
    #         identifiers={(DOMAIN, f"zone_{self._attr_unique_id}")},
    #         name=self._attr_name,
    #         manufacturer="Unavailable",
    #         model="Virtual Irrigation Zone"
    #     )

    async def async_run_zone(self, duration_minutes: int):
        self._duration = duration_minutes

        for valve in self._valves:
            await self.hass.services.async_call("switch", "turn_on", {"entity_id": valve})

        await asyncio.sleep(duration_minutes * 60)

        for valve in self._valves:
            await self.hass.services.async_call("switch", "turn_off", {"entity_id": valve})

        self._duration = 0
        self.async_write_ha_state()