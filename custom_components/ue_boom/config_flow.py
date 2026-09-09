"""Config flow for the UE Boom integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers import device_registry as dr, selector

from .const import CONF_TRUSTED_MAC, DOMAIN, MANUFACTURER_ID, SERVICE_UUID
from .util import normalize_mac

_LOGGER = logging.getLogger(__name__)

# Sentinel value for the "enter address manually" choice.
MANUAL_ADDRESS = "manual"


def _is_ue_boom(service_info: BluetoothServiceInfoBleak) -> bool:
    """Return True if the advertisement looks like a UE Boom speaker."""
    name = (service_info.name or "").upper()
    if any(token in name for token in ("BOOM", "MEGABOOM")):
        return True
    service_uuids = {str(uuid).lower() for uuid in service_info.service_uuids}
    if SERVICE_UUID in service_uuids:
        return True
    return MANUFACTURER_ID in (service_info.manufacturer_data or {})


class UeBoomConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UE Boom."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered: dict[str, BluetoothServiceInfoBleak] = {}
        self._address: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a Bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._address = discovery_info.address
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }
        return await self.async_step_trusted_mac()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick a discovered speaker."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            if address == MANUAL_ADDRESS:
                return await self.async_step_manual()
            self._address = address
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return await self.async_step_trusted_mac()

        self._discovered = {}
        current_addresses = self._async_current_ids(include_ignore=False)
        for info in async_discovered_service_info(self.hass, connectable=True):
            if info.address in current_addresses or not _is_ue_boom(info):
                continue
            self._discovered[info.address] = info

        if not self._discovered:
            return await self.async_step_manual()

        options = {
            info.address: f"{info.name or 'UE Boom'} ({info.address})"
            for info in self._discovered.values()
        }
        options[MANUAL_ADDRESS] = "Enter address manually…"
        data_schema = vol.Schema({vol.Required(CONF_ADDRESS): vol.In(options)})
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual entry of the speaker address."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._address = dr.format_mac(user_input[CONF_ADDRESS])
            except ValueError:
                errors[CONF_ADDRESS] = "invalid_mac"
            else:
                await self.async_set_unique_id(
                    self._address, raise_on_progress=False
                )
                self._abort_if_unique_id_configured()
                return await self.async_step_trusted_mac()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): selector.TextSelector(
                    selector.TextSelectorConfig()
                )
            }
        )
        return self.async_show_form(
            step_id="manual", data_schema=data_schema, errors=errors
        )

    async def async_step_trusted_mac(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect the MAC address of a trusted device."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                trusted_mac = normalize_mac(user_input[CONF_TRUSTED_MAC])
            except ValueError:
                errors[CONF_TRUSTED_MAC] = "invalid_mac"
            else:
                return self._create_entry(trusted_mac)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_TRUSTED_MAC): selector.TextSelector(
                    selector.TextSelectorConfig()
                )
            }
        )
        return self.async_show_form(
            step_id="trusted_mac",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"address": self._address or ""},
        )

    def _create_entry(self, trusted_mac: str) -> ConfigFlowResult:
        """Create the config entry from the collected values."""
        assert self._address is not None
        return self.async_create_entry(
            title=self._title(self._address),
            data={
                CONF_ADDRESS: self._address,
                CONF_TRUSTED_MAC: trusted_mac,
            },
        )

    def _title(self, address: str) -> str:
        """Build a friendly title for the config entry."""
        if self._discovery_info is not None and self._discovery_info.name:
            return self._discovery_info.name
        info = self._discovered.get(address)
        if info is not None and info.name:
            return info.name
        return f"UE Boom {address}"
