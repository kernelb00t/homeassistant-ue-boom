"""Binary sensor platform for the UE Boom integration."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UeBoomConfigEntry, device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UeBoomConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the UE Boom binary sensor."""
    async_add_entities([UeBoomSignalSensor(entry)])


class UeBoomSignalSensor(BinarySensorEntity):
    """Binary sensor reporting whether the BLE signal is received reliably.

    The speaker only emits its BLE beacon while in standby; once turned on it
    switches to classic Bluetooth and stops advertising. "Reliable reception"
    is determined by Home Assistant's own Bluetooth availability tracking,
    which learns the speaker's advertising interval and flips this sensor off
    once the beacon has been missing for too long.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "bluetooth_signal"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, entry: UeBoomConfigEntry) -> None:
        """Initialize the sensor."""
        data = entry.runtime_data
        self._address = data.address
        self._attr_unique_id = f"{data.address}_signal"
        self._attr_device_info = device_info(data.address, data.title)
        self._attr_is_on = False
        self._unsubscribe_adv: Callable[[], None] | None = None
        self._unsubscribe_unavailable: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Register Bluetooth callbacks when added to Home Assistant."""
        await super().async_added_to_hass()

        @callback
        def _async_update_ble(
            service_info: BluetoothServiceInfoBleak, change: BluetoothChange
        ) -> None:
            """Mark the signal as reliably received on a new advertisement."""
            self._attr_is_on = True
            self.async_write_ha_state()

        @callback
        def _async_handle_unavailable(
            service_info: BluetoothServiceInfoBleak,
        ) -> None:
            """Mark the signal as lost when the beacon stops arriving."""
            self._attr_is_on = False
            self.async_write_ha_state()

        self._unsubscribe_adv = bluetooth.async_register_callback(
            self.hass,
            _async_update_ble,
            BluetoothCallbackMatcher({ADDRESS: self._address}),
            BluetoothScanningMode.PASSIVE,
        )
        self._unsubscribe_unavailable = bluetooth.async_track_unavailable(
            self.hass, _async_handle_unavailable, self._address, connectable=True
        )
        self.async_on_remove(self._unsubscribe_adv)
        self.async_on_remove(self._unsubscribe_unavailable)

    async def async_will_remove_from_hass(self) -> None:
        """Clean up Bluetooth callbacks."""
        if self._unsubscribe_adv:
            self._unsubscribe_adv()
            self._unsubscribe_adv = None
        if self._unsubscribe_unavailable:
            self._unsubscribe_unavailable()
            self._unsubscribe_unavailable = None
        await super().async_will_remove_from_hass()
