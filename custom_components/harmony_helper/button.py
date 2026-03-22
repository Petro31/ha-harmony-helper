"""Support for controlling harmony activity commands with a single switch."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.components.remote import (
    ATTR_CURRENT_ACTIVITY,
    DOMAIN as REMOTE_DOMAIN,
    SERVICE_SEND_COMMAND,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_COMMAND, ATTR_ENTITY_ID
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import DATA_HARMONY_HELPER
from .const import ATTR_SOURCE, DEFAULT_ICON
from .helpers import Command, Link, get_harmony_remote_device_id

_LOGGER = logging.getLogger(__name__)

ATTR_DEVICE = "device"


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
                HarmonyHelperButton(
                    hass,
                    f"{item.name}_{command.command}",
                    item.source,
                    command,
                    get_harmony_remote_device_id(entity_registry, item.source),
                )
                for item in config
                for command in item.commands
            ]
        )


class HarmonyHelperButton(ButtonEntity):
    """Representation of a harmony activity command."""

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: str,
        source: str,
        command: Command,
        device_id: str | None,
    ) -> None:
        """Initalize."""
        self._hass = hass
        self._attr_unique_id = unique_id
        self._attr_name = (
            f"{source.replace('_', ' ').replace('.', ' ').title()} {command.command}"
        )
        self._source = source
        self._command = command
        self._link: Link | None = None

        device_registry = dr.async_get(hass)
        if device_id is not None:
            self.device_entry = device_registry.async_get(device_id)

    async def async_added_to_hass(self):
        """Handle added to Hass."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source],
                self._async_update_links,
            )
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the switch."""
        ret = {
            ATTR_SOURCE: self._source,
        }
        if self._link:
            ret[ATTR_COMMAND] = self._link.device_command
            ret[ATTR_DEVICE] = self._link.device
        else:
            ret[ATTR_COMMAND] = None
            ret[ATTR_DEVICE] = None
        return ret

    @property
    def icon(self):
        """Return the icon to use, if any."""
        return self._link.icon if self._link else DEFAULT_ICON

    def _update_link(self, activity: str | None) -> None:
        """Update the linked activity."""
        if activity in self._command.links:
            self._link = self._command.links[activity]
        else:
            self._link = None

    @callback
    def _async_update_links(self, event: Event[EventStateChangedData]):
        """Handle sensor state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        self._update_link(new_state.attributes.get(ATTR_CURRENT_ACTIVITY))
        self.async_write_ha_state()

    async def async_press(self) -> None:
        """Press the button."""
        if self._link is None:
            if (state := self._hass.states.get(self._source)) is None:
                _LOGGER.warning(
                    "No source found for '%s' command: %s",
                    self._command.name,
                    self._source,
                )
                return

            if (activity := state.attributes.get(ATTR_CURRENT_ACTIVITY)) is None:
                _LOGGER.warning(
                    "No '%s' activity, skipping '%s' command",
                    self._source,
                    self._command.name,
                )
                return

            self._update_link(activity)

        await self.hass.services.async_call(
            REMOTE_DOMAIN,
            SERVICE_SEND_COMMAND,
            {
                ATTR_DEVICE: self._link.device,
                ATTR_COMMAND: self._link.device_command,
            },
            blocking=True,
            target={ATTR_ENTITY_ID: self._source},
            context=self._context,
        )
