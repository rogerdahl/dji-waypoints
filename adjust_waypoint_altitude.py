#!/usr/bin/env python

import contextlib
import json
import logging
import os
import sqlite3
import subprocess
import tempfile
import time

import requests

import settings


def main():
  logging.basicConfig(format='%(levelname)-7s %(message)s', level=logging.INFO)
  with tmp_mount_dir() as mount_dir_path:
    with mtp_mount(mount_dir_path):
      with sqlite_connection(mount_dir_path) as conn:
        adjust_waypoint_altitudes(conn)


def adjust_waypoint_altitudes(conn):
  cursor = conn.cursor()

  row_cursor = cursor.execute(
    'select * from dji_pilot_dji_groundstation_controller_DataMgr_DJIWPCollectionItem'
  )

  for mission_dict in list(row_cursor):
    logging.info('\n' + '-' * 80)
    logging.info('Mission: {}\n'.format(mission_dict['location']))

    points_dict = json.loads(mission_dict['pointsJsonStr'])

    abs_home_elevation_m = None

    for point_idx, point_dict in enumerate(points_dict['points']):
      lat_float, lng_float = point_dict['lat'], point_dict['lng']

      logging.info(
        'waypoint={:03} lat={:03.15} lng={:03.15}:'.format(
          point_idx + 1, lat_float, lng_float
        )
      )

      try:
        abs_elevation_m, resolution_m = get_elevation_with_resolution(
          lat_float, lng_float
        )
      except WaypointAdjusterExeption as e:
        logging.error(str(e))
        continue

      abs_home_elevation_m = abs_home_elevation_m or abs_elevation_m
      new_rel_altitude_m = (
        abs_elevation_m - abs_home_elevation_m + settings.ALTITUDE_M
      )

      logging.info(
        'Adjusting altitude. new_altitude_m={:04}'.format(new_rel_altitude_m)
      )
      point_dict['height'] = new_rel_altitude_m

    cursor.execute(
      'update dji_pilot_dji_groundstation_controller_DataMgr_DJIWPCollectionItem '
      'set pointsJsonStr=? where id=?',
      [json.dumps(points_dict), mission_dict['id']],
    )

    conn.commit()


@contextlib.contextmanager
def sqlite_connection(mount_dir_path):
  db_path = os.path.join(mount_dir_path, settings.DJI_GO_SQLITE_DB_PATH)
  try:
    conn = sqlite3.connect(db_path)
  except sqlite3.OperationalError as e:
    raise WaypointAdjusterExeption(
      'error="{}" path="{}"'.format(str(e), db_path)
    )
  conn.row_factory = dict_factory
  yield conn
  conn.commit()
  conn.close()


def get_elevation_with_resolution(lat_float, lng_float):
  response = requests.get(
    settings.GOOGLE_MAPS_ELEVATION_ENDPOINT_URL,
    params={
      'locations': '{},{}'.format(lat_float, lng_float),
      'key': settings.GOOGLE_MAPS_API_KEY,
    },
  )
  elevation_dict = response.json()
  if elevation_dict['status'] != 'OK':
    raise WaypointAdjusterExeption(
      'Unable to query elevation. error="{}"'.format(
        elevation_dict['error_message']
      )
    )
  elevation_m = round(elevation_dict['results'][0]['elevation'])
  resolution_m = elevation_dict['results'][0]['resolution']
  if resolution_m > settings.WARN_RESOLUTION:
    logging.warning(
      'Elevation has low resolution. resolution_m={:.02}'.format(resolution_m)
    )
  return elevation_m, resolution_m


@contextlib.contextmanager
def tmp_mount_dir():
  mount_dir_path = tempfile.mkdtemp()
  yield mount_dir_path
  os.rmdir(mount_dir_path)


@contextlib.contextmanager
def mtp_mount(mount_dir_path):
  fuse_proc = mount_mtp(mount_dir_path)
  yield
  umount_mtp(fuse_proc, mount_dir_path)


def mount_mtp(mount_dir_path):
  try:
    fuse_proc = subprocess.Popen(settings.MOUNT_CMD_LIST + [mount_dir_path])
  except subprocess.CalledProcessError as e:
    raise WaypointAdjusterExeption(str(e))
  for i in range(10):
    if os.path.ismount(mount_dir_path):
      return fuse_proc
    logging.info('Waiting for MTP mount...')
    time.sleep(1)
  raise WaypointAdjusterExeption('MTP mount timed out')


def umount_mtp(fuse_proc, mount_dir_path):
  for i in range(10):
    try:
      subprocess.check_call(settings.UMOUNT_CMD_LIST + [mount_dir_path])
    except subprocess.CalledProcessError as e:
      logging.error(WaypointAdjusterExeption(str(e)))
      time.sleep(1)
      continue
    if not os.path.ismount(mount_dir_path):
      return
    logging.info('Waiting for MTP unmount...')
    time.sleep(1)
  fuse_proc.wait()


def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d


class WaypointAdjusterExeption(Exception):
  pass


if __name__ == '__main__':
  main()
