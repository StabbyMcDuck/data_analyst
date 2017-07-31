import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import csv
import codecs
import cerberus
import schema

osm_file = open("austin_texas.osm", "r")

# Find problematic character tags

lower = re.compile(r'^([a-z]|_*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problem_chars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        if lower.match(element.attrib['k']):
            keys["lower"] += 1
        elif lower_colon.match(element.attrib['k']):
            keys["lower_colon"] += 1
        elif problem_chars.match(element.attrib['k']):
            keys["problem_chars"] += 1
        else:
            keys["other"] += 1

def process_map(filename):
    keys = {"lower": 0, "lower_colon":0, "problem_chars":0, "other":0}
    for _, element in ET.interparse(filename):
        keys = key_type(element, keys)
    return keys

# Search for unexpected street types

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected_street_names = ["Street", "Avenue", "Boulevard", "Place", "Drive", "Court", "Way", "Road", "Parkway", "Square", "Lane", "Trail", "Commons", "Terrace", "Run", "Circle", "Path", "Loop", "Highway", "Broadway"]

def audit_street_type(street_types, street_name):
    found_street_name = street_type_re.search(street_name)

    if found_street_name:
        street_type = found_street_name.group()
        if street_type not in expected_street_names:
            street_types[street_type].add(street_name)

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())

    for k in keys:
        v = d[k]
        print "%s: %s" % (k,v)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(filename):
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

# Search for weird zip codes

zip_codes = []



