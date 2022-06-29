#!/usr/bin/python
from gps import *
from influxdb import InfluxDBClient
from time import *
import getopt
import os
import socket
import sys
import threading
import time
import argparse

# Your InfluxDB Settings
influx_host = 'localhost'
influx_port = 8086
influx_user = None
influx_pass = None
influx_db = 'gpsd'

# Number of seconds between updates
update_interval = 10

# --------------------------------------------------------------------------------
# Do not change anything below this line
hostname = socket.gethostname()



# --------------------------------------------------------------------------------
# GPS Thread
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd
    gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
    self.current_value = None
    self.running = True

  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next()

# --------------------------------------------------------------------------------
# GPS Loop
if __name__ == '__main__':
# --------------------------------------------------------------------------------
# Command Line Options
  parser = argparse.ArgumentParser()
  parser.add_argument("--debug","-d", help="print debug", action="store_true")
  parser.add_argument("--influx_port", "-p", help="influx server port", type=int, default=influx_port)
  parser.add_argument("--influx_host", "-h", help="influx server address", type=str, default=influx_host)
  parser.add_argument("--influx_db", "-b", help="influx database name", type=str, default=influx_db)
  
  influx_db = args.influx_db
  influx_port = args.influx_port
  influx_host = args.influx_host
  
  debug = args.debug
  
  # Create the thread
  gpsp = GpsPoller()
  try:
    # Start up the thread
    gpsp.start()

    # Sleep for 5 seconds to allow the gps to pick up the position
    time.sleep(5)

    # Start the loop
    influx_client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, influx_db)
    while gpsp.running:
      gpsd_alt   = gpsd.fix.altitude
      gpsd_climb = gpsd.fix.climb
      gpsd_epc   = gpsd.fix.epc
      gpsd_eps   = gpsd.fix.eps
      gpsd_ept   = gpsd.fix.ept
      gpsd_epv   = gpsd.fix.epv
      gpsd_epx   = gpsd.fix.epx
      gpsd_epy   = gpsd.fix.epy
      gpsd_lat   = gpsd.fix.latitude
      gpsd_lon   = gpsd.fix.longitude
      gpsd_mode  = gpsd.fix.mode
      gpsd_speed = gpsd.fix.speed
      gpsd_track = gpsd.fix.track

      # Make sure we have a lat, lon and alt
      if None not in (gpsd_lat, gpsd_lon, gpsd_alt,):
        if debug == True:
          print( "gpsd-python,host=",hostname,",tpv=alt value=",gpsd_alt)
          print( "gpsd-python,host=",hostname,",tpv=climb value=",gpsd_climb)
          print( "gpsd-python,host=",hostname,",tpv=epc value=",gpsd_epc)
          print( "gpsd-python,host=",hostname,",tpv=eps value=",gpsd_eps)
          print( "gpsd-python,host=",hostname,",tpv=ept value=",gpsd_ept)
          print( "gpsd-python,host=",hostname,",tpv=epv value=",gpsd_epv)
          print( "gpsd-python,host=",hostname,",tpv=epx value=",gpsd_epx)
          print( "gpsd-python,host=",hostname,",tpv=epy value=",gpsd_epy)
          print( "gpsd-python,host=",hostname,",tpv=lat value=",gpsd_lat)
          print( "gpsd-python,host=",hostname,",tpv=lon value=",gpsd_lon)
          print( "gpsd-python,host=",hostname,",tpv=mode value=",gpsd_mode)
          print( "gpsd-python,host=",hostname,",tpv=speed value=",gpsd_speed)
          print( "gpsd-python,host=",hostname,",tpv=track value=",gpsd_track)

      influx_json_body = [
        {
          "measurement": "gpsd-python",
          "tags": {
            "host": hostname
          },
          "fields": {
            "alt": gpsd_alt,
            "climb": gpsd_climb,
            "epc": gpsd_epc,
            "eps": gpsd_eps,
            "ept": gpsd_ept,
            "epv": gpsd_epv,
            "epx": gpsd_epx,
            "epy": gpsd_epy,
            "lat": gpsd_lat,
            "lon": gpsd_lon,
            "mode": gpsd_mode,
            "speed": gpsd_speed,
            "track": gpsd_track
          }
        }
      ]
      
      
      try :
        influx_client.write_points(influx_json_body)
      # sometime we get invalid number
      except Exception as e:
        print(e)
        
      time.sleep(update_interval)

  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print( "\nKilling Thread...")
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print( "Done.\nExiting.")
