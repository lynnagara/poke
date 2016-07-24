#!/usr/bin/python

import sys
import math
import urllib.request
import urllib.parse
import json
import polyline
import os
import datetime
from xml.etree import ElementTree as et

BASE_URL = 'https://maps.googleapis.com/maps/api/directions/json?mode=walking&'
args = sys.argv[1:]
CURRENT_TIME = datetime.datetime.now()


def make_request(fr, to):
  endpoint = BASE_URL + urllib.parse.urlencode({'origin': fr, 'destination': to})
  data = json.loads(urllib.request.urlopen(endpoint).read().decode('utf-8'))

  routes = data['routes']

  if (len(routes) > 0):
    make_file(routes[0])
  else:
    print('No routes found')



def get_xml_tree(waypoints):
  root = et.Element('gpx')

  seconds_from_now = 0

  for point in waypoints:
    # walk pretty fast smoothing time between each waypoint
    seconds_from_now += math.ceil(point[2]/10)
    waypoint_time = CURRENT_TIME + datetime.timedelta(0, seconds_from_now)
    formatted_time = datetime.datetime.strftime(waypoint_time,'%Y-%m-%dT%H:%M:%S')

    elem = et.SubElement(root, 'wpt')
    time_elem = et.SubElement(elem, 'time')
    time_elem.text = str(formatted_time)
    elem.attrib['lat'] = str(point[0])
    elem.attrib['lon'] = str(point[1])

  tree = et.ElementTree(root)
  return tree

def make_file(route):
  if (os.path.exists('output') == False):
    os.mkdir('output')

  steps = route['legs'][0]['steps']
  points = []

  for step in steps:
    points_in_step = polyline.decode(step['polyline']['points'])
    for point in points_in_step:
      dist_to_point = step['distance']['value'] / len(points_in_step)
      points.append(point + tuple([dist_to_point]))

  tree = get_xml_tree(points)
  tree.write('output/out.gpx', xml_declaration=True, encoding='utf-8')
  print('Created out.gpx')
  print('From: ' + args[0] + ', To: ' + args[1])


if (len(args) != 2):
  print('Incorrect number of arguments')
else:
  make_request(*args)


