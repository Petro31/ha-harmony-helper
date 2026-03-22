"""The harmony_helper component."""

from dataclasses import dataclass
import logging

import voluptuous as vol

from homeassistant import config as conf_util
from homeassistant.components.remote import DOMAIN as REMOTE_DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_COMMAND,
    CONF_DEVICE,
    CONF_ICON,
    CONF_NAME,
    CONF_SOURCE,
    SERVICE_RELOAD,
)
from homeassistant.core import Event, HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.reload import async_reload_integration_platforms
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration
from homeassistant.util.hass_dict import HassKey

from .const import (
    CONF_ACTIVITY,
    CONF_ACTIVITY_DEVICE_LINKS,
    CONF_COMMANDS,
    CONF_DEVICE_COMMAND,
    CONF_LINK,
    CONF_LINKS,
    DOMAIN,
    PLATFORMS,
    HarmonyHelperModule,
)
from .helpers import ActivityDeviceLink, Command, Link

DATA_MODULE: HassKey[HarmonyHelperModule] = "harmony_helper_module"


@dataclass
class HarmonyHelperData:
    """Harmony Helper Data."""

    name: str
    source: str
    commands: list[Command]


DATA_HARMONY_HELPER: HassKey[list[HarmonyHelperData]] = "harmony_helper_data"

_LOGGER = logging.getLogger(__name__)


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
    vol.Optional(CONF_ICON): str,
    vol.Optional(CONF_LINKS): vol.Any([str, LINK_SCHEMA]),
}

HARMONY_HELPER_SCHEMA = {
    vol.Required(CONF_SOURCE): cv.entity_domain(REMOTE_DOMAIN),
    vol.Required(CONF_ACTIVITY_DEVICE_LINKS): {
        str: ACTIVITY_DEVICE_LINK_SCHEMA,
    },
    vol.Required(CONF_COMMANDS): vol.Any([str, COMMAND_SCHEMA]),
}

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: HARMONY_HELPER_SCHEMA})}, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Harmony Helper Binary Sensors."""

    if DOMAIN not in config:
        return True

    if not hass.config_entries.async_entries(DOMAIN):
        # We avoid creating an import flow if its already
        # setup since it will have to import the config_flow
        # module.
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=config,
            )
        )

    _process_config(hass, config[DOMAIN])

    async def _reload_config(call: Event | ServiceCall) -> None:
        try:
            unprocessed_conf = await conf_util.async_hass_config_yaml(hass)
        except HomeAssistantError as err:
            _LOGGER.error(err)
            return

        integration = await async_get_integration(hass, DOMAIN)
        conf = await conf_util.async_process_component_and_handle_errors(
            hass, unprocessed_conf, integration
        )
        if conf is None:
            return

        await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)

        if DOMAIN in conf:
            _process_config(hass, conf)
        else:
            hass.data.pop(DATA_HARMONY_HELPER, None)

        if module := hass.data.get(DATA_MODULE):
            await hass.config_entries.async_reload(module.entry.entry_id)

        hass.bus.async_fire(f"event_{DOMAIN}_reloaded", context=call.context)

    async_register_admin_service(hass, DOMAIN, SERVICE_RELOAD, _reload_config)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup a config entry."""

    module: HarmonyHelperModule | None
    if hass.data.get(DATA_HARMONY_HELPER):
        hass.data[DATA_MODULE] = module = HarmonyHelperModule(PLATFORMS, entry)
        await hass.config_entries.async_forward_entry_setups(entry, module.platforms)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _process_config(hass: HomeAssistant, helper_config: dict[str, ConfigType]) -> None:
    """Process Harmony Helper Config."""

    hass.data.pop(DATA_HARMONY_HELPER, None)

    harmony_helpers = []
    for harmony_helper, conf in helper_config.items():
        conf: ConfigType
        _LOGGER.debug("Setup %s.%s", DOMAIN, harmony_helper)

        source: str = conf.get(CONF_SOURCE)
        commands = {}

        activity_device_links_config: ConfigType = conf[CONF_ACTIVITY_DEVICE_LINKS]

        activity_device_links = {
            k: ActivityDeviceLink(k, v[CONF_ACTIVITY], v[CONF_DEVICE])
            for k, v in activity_device_links_config.items()
        }
        command_config: list[str | ConfigType] = conf[CONF_COMMANDS]
        for command in command_config:
            if isinstance(command, str):
                helper_command = command
                command = Command(helper_command, None, None, None)
                for activity_device_link in activity_device_links.values():
                    command.links[activity_device_link.activity] = Link(
                        command, activity_device_link, None, None, None
                    )

            else:
                helper_command = command[CONF_COMMAND]
                links = command.get(CONF_LINKS, list(activity_device_links.values()))
                command = Command(
                    helper_command,
                    command.get(CONF_NAME),
                    command.get(CONF_DEVICE_COMMAND),
                    command.get(CONF_ICON),
                )
                for link in links:
                    link_dict = {}
                    if isinstance(link, str):
                        link_key = link
                        activity_device_link = activity_device_links.get(link_key)
                    elif isinstance(link, dict):
                        link_dict = link
                        link_key = link.get(CONF_LINK)
                        activity_device_link = activity_device_links.get(link_key)
                    else:
                        activity_device_link = link

                    if activity_device_link is None:
                        _LOGGER.warning(
                            "Activity device link '%s' does not exist", link_key
                        )
                    else:
                        command.links[activity_device_link.activity] = Link(
                            command,
                            activity_device_link,
                            link_dict.get(CONF_NAME),
                            link_dict.get(CONF_DEVICE_COMMAND),
                            link_dict.get(CONF_ICON),
                        )

            if helper_command in commands:
                _LOGGER.warning(
                    "Command '%s' already exists, overwriting", helper_command
                )

            commands[helper_command] = command

        harmony_helpers.append(
            HarmonyHelperData(harmony_helper, source, list(commands.values()))
        )

    if harmony_helpers:
        hass.data[DATA_HARMONY_HELPER] = harmony_helpers
