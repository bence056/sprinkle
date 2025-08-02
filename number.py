
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
import asyncio

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    #save the callback to the dataset for later use.
    hass.data[DOMAIN]["add_number_entity"] = async_add_entities