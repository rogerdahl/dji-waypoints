# The app needs an API key in order to access the Google Elevation service
GOOGLE_MAPS_API_KEY = '<insert your Google Elevations API key here>'

# Meters above ground to which to move each waypoint
ALTITUDE_M = 100

# Warn if the uncertainty of the elevation returned by the Google Elevation API
# is higher than this number of meters
WARN_RESOLUTION_M = 10

# The relative path to the DJI Go Mod Sqlite database
# You may need to modify the version numbers in the filename to match your
# version of DJI Go Mod
DJI_GO_SQLITE_DB_PATH = 'Internal storage/DJI/dji_mod_4_1_15.db'

# It should not be necessary to change the settings below
MOUNT_CMD_LIST = ['go-mtpfs', '-allow-other']
UMOUNT_CMD_LIST = ['fusermount', '-u']
GOOGLE_MAPS_ELEVATION_ENDPOINT_URL = 'https://maps.googleapis.com/maps/api/elevation/json'
