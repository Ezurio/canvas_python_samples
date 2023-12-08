# Beacons

## Overview
The Beacons examples are slightly different as they make use of a Python module written in Python.
To utilise this the Beacons.py module needs to be saved onto the device filesystem.
Once this is done the demo scripts can be run to produce the relevant Beacons.

## Beacons.py
The Beacons module is intended as a quick lightweight method of creating Beacons of various formats and types. This library has been specifically tailored towards the Canvas Python implementation.

### Usage
All beacons are created and accessed in a similar way.
- Initial data is added during construction via the \_\_init\_\_ function.
- The current beacon data can be accessed with the get_data method. This gives an object that can be manipulated or turned into a bytes object for passing to the advertiser.
- If the beacon has any fields that can be updated then an update method is provided. Note the data must be got and the advert also updated with the new data.

## Eddystone Beacons
Eddystone beacons are no longer supported by Google but are still very commonly used.
The Eddystone specification allows for 4 major typed of beacon.
- URL. This broadcasts a compressed URL which can be decoded and give a user access to a website.
- UID. This broadcasts a unique ID and ranging data which can be used to locate a becon within BLE's limitations.
- TLM. This broadcasts telemetry data, battery voltage and temperature. This can be encrypted but is not currently supported as no standard crypto libs are currently available on the platform.
- EID. This brodcasts an ephemeral ID. This serves the same purpose as the UID however is encrypted and so can provide better security. This is only minimally supported due to the current lack of crypto library on the platform.

These beacon types can be cycled over a time period allowing all data to be transmitted - see Rotating_Eddystone.py for a simple example of this.

Full details of the [Eddystone Protocol Specification](https://github.com/google/eddystone/blob/master/protocol-specification.md)

### Eddystone_EID_Beacon.py
- This creates an Eddystone EID beacon dataset using the module, prints it out and then uses this data to start an advert.
### Eddystone_TLM_Beacon.py
- This creates an Eddystone TLM beacon dataset using the module, prints it out and then uses this data to start an advert.
### Eddystone_UID_Beacon.py
- This creates an Eddystone UID beacon dataset using the module, prints it out and then uses this data to start an advert.
### Eddystone_URL_Beacon.py
- This creates an Eddystone URL beacon dataset using the module, prints it out and then uses this data to start an advert.
### Rotating_Eddystone.py
- This creates a beacon that rotates between UID, URL and TLM type beacons to simulate a real world use case. Temperature and battery data can be changed by manipulating the 'event_data' object directly using the keys 'temperature' and 'battery'. This can be done from the REPL after the script is run.


## Apple iBeacon
The Apple iBeacon is a simple beacon with a specification allowing a UID and 4 bytes of data to be transmitted. Further facilities can be added using a GATT server and connection by the client device, this however is beyond the scope of this module.

Further details of the [Apple iBeacon](https://en.wikipedia.org/wiki/IBeacon)
### iBeacon.py
- This creates an iBeacon beacon dataset using the module, prints it out and then uses this data to start an advert.


## AltBeacon
The AltBeacon was designed as an open source alternative to Apples iBeacon. The AltBeacon leverages the Manufacturer Data ble tag to transmit a UUID (Beacon ID), ranging data and a byte of open data. The UUID can also contain unique data.

Further details of the [Alt Beacon](https://github.com/AltBeacon/spec)
### AltBeacon.py
- This creates an AltBeacon dataset using the module, prints it and then used this data to start an advert.

## Comonalities
All beacon classes use the \_\_init\_\_ constructor method to take parameters and construct the beacon data, stored in the returned object. This data is then available by calling the method 'get_beacon' on the object returned. If apropriate an 'update' method is available to update the beacons data. After updating the beacon data will need to be got again and the advert updated with this new data. See Rotating_Eddystone.py for an example.

