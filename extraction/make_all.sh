#!/bin/bash
#
#
#

### Make JSON ###
python3 get_json.py

### Make extraction ###
python3 get_data.py -t all -v