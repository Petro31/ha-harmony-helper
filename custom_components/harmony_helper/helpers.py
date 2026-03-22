"""Helpers for harmony helper."""

from homeassistant.helpers import entity_registry as er

from .const import DEFAULT_ICON, DEFAULT_ICONS


def get_harmony_remote_device_id(
    entity_registry: er.EntityRegistry, entity_id: str
) -> str:
    """Get the harmony remote device_id."""
    if registry := entity_registry.async_get(entity_id):
        return registry.device_id

    return None


class CommandBase:
    """Base object for Harmony Commands."""

    def __init__(self, name: str, device_command: str, icon: str) -> None:
        """Initialize."""
        self._name = name
        self._device_command = device_command
        self._icon = icon


class Command(CommandBase):
    """Harmony Command."""

    def __init__(self, command: str, name: str, device_command: str, icon: str) -> None:
        """Initialize."""
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
    """Activity Link."""

    def __init__(
        self,
        command: Command,
        link: ActivityDeviceLink,
        name: str,
        device_command: str,
        icon: str,
    ) -> None:
        """Initialize."""
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
            ret = DEFAULT_ICONS.get(self.device_command)
            if ret is None:
                ret = self._command.icon
        return ret

    @property
    def device(self) -> str:
        """The link activity."""
        return self._link.device


class ActivityDeviceLink:
    """Activity and Device Link."""

    def __init__(self, name, activity, device) -> None:
        """Initialize."""
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
