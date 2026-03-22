"""Support for controlling harmony activity commands with a single switch."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.remote import ATTR_CURRENT_ACTIVITY
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import DATA_HARMONY_HELPER
from .helpers import Command, get_harmony_remote_device_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize config entry."""
    entity_registry = er.async_get(hass)
    if (config := hass.data.get(DATA_HARMONY_HELPER)) is not None:
        async_add_entities(
            [
                HarmonyHelperBinarySensor(
                    hass,
                    item.name,
                    f"{item.source.replace('_', ' ').replace('.', ' ').title()} Control",
                    item.source,
                    item.commands,
                    get_harmony_remote_device_id(entity_registry, item.source),
                )
                for item in config
            ]
        )


class HarmonyHelperBinarySensor(BinarySensorEntity):
    """Representation of available activity commands."""

    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: str,
        name: str,
        source: str,
        commands: list[Command],
        device_id: str | None,
    ) -> None:
        """Initalize."""
        self.hass = hass
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._source = source
        self._commands = commands
        self._attr_device_class = BinarySensorDeviceClass.RUNNING

        device_registry = dr.async_get(hass)
        if device_id is not None:
            self.device_entry = device_registry.async_get(device_id)

    async def async_added_to_hass(self):
        """Handle added to Hass."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source],
                self._async_harmony_helper_sensor_state_listener,
            )
        )

    def _update_activity(self, activity: str | None) -> None:
        """Update the activity and links."""
        self._attr_is_on = False
        if activity is None:
            self.async_write_ha_state()
            return

        for command in self._commands:
            if activity in command.links:
                self._attr_is_on = True
                break

        self.async_write_ha_state()

    @callback
    def _async_harmony_helper_sensor_state_listener(
        self, event: Event[EventStateChangedData]
    ):
        """Handle sensor state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        self._update_activity(new_state.attributes.get(ATTR_CURRENT_ACTIVITY))
