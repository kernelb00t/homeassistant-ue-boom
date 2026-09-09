"""Button platform for the UE Boom integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UeBoomConfigEntry, device_info
from .ble import async_send_power_command
from .const import CMD_POWER_ON


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UeBoomConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the UE Boom button."""
    async_add_entities([UeBoomPowerButton(entry, CMD_POWER_ON, "power_on")])


class UeBoomPowerButton(ButtonEntity):
    """Button that sends a magic power packet to the speaker."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: UeBoomConfigEntry, command: int, translation_key: str
    ) -> None:
        """Initialize the button."""
        data = entry.runtime_data
        self._address = data.address
        self._trusted_mac = data.trusted_mac
        self._command = command
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{data.address}_{command:02x}"
        self._attr_device_info = device_info(data.address, data.title)

    async def async_press(self) -> None:
        """Send the magic power packet on press."""
        await async_send_power_command(
            self.hass, self._address, self._trusted_mac, self._command
        )
