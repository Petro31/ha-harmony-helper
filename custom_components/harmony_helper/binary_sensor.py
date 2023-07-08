"""Support for controlling harmony activity commands with a single switch."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.compensation.sensor import ATTR_SOURCE
from homeassistant.components.remote import (
    ATTR_CURRENT_ACTIVITY,
    DOMAIN as REMOTE_DOMAIN,
    SERVICE_SEND_COMMAND,
)
from homeassistant.const import (
    ATTR_COMMAND,
    ATTR_ENTITY_ID,
    CONF_COMMAND,
    CONF_DEVICE,
    CONF_ICON,
    CONF_NAME,
    CONF_SOURCE,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.reload import async_setup_reload_service

from . import (
    CONF_ACTIVITY,
    CONF_ACTIVITY_DEVICE_LINKS,
    CONF_COMMANDS,
    CONF_DEVICE_COMMAND,
    CONF_LINK,
    CONF_LINKS,
    DATA_HARMONY_HELPER,
    DEFAULT_ICON,
    DOMAIN,
    PLATFORMS,
    Command,
)

_LOGGER = logging.getLogger(__name__)

ATTR_DEVICE = "device"


ACTIVITY_DEVICE_LINK_SCHEMA = {
    vol.Required(CONF_ACTIVITY): str,
    vol.Required(CONF_DEVICE): str,
}

LINK_SCHEMA = {
    vol.Required(CONF_LINK): str,
    vol.Optional(CONF_NAME): str,
    vol.Optional(CONF_ICON): str,
    vol.Optional(CONF_DEVICE_COMMAND): str,
}

COMMAND_SCHEMA = {
    vol.Required(CONF_COMMAND): str,
    vol.Optional(CONF_NAME): str,
    vol.Optional(CONF_DEVICE_COMMAND): str,
    vol.Optional(CONF_LINKS): vol.Any(str, LINK_SCHEMA),
}

HARMONY_HELPER_SCHEMA = {
    vol.Required(CONF_SOURCE): cv.entity_domain(REMOTE_DOMAIN),
    vol.Required(CONF_ACTIVITY_DEVICE_LINKS): {
        str: ACTIVITY_DEVICE_LINK_SCHEMA,
    },
    vol.Required(CONF_COMMANDS): vol.Any(str, COMMAND_SCHEMA),
}

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: HARMONY_HELPER_SCHEMA})}, extra=vol.ALLOW_EXTRA
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Compensation sensor."""
    if discovery_info is None:
        return

    harmony_helper = discovery_info[DOMAIN]
    conf = hass.data[DATA_HARMONY_HELPER][harmony_helper]

    commands: dict[str, Command] = conf[CONF_COMMANDS]

    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)

    source = conf[CONF_SOURCE]

    async_add_entities(
        [
            HarmonyHelperBinarySensor(
                f"{harmony_helper}_{command.command}",
                f"{source} {command.command}",
                source,
                command,
            )
            for command in commands.values()
        ]
    )

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SEND_COMMAND, {}, "async_send_command"
    )


class HarmonyHelperBinarySensor(BinarySensorEntity):
    """Representation of a harmony activity device switch."""

    def __init__(
        self, unique_id: str, name: str, source: str, command: Command
    ) -> None:
        self._unique_id = unique_id
        self._name = name
        self._source = source
        self._command = command
        self._state = None
        self._link = None
        self._icon = DEFAULT_ICON

    async def async_added_to_hass(self):
        """Handle added to Hass."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source],
                self._async_harmony_helper_sensor_state_listener,
            )
        )

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of this switch."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the switch."""
        return self._state

    @property
    def name(self):
        """Return the name of the switch."""
        return self._link.name if self._link else self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the switch."""
        ret = {
            ATTR_SOURCE: self._source,
        }
        if self._link:
            ret[ATTR_COMMAND] = self._link.device_command
            ret[ATTR_DEVICE] = self._link.device
        return ret

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._link.icon if self._link else self._icon

    def _service_arguments(self):
        args = ()
        kwargs = {}
        if self._link:
            args = (
                REMOTE_DOMAIN,
                SERVICE_SEND_COMMAND,
                {
                    ATTR_DEVICE: self._link.device,
                    ATTR_COMMAND: self._link.device_command,
                }
            )
            kwargs = {'blocking': True, 'target':{ATTR_ENTITY_ID: self._source}, 'context': self._context}
        
        return args, kwargs

    def send_command(self):
        """Send a command to the source."""
        args, kwargs = self._service_arguments()
        if args or kwargs:
            self.hass.services.call(*args, **kwargs)

    async def async_send_command(self):
        """Send a command to the source."""
        args, kwargs = self._service_arguments()
        if args or kwargs:
            await self.hass.services.async_call(*args, **kwargs)

    @callback
    def _async_harmony_helper_sensor_state_listener(self, event):
        """Handle sensor state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        activity = new_state.attributes.get(ATTR_CURRENT_ACTIVITY, "")

        if activity in self._command.links:
            self._link = self._command.links[activity]
            self._state = STATE_ON
        else:
            self._state = STATE_OFF

        self.async_write_ha_state()
