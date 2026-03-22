"""Constants."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

ATTR_SOURCE = "source"

CONF_ACTIVITIES = "activities"
CONF_ACTIVITY = "activity"
CONF_ACTIVITY_DEVICE_LINKS = "activity_device_links"
CONF_COMMANDS = "commands"
CONF_DEVICE_COMMAND = "device_command"
CONF_LINK = "link"
CONF_LINKS = "links"

PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON]
DEFAULT_ICON = "mdi:sync-off"
DOMAIN = "harmony_helper"

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
    "Back": "mdi:undo-variant",
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


@dataclass
class HarmonyHelperModule:
    """List of harmony helper platforms."""

    platforms: tuple[str, ...]
    entry: ConfigEntry
