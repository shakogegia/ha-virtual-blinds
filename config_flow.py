from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.selector as selector

from .const import DOMAIN


class VirtualBlindsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): selector.TextSelector(),
                vol.Required("up_button"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="button")
                ),
                vol.Required("down_button"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="button")
                ),
                vol.Required("stop_button"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="button")	
                ),
                vol.Required("up_travel_time"): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=60,
                        unit_of_measurement="s",
                        mode="box"
                    )
                ),
                vol.Required("down_travel_time"): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=60,
                        unit_of_measurement="s",
                        mode="box"
                    )
                ),
            }),
            errors=errors
        )