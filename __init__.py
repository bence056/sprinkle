from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN
from .panel import (
    async_register_panel,
    async_unregister_panel
)

from homeassistant.helpers.device_registry import async_get as async_get_device_registry


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:


    # Create the controller device
    device_registry = async_get_device_registry(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        name=const.NAME,
        model=const.NAME,
        sw_version=const.VERSION,
        manufacturer=const.MANUFACTURER,
    )

    # Setup data configuration.
    hass.data.setdefault(DOMAIN, {"entities": []})
    hass.data[DOMAIN]["device_id"] = device.id

    #Setup the side panel.
    await panel.async_register_panel(hass)

    # create the default controller entities after controller flow creation.
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
