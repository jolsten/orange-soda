# import math

# import geojson

# MEAN_EARTH_RADIUS_KM = 6_371


# def radians(ang: float) -> float:
#     return ang * math.pi / 180


# def degrees(ang: float) -> float:
#     return ang * 180 / math.pi


# def inverse_haversine(lon: float, lat: float, direction: float, d: float):
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


# def ground_site_visibility(
#     lon: float, lat: float, alt: float, sat_alt: float, min_el: float
# ):
#     r_earth = MEAN_EARTH_RADIUS_KM * 1000
#     r_gs = r_earth + alt
#     r_sat = r_earth + sat_alt

#     a_rad = (min_el + 90) * math.pi / 180
#     b_rad = math.asin(r_gs / r_sat * math.sin(a_rad))
#     g_rad = math.pi - (a_rad + b_rad)

#     coords = [inverse_haversine(lat, lon, radians(d), g_rad) for d in range(0, 360, 10)]

#     feature = geojson.Feature(
#         geometry=geojson.LineString(coords),
#         properties={"min_elevation": min_el},
#     )

#     return feature
