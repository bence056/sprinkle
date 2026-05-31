import logging

from apischema.deserialization.coercion import false
from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .const import DOMAIN
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class IrrigationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Irrigation Controller creation flow."""
    VERSION = 2

    async def async_step_user(self, user_input=None):

        data_schema = {
            vol.Required("select_mode", default="virtual"):
                selector({
                    "select": {
                        "translation_key": "select_instance_mode",
                        "options": ["virtual", "hardware"]
                    }
                })
        }

        return self.async_show_form(
            step_id="mode",
            data_schema=vol.Schema(data_schema),
        )

    async def async_step_mode(self, user_input):
        if user_input['select_mode'] == "hardware":
            return self.async_abort(reason="wip")
        else:
            data_schema = vol.Schema({
                vol.Required("instance_name", default="Sprinkle Virtual Instance"): vol.All(
                    TextSelector(
                        TextSelectorConfig(
                            multiline=False,
                            type=TextSelectorType.TEXT
                        )
                    )
                )
            })
            return self.async_show_form(
                step_id="virtual_create",
                data_schema=data_schema,
            )

    async def async_step_virtual_create(self, user_input):
        return self.async_create_entry(title=user_input['instance_name'], data={})
