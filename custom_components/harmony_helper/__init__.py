"""The harmony_helper component."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import (
    CONF_COMMAND,
    CONF_DEVICE,
    CONF_ICON,
    CONF_NAME,
    CONF_SOURCE,
)
from homeassistant.helpers.discovery import async_load_platform

DOMAIN = "harmony_helper"
PLATFORMS = ["binary_sensor"]

CONF_ACTIVITIES = "activities"
CONF_ACTIVITY = "activity"
CONF_ACTIVITY_DEVICE_LINKS = "activity_device_links"
CONF_COMMANDS = "commands"
CONF_DEVICE_COMMAND = "device_command"
CONF_LINK = "link"
CONF_LINKS = "links"

DATA_HARMONY_HELPER = "harmony_helper_data"

DEFAULT_ICON = "mdi:eye"
DEFAULT_ICONS = {
    "PowerOff": "mdi:power-off",
    "PowerOn": "mdi:power-on",
    "PowerToggle": "mdi:power",
    "Mute": "mdi:volume-mute",
    "VolumeDown": "mdi:volume-minus",
    "VolumeUp": "mdi:volume-plus",
    "ChannelDown": "mdi:menu-down",
    "ChannelUp": "mdi:menu-up",
    "DirectionDown": "mdi:arrow-down-bold",
    "DirectionLeft": "mdi:arrow-left-bold",
    "DirectionRight": "mdi:arrow-right-bold",
    "DirectionUp": "mdi:arrow-up-bold",
    "OK": "mdi:check-bold",
    "Stop": "mdi:stop",
    "Play": "mdi:play",
    "Rewind": "mdi:rewind",
    "Eject": "mdi:eject",
    "Pause": "mdi:pause",
    "FastForward": "mdi:fast-forward",
    "Record": "mdi:record",
    "SkipBack": "mdi:skip-backward",
    "SkipForward": "mdi:skip-forward",
    "Menu": "mdi:menu",
    "Subtitle": "mdi:subtitles",
    "Back": "mdi:arrow-left",
    "Green": "mdi:rectangle",
    "Red": "mdi:rectangle",
    "Blue": "mdi:rectangle",
    "Yellow": "mdi:rectangle",
    "Info": "mdi:information",
    "Movies": "mdi:filmstrip",
    "Play/Pause": "mdi:play-pause",
    "Replay": "mdi:replay",
    "Standby": "mdi:power-standby",
    "Search": "mdi:movie-search",
    "Sleep": "mdi:sleep",
    "Exit": "mdi:exit-to-app",
    "Home": "mdi:home",
    "Share": "mdi:share",
    ".": "mdi:circle-small",
    "0": "mdi:numeric-0",
    "1": "mdi:numeric-1",
    "2": "mdi:numeric-2",
    "3": "mdi:numeric-3",
    "4": "mdi:numeric-4",
    "5": "mdi:numeric-5",
    "6": "mdi:numeric-6",
    "7": "mdi:numeric-7",
    "8": "mdi:numeric-8",
    "9": "mdi:numeric-9",
}

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the Harmony Helper Binary Sensors."""

    hass.data[DATA_HARMONY_HELPER] = {}

    for harmony_helper, conf in config.get(DOMAIN).items():
        _LOGGER.debug("Setup %s.%s", DOMAIN, harmony_helper)

        source = conf.get(CONF_SOURCE)
        data = {}

        activity_device_links = {
            k: ActivityDeviceLink(k, v[CONF_ACTIVITY], v[CONF_DEVICE])
            for k, v in conf[CONF_ACTIVITY_DEVICE_LINKS].items()
        }

        for command in conf[CONF_COMMANDS]:
            if isinstance(command, str):
                helper_command = command
                command = Command(helper_command, None, None, None)
                for activity_device_link in activity_device_links.values():
                    command.links[activity_device_link.activity] = Link(
                        command, activity_device_link, None, None, None
                    )

            else:
                helper_command = command[CONF_COMMAND]
                links = command.get(CONF_LINKS, [])
                command = Command(
                    helper_command,
                    command.get(CONF_NAME),
                    command.get(CONF_DEVICE_COMMAND),
                    command.get(CONF_ICON),
                )
                for link in links:
                    if isinstance(link, str):
                        link_key = link
                        link = {}
                    else:
                        link_key = link.get(CONF_LINK)

                    activity_device_link = activity_device_links.get(link_key)
                    if activity_device_link is None:
                        _LOGGER.warning(
                            "Activity device link '%s' does not exist", link_key
                        )
                    else:

                        command.links[activity_device_link.activity] = Link(
                            command,
                            activity_device_link,
                            link.get(CONF_NAME),
                            link.get(CONF_DEVICE_COMMAND),
                            link.get(CONF_ICON),
                        )

            if helper_command in data:
                _LOGGER.warning(
                    "Command '%s' already exists, overwriting", helper_command
                )

            data[helper_command] = command

        hass.data[DATA_HARMONY_HELPER][harmony_helper] = {
            CONF_SOURCE: source,
            CONF_COMMANDS: data,
        }

        hass.async_create_task(
            async_load_platform(
                hass,
                BINARY_SENSOR_DOMAIN,
                DOMAIN,
                {DOMAIN: harmony_helper},
                config,
            )
        )

    return True


class CommandBase(object):
    def __init__(self, name: str, device_command: str, icon: str) -> None:
        self._name = name
        self._device_command = device_command
        self._icon = icon


class Command(CommandBase):
    def __init__(self, command: str, name: str, device_command: str, icon: str):
        super().__init__(name, device_command, icon)
        self._command = command
        self._links: dict[str, Link] = {}

    @property
    def command(self) -> str:
        """The harmony helper command."""
        return self._command

    @property
    def name(self) -> str:
        """The name."""
        ret = self._name
        if ret is None:
            ret = self.command
        return ret

    @property
    def device_command(self) -> str:
        """The harmony device command."""
        ret = self._device_command
        if ret is None:
            ret = self.command
        return ret

    @property
    def icon(self) -> str:
        """The current icon."""
        ret = self._icon
        if ret is None:
            ret = DEFAULT_ICONS.get(self.device_command)
            if ret is None:
                ret = DEFAULT_ICON
        return ret

    @property
    def links(self) -> dict[str, Link]:
        """The activity device links."""
        return self._links


class Link(CommandBase):
    def __init__(
        self,
        command: Command,
        link: ActivityDeviceLink,
        name: str,
        device_command: str,
        icon: str,
    ):
        super().__init__(name, device_command, icon)
        self._link = link
        self._command = command

    @property
    def name(self) -> str:
        """The link name."""
        ret = self._name
        if ret is None:
            ret = self._command.name
        return ret

    @property
    def device_command(self) -> str:
        """The link device command."""
        ret = self._device_command
        if ret is None:
            ret = self._command.device_command
        return ret

    @property
    def icon(self) -> str:
        """The link icon."""
        ret = self._icon
        if ret is None:
            ret = self._command.icon
        return ret

    @property
    def device(self) -> str:
        """The link activity."""
        return self._link.device


class ActivityDeviceLink(object):
    def __init__(self, name, activity, device) -> None:
        self._name = name
        self._activity = activity
        self._device = device

    @property
    def name(self) -> str:
        """The activity device link name."""
        return self._name

    @property
    def device(self) -> str:
        """The activity device link name."""
        return self._device

    @property
    def activity(self) -> str:
        """The activity device link name."""
        return self._activity
