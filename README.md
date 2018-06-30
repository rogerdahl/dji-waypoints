## Automatically adjust the altitude of waypoints in DJI GO Mod to match the terrain

This script connects to the waypoints database in DJI Go Mod and, for each waypoint, looks up the elevation for the GPS position using the Google Elevations API, adds a configurable altitude value to the elevation and writes the new altitudes back to the waypoint.

The goal is to keep the drone at a fairly constant altitude in hilly terrain.


### Notes

* This works for me but might crash your drone

* Requires that you obtain an API key from Google in order to access the Google Elevation API. It is very unlikely that you will exceed their free usage tier, but you will still need to register a payment method, such as a credit card, or bank account with Google.

* Works only with the hacked version of DJI Go, called DJI Go Mod

* Works only on Linux, due to dependency on `go-mtpfs`


### Setup

* Install `go-mtpfs`
  * `$ apt install go-mtpfs`

* Clone this repo and enter it:
  * `$ git clone <copy and paste the "Clone with HTTPS " URL from the top of this page>`
  * `$ cd dji-waypoint`

* Prepare and activate a Python 3 virtual environment
  * `$ python3 -m venv venv`
  * `$ . ./venv/bin/activate`
  * `$ pip install requests`

* Obtain a API key from Google for the Elevation API
  * https://developers.google.com/maps/documentation/elevation/get-api-key

* Prepare and edit the settings
  * `$ cp settings_sample.py settings.py`
  * Edit `settings.py`
    * Insert your API key
    * Check and adjust `ALTITUDE_M`
      * I recommend using high altitudes while testing the adjusted waypoints


### Usage

* On an Android device that has DJI Go Mod installed, set the USB configuration to MTP (Media Transfer Protocol)

* Connect the device to the Linux box via USB

* Run `./adjust_waypoint_altitude.py`


### Workflow

* Create mission on the PC while leaving waypoint altitudes at the default value
  * https://mission.3d-log.com/

* Important: Take care to place the waypoints at the highest points in the terrain

* Download the mission to the Android device (or create directly on Android)
  * https://play.google.com/store/apps/details?id=ru.zalomskij.mission&rdid=ru.zalomskij.mission

* Run `./adjust_waypoint_altitude.py`
* Upload the mission to the drone with DJI Go Mod and fly
  * https://sparkpilots.zone/threads/dji-go-4-mod-2-0-dji-go-4-mod-lite-additional-features-android-app-ver-4-1-15.3841/


### Resources

#### DJI hacks
https://github.com/Bin4ry/deejayeye-modder

#### go-mtpfs
https://github.com/hanwen/go-mtpfs
