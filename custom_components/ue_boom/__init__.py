"""The UE Boom integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothReachabilityIntent,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_TRUSTED_MAC, DOMAIN

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]


@dataclass
class UeBoomData:
    """Runtime data for a single UE Boom device."""

    address: str
    trusted_mac: str
    title: str


type UeBoomConfigEntry = ConfigEntry[UeBoomData]


def device_info(address: str, name: str) -> DeviceInfo:
    """Return the shared device info for a UE Boom speaker."""
    return DeviceInfo(
        identifiers={(DOMAIN, address)},
        name=name,
        connections={(dr.CONNECTION_BLUETOOTH, address)},
        manufacturer="Ultimate Ears",
    )


async def async_setup_entry(hass: HomeAssistant, entry: UeBoomConfigEntry) -> bool:
    """Set up UE Boom from a config entry."""
    address: str = entry.data[CONF_ADDRESS]

    ble_device = bluetooth.async_ble_device_from_address(
        hass, address.upper(), connectable=True
    )
    if not ble_device:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="device_not_found",
            translation_placeholders={
                "address": address,
                "reason": bluetooth.async_address_reachability_diagnostics(
                    hass,
                    address.upper(),
                    BluetoothReachabilityIntent.CONNECTION,
                ),
            },
        )

    entry.runtime_data = UeBoomData(
        address=address,
        trusted_mac=entry.data[CONF_TRUSTED_MAC],
        title=entry.title,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: UeBoomConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
