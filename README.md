# UE Boom

A [Home Assistant](https://www.home-assistant.io) custom component to turn a [Ultimate Ears](https://www.ultimateears.com) **UE Boom / Megaboom** speaker on and off remotely over Bluetooth Low Energy (BLE).

[![Open your Home Assistant instance and open this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kernelb00t&repository=homeassistant-ue-boom&category=integration)

It exposes:

- Two **buttons**: `Power on` / `Power off` — send the magic BLE packet that wakes the speaker from standby or puts it back to sleep.
- One **binary sensor**: `Bluetooth signal` — `on` while the speaker's BLE beacon is received reliably, `off` once it stops.
- One **sensor**: `Battery` — reads the battery level over BLE (only while the speaker is in standby).

> **Important — how state works.** The speaker only emits its BLE beacon while it is **off (standby)**. Once turned on it switches to classic Bluetooth and disappears from the BLE scan. There is no way to *query* the on/off state over BLE, so this integration is intentionally **honest**: the binary sensor reports raw BLE reachability (on = beacon seen reliably, off = beacon lost), and it does not claim to know whether the speaker is on, off, or out of range.

## Requirements

- Home Assistant `2024.4` or newer, with the [Bluetooth integration](https://www.home-assistant.io/integrations/bluetooth/) and a working BLE adapter (local adapter or an [ESPHome Bluetooth proxy](https://esphome.io/components/bluetooth_proxy.html)).
- The speaker's **"Remote power on"** option enabled in the official UE Boom app.
- The **MAC address of a device the speaker trusts** (see below).

## Installation

### HACS (recommended)

Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) in HACS (category *Integration*), then install **UE Boom**.

### Manual

Copy the `custom_components/ue_boom` directory into your Home Assistant `config/custom_components/` folder and restart Home Assistant.

## Configuration

1. In the UE Boom app, enable **Settings → Remote power on** for your speaker.
2. In Home Assistant, go to **Settings → Devices & Services → Add Integration → UE Boom**.
3. Select the discovered speaker, or enter its Bluetooth address manually.
4. Enter the **trusted device MAC**. This is the Bluetooth address of a device authorized to turn the speaker on and off — usually the phone you paired in the app's "Remote power on" setting. On iOS, find it in `Settings → General → About → Bluetooth`.

### About the "trusted MAC"

The magic packet embeds the MAC address of a device the speaker trusts. This is typically your phone or computer's **classic Bluetooth** MAC address, which Home Assistant cannot auto-discover (its BLE scan only sees BLE advertisers, and modern phones randomize their BLE MAC anyway).

- **iOS**: `Settings → General → About → Bluetooth`.
- **Android**: varies by device — often `Settings → About phone → Status`, or a Bluetooth info screen.

The speaker must be in standby (off) and within BLE range for the wake packet to work.

## How it works

The magic packet is a 7-byte GATT write to characteristic `c6d6dc0d-07f5-47ef-9b59-630622b01fd3`:

```
<trusted_mac (6 bytes)> + <command (1 byte)>
```

where `command` is `0x01` (power on) or `0x02` (power off). The speaker only honors a GATT **Write Request** (with response).

## Acknowledgements

Based on prior reverse-engineering work by the community:

- [countableset/ue-boom-re](https://github.com/countableSet/ue-boom-re) and its [write-up](https://blog.countableset.com/2022/02/22/ue-boom-reverse-engineering/)
- [marcust's gist](https://gist.github.com/marcust/af93ff47899583f5a52f)
- [eni23/ueboom](https://github.com/eni23/ueboom)
- [cstan11/ue-boom-macos](https://github.com/cstan11/ue-boom-macos)
- [whayn/ueboom-ctl](https://github.com/whayn/ueboom-ctl)
- [alessandroaime/homebridge-ueboom](https://github.com/alessandroaime/homebridge-ueboom)

## Credits

This integration was coded using [Zed](https://zed.dev) as the editor and [DeepSeek V4 Pro](https://www.deepseek.com) as the AI coding assistant.