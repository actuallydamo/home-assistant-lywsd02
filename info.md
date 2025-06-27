# LYWSD02 Sync

Once installed, you need to add the following to Home Assistant's `configuration.yaml` and restart it:
```yaml
lywsd02:
```

## Setting Time

Now you have a `lywsd.set_time` service that can be used to set the time on a LYWSD02 given its BLE MAC address.

Only the MAC address parameter is required, and it will set the time to what is on your Home Assistant.
Here's a minimal invocation:
```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
```

Now you can setup an automation to invoke this service as often as you'd like to sync LYWSD02's time.

If you want lower-level control - you can tweak the exact time set via additional parameters.
See [./services.yaml](./custom_components/lywsd02/services.yaml) for details.

## Setting Unit

You can also set the temperature unit (F/C), TZ offset, as well as clock mode (12/24) via optional parameters:
```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
  clock_mode: 24
  tz_offset: 0
  temp_mode: 'C'
```

`tz_offset` only accepts whole numbers.

If you are in a whole number timezone (e.g. UTC+2, UTC-5):
`tz_offset` defaults to your timezone offset.
`timestamp` defaults to UTC.

If you are in a partial hour timezone (e.g. UTC+8:45, UTC-3:30):
`tz_offset` defaults to rounding down your timezone offset.
`timestamp` defaults to UTC + your partial hour offset.

## Timeout

If you get an error establishing a connection - it could be because it takes longer than expected to get the Bluetooth proxy working. Consider increasing `timeout` from default 10s to a larger value:
```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
  timeout: 60
```
