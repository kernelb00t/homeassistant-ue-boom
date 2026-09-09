"""Sensor platform for the UE Boom integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import UeBoomConfigEntry, device_info
from .ble import async_read_battery
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# The battery is only readable while the speaker is in BLE standby, so keep a
# conservative poll interval rather than hammering the connection.
BATTERY_UPDATE_INTERVAL = timedelta(minutes=15)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UeBoomConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the UE Boom battery sensor."""
    data = entry.runtime_data
    coordinator = UeBoomBatteryCoordinator(hass, entry, data.address)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([UeBoomBatterySensor(coordinator, entry)])


class UeBoomBatteryCoordinator(DataUpdateCoordinator[int | None]):
    """Coordinator that polls the battery level over BLE."""

    def __init__(
        self, hass: HomeAssistant, entry: UeBoomConfigEntry, address: str
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_battery",
            update_interval=BATTERY_UPDATE_INTERVAL,
            config_entry=entry,
        )
        self._address = address

    async def _async_update_data(self) -> int | None:
        """Read the battery level, returning None when not available."""
        return await async_read_battery(self.hass, self._address)


class UeBoomBatterySensor(
    CoordinatorEntity[UeBoomBatteryCoordinator], SensorEntity
):
    """Sensor reporting the speaker battery level."""

    _attr_has_entity_name = True
    _attr_translation_key = "battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self, coordinator: UeBoomBatteryCoordinator, entry: UeBoomConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        data = entry.runtime_data
        self._attr_unique_id = f"{data.address}_battery"
        self._attr_device_info = device_info(data.address, data.title)

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        return self.coordinator.data
