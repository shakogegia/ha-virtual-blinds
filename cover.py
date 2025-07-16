from homeassistant.components.cover import (
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.helpers.entity import Entity
import asyncio

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the virtual blinds cover platform."""
    # Get the data from the config entry
    name = config_entry.data.get("name", "Virtual Blind")
    up_button = config_entry.data.get("up_button")
    down_button = config_entry.data.get("down_button")
    stop_button = config_entry.data.get("stop_button")
    up_travel_time = config_entry.data.get("up_travel_time", 30)
    down_travel_time = config_entry.data.get("down_travel_time", 30)
    unique_id = config_entry.entry_id

    # Create the blind entity
    blind = VirtualBlind(
        hass, name, up_button, down_button, stop_button, 
        up_travel_time, down_travel_time, unique_id
    )
    
    # Store the blind entity reference for access by button
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][f"{unique_id}_cover"] = blind
    
    # Add the entity
    async_add_entities([blind], update_before_add=True)


class VirtualBlind(CoverEntity):
    def __init__(self, hass, name, up_button, down_button, stop_button, up_travel_time, down_travel_time, unique_id):
        self._hass = hass
        self._name = name
        self._up_button = up_button
        self._down_button = down_button
        self._stop_button = stop_button
        self._up_travel_time = up_travel_time
        self._down_travel_time = down_travel_time
        self._unique_id = unique_id
        self._position = 0  # 0 = closed, 100 = open
        self._is_moving = False

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def current_cover_position(self):
        return self._position

    @property
    def is_closed(self):
        return self._position == 0

    @property
    def supported_features(self):
        return (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
            | CoverEntityFeature.SET_POSITION
        )

    @property
    def device_class(self):
        return "blind"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Virtual Components Inc.",
            "model": "Virtual Blinds 1.0",
        }

    async def async_open_cover(self, **kwargs):
        await self._move_to_position(100)

    async def async_close_cover(self, **kwargs):
        await self._move_to_position(0)

    async def async_stop_cover(self, **kwargs):
        if self._stop_button and self._is_moving:
            await self._press_button(self._stop_button)
        self._is_moving = False
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs):
        target = kwargs.get("position")
        await self._move_to_position(target)

    async def _move_to_position(self, target_pos):
        if target_pos == self._position:
            return

        direction = "up" if target_pos > self._position else "down"
        button = self._up_button if direction == "up" else self._down_button

        # Calculate time to move
        distance = abs(target_pos - self._position)
        travel_time = self._up_travel_time if direction == "up" else self._down_travel_time
        time_to_move = travel_time * (distance / 100)

        await self._press_button(button)

        self._is_moving = True
        self.async_write_ha_state()

        await asyncio.sleep(time_to_move)

        # Press stop button when movement should complete (if configured)
        # Only for intermediate positions - full open/close will stop naturally
        if self._stop_button and target_pos not in [0, 100]:
            await self._press_button(self._stop_button)

        self._position = target_pos
        self._is_moving = False
        self.async_write_ha_state()

    async def _press_button(self, entity_id):
        domain = entity_id.split(".")[0]
        await self._hass.services.async_call(
            domain=domain,
            service="press",
            target={"entity_id": entity_id},
            blocking=True
        )