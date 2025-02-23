import math
from dataclasses import dataclass
from typing import Optional

import geojson
import haversine
import numpy as np

MEAN_EARTH_RADIUS_KM = 6_371


def radians(ang: float) -> float:
    return ang * math.pi / 180


def degrees(ang: float) -> float:
    return ang * 180 / math.pi


# def inverse_haversine(lat: float, lon: float, direction: float, d: float):
#     """
#     Compute the inverse haversine on unit sphere.  lat/lon are in degrees,
#     direction in radians; all inputs are either scalars (with ops==math) or
#     arrays (with ops==numpy).
#     """
#     lat = radians(lat)
#     lon = radians(lon)
#     cos_d, sin_d = math.cos(d), math.sin(d)
#     cos_lat, sin_lat = math.cos(lat), math.sin(lat)
#     sin_d_cos_lat = sin_d * cos_lat
#     return_lat = math.asin(cos_d * sin_lat + sin_d_cos_lat * math.cos(direction))
#     return_lon = lon + math.atan2(
#         math.sin(direction) * sin_d_cos_lat, cos_d - sin_lat * math.sin(return_lat)
#     )
#     return degrees(return_lon), degrees(return_lat)


def ground_site_visibility_circle(
    lat: float,
    lon: float,
    alt_m: float,
    sat_alt_m: float,
    min_el_deg: float,
    points: int = 50,
):
    r_earth = MEAN_EARTH_RADIUS_KM * 1000
    r_gs = r_earth + alt_m
    r_sat = r_earth + sat_alt_m

    a_rad = (min_el_deg + 90) * math.pi / 180
    b_rad = math.asin(r_gs / r_sat * math.sin(a_rad))
    g_rad = math.pi - (a_rad + b_rad)
    dist = r_earth * g_rad

    coords = [
        haversine.inverse_haversine(
            (lat, lon), dist, radians(x), unit=haversine.Unit.METERS
        )
        for x in np.linspace(0, 360, points)
    ]
    # Result is in (lat, lon) order. Convert to (lon, lat) for GeoJSON.
    coords = [(lon, lat) for lat, lon in coords]

    feature = geojson.Feature(
        geometry=geojson.LineString(coords),
        properties={"min_elevation": min_el_deg},
    )

    return feature


@dataclass
class GroundSite:
    lat: float
    lon: float
    alt: float = 0.0
    name: Optional[str] = None

    def to_geojson(self) -> geojson.Feature:
        return geojson.Feature(
            geometry=geojson.Point(coordinates=(self.lon, self.lat, self.alt)),
            properties={"name": self.name},
        )

    def satellite_visibility_ring(
        self,
        sat_alt_km: float,
        min_el_deg: float = 0,
        points: int = 50,
    ) -> geojson.Feature:
        feature = ground_site_visibility_circle(
            lat=self.lat,
            lon=self.lon,
            alt_m=self.alt,
            sat_alt_m=sat_alt_km * 1000,
            min_el_deg=min_el_deg,
            points=points,
        )
        return feature
