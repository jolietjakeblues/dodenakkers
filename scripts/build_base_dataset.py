#!/usr/bin/env python3
"""
Build the base cemetery dataset from the normalized CSV.

Main geometry: cemetery terrain.
Entrance: preserved as a Point in properties.
Measurements: calculated in EPSG:28992.

This script intentionally does not silently resolve status conflicts.
"""
from pathlib import Path
import json
import pandas as pd
from shapely import wkt
from shapely.geometry import mapping
from shapely.ops import transform
from pyproj import Transformer

# The full implementation used for the current generated snapshot is documented
# in docs/data/kml-audit-resultaten.md and docs/data/003-csv-bron-en-koppeling.md.
# This repository script is a starting point for moving the build logic into GitHub.
#
# Next implementation step:
# - copy the deterministic matching rules from the audit notebook/build step;
# - add assertions for 463 terrains, 461 entrances and known exceptions;
# - write GeoJSON/CSV into data/generated/.
