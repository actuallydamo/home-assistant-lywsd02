from __future__ import annotations

import time
import struct
import logging

from datetime import datetime, timezone, timedelta

from bleak import BleakClient

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import bluetooth

DOMAIN = "lywsd02"

_LOGGER = logging.getLogger(__name__)


_UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'
_UUID_TEMO = 'EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6'

def get_localized_timestamp():
    now = time.time()
    utc = datetime.fromtimestamp(now, timezone.utc)
    local = datetime.fromtimestamp(now)
    diff = (local.replace(tzinfo=timezone.utc) - utc).total_seconds()
    return int((utc + timedelta(seconds=diff)).timestamp())

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """
    Based off https://github.com/h4/lywsd02
    """
    
    @callback
    async def set_time(call: ServiceCall) -> None:
        mac = call.data['mac'].upper()
        if not mac:
            _LOGGER.error(f"The 'mac' parameter is missing from service call: {call.data}.")
            return

        tz_offset = call.data.get('tz_offset')
        tz_offset = int(tz_offset) if tz_offset is not None else None

        timestamp = call.data.get('timestamp')
        timestamp = int(timestamp) if timestamp is not None else None

        ble_device = bluetooth.async_ble_device_from_address(
            hass,
            mac,
            connectable=True
        )

        if not ble_device:
            _LOGGER.error(f"Could not find '{mac}'.")
            return

        _LOGGER.info(f"Found '{ble_device}' - Attempting to update time.")

        temo_set = False
        ckmo_set = False
        temo = call.data.get('temp_mode', '') or "x"
        temo = temo.upper()
        _LOGGER.debug(f"temo var: {temo}")

        if temo in 'CF':
            data_temp_mode = struct.pack('B', (0x01 if temo == 'F' else 0xFF))
            _LOGGER.debug(f"Will set temp_mode")
            temo_set = True

        ckmo = call.data.get('clock_mode', 0)
        _LOGGER.debug(f"ckmo var: {ckmo}")
        if ckmo in [12, 24]:
            data_clock_mode = struct.pack('IHB', 0, 0, 0xaa if ckmo == 12 else 0x00)
            _LOGGER.debug(f"Will set clock_mode")
            ckmo_set = True

        tout = int(call.data.get('timeout', 60))
        
        async with BleakClient(ble_device, timeout=tout) as client:
            if not timestamp:
                if tz_offset is not None:
                    timestamp = int(time.time())
                else:
                    tz_offset = 0
                    timestamp = get_localized_timestamp()
            elif tz_offset is None:
                tz_offset = 0
            data = struct.pack('Ib', timestamp, tz_offset)
            await client.write_gatt_char(_UUID_TIME, data)
            if temo_set:
                await client.write_gatt_char(_UUID_TEMO, data_temp_mode)
            if ckmo_set:
                await client.write_gatt_char(_UUID_TIME, data_clock_mode)

        _LOGGER.info(f"Done - refreshed time on '{mac}' to '{timestamp}' with offset of '{tz_offset}' hours.")

    hass.services.async_register(DOMAIN, 'set_time', set_time)

    return True
