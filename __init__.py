from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging
from .const import *

from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.components import panel_custom

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

    # create the default controller entities after controller flow creation.
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def handle_run_zone(call):
        entity_id = call.data["entity_id"]
        duration = call.data["duration"]
        for entity in hass.data[DOMAIN]["entities"]:
            if entity.entity_id == entity_id:
                await entity.async_run_zone(duration)
                break

    hass.services.async_register(DOMAIN, "run_zone", handle_run_zone)

    # Reguister the custom panel
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=DOMAIN,
        frontend_url_path="",
        module_url="",
        sidebar_title="Irrigation Config",
        sidebar_icon="mdi:sprinkler-variant",
        require_admin=True,
        config={},
        config_panel_domain=DOMAIN,
    )

    return True
