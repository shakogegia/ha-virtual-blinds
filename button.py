from homeassistant.components.button import ButtonEntity
import asyncio

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the virtual blinds button platform."""
    name = config_entry.data.get("name", "Virtual Blind")
    down_button = config_entry.data.get("down_button")
    down_travel_time = config_entry.data.get("down_travel_time", 30)
    unique_id = config_entry.entry_id

    reset_button = VirtualBlindResetButton(
        hass, name, down_button, down_travel_time, unique_id
    )
    
    async_add_entities([reset_button], update_before_add=True)


class VirtualBlindResetButton(ButtonEntity):
    def __init__(self, hass, name, down_button, down_travel_time, unique_id):
        self._hass = hass
        self._name = f"{name} Reset to Closed"
        self._down_button = down_button
        self._down_travel_time = down_travel_time
        self._unique_id = f"{unique_id}_reset"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def icon(self):
        return "mdi:sync"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id.replace("_reset", ""))},
            "name": self._name.replace(" Reset to Closed", ""),
            "manufacturer": "Virtual Components Inc.",
            "model": "Virtual Blinds 1.0",
        }

    async def async_press(self):
        """Reset the blinds to closed position and sync virtual position."""
        if self._down_button:
            # Press the down button
            await self._press_button(self._down_button)
            
            # Wait for full travel time
            await asyncio.sleep(self._down_travel_time)
            
            # Update the stored cover entity position
            base_unique_id = self._unique_id.replace("_reset", "")
            cover_entity = self._hass.data.get(DOMAIN, {}).get(f"{base_unique_id}_cover")
            
            if cover_entity:
                cover_entity._position = 0
                cover_entity._is_moving = False
                cover_entity.async_write_ha_state()

    async def _press_button(self, entity_id):
        """Press a button entity."""
        domain = entity_id.split(".")[0]
        await self._hass.services.async_call(
            domain=domain,
            service="press",
            target={"entity_id": entity_id},
            blocking=True
        ) 