import math
from typing import Optional

import geojson
import haversine
import numpy as np

from orange_soda.utils import MEAN_EARTH_RADIUS, radians


def point(lat, lon, name: Optional[str] = None) -> geojson.Feature:
    return geojson.Feature(
        geometry=geojson.Point((lon, lat)), properties={"name": name}
    )


def visibility_circle(
    lat: float,
    lon: float,
    alt_m: float,
    min_el: float,
    sat_alt_m: float,
    points: int = 60,
) -> geojson.Feature:
    r_earth = MEAN_EARTH_RADIUS["km"] * 1000
    r_gs = r_earth + alt_m
    r_sat = r_earth + sat_alt_m

    a_rad = (min_el + 90) * math.pi / 180
    b_rad = math.asin(r_gs / r_sat * math.sin(a_rad))
    g_rad = math.pi - (a_rad + b_rad)
    dist = r_earth * g_rad

    coords = [
        haversine.inverse_haversine(
            (lat, lon), dist, radians(x), unit=haversine.Unit.METERS
        )
        for x in np.linspace(0, 360, points)
    ]
    coords.append(coords[0])  # Close the shape

    # Flip lat, lon to lon, lat
    coords = [(lon, lat) for lat, lon in coords]

    feature = geojson.FeatureCollection(
        features=[
            geojson.Feature(geometry=geojson.Point(coordinates=(lon, lat))),
            geojson.Feature(geometry=geojson.LineString(coordinates=coords)),
        ],
    )

    return feature
