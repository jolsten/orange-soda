from typing import Union

import antimeridian
import geojson

GeoJSON = Union[
    geojson.Point,
    geojson.MultiPoint,
    geojson.LineString,
    geojson.MultiLineString,
    geojson.Polygon,
    geojson.MultiPolygon,
    geojson.GeometryCollection,
    geojson.Feature,
    geojson.FeatureCollection,
]

FIXABLE = ["LineString", "MultiLineString", "Polygon", "MultiPolygon"]
UNFIXABLE = ["Point", "MultiPoint"]
GEOMETRIES = UNFIXABLE + FIXABLE


def fix_geojson(obj: GeoJSON) -> GeoJSON:
    if obj["type"] == "GeometryCollection":
        # For a GeometryCollection, split the geometries apart, then fix them
        obj["geometries"] = [fix_geojson(geometry) for geometry in obj["geometries"]]
        return obj
    elif obj["type"] == "FeatureCollection":
        for idx in range(len(obj["features"])):
            fixed = fix_geojson(obj["features"][idx])
            obj["features"][idx]["geometry"]["coordinates"] = fixed["geometry"][
                "coordinates"
            ]
            return obj
    elif obj["type"] == "Feature":
        if obj["geometry"]["type"] in UNFIXABLE:
            # Points and MultiPoints do not need to be fixed
            return obj
        elif obj["geometry"]["type"] in FIXABLE:
            # If the Feature's geometry can be fixed, fix it
            # Update the original dictionary with the new geometry's coordinates
            fixed = antimeridian.fix_geojson(obj)
            obj["geometry"]["coordinates"] = fixed["geometry"]["coordinates"]
            return obj
        elif obj["geometry"]["type"] == "GeometryCollection":
            for idx, geometry in enumerate(obj["geometries"]):
                fixed = fix_geojson(geometry)
                obj["geometries"][idx]["geometry"]["coordinates"] = fixed["coordinates"]
            return obj
    elif obj["type"] in GEOMETRIES:
        # 1. Encapsulate the geometry in a Feature
        # 2. Fix it
        # 4. Return the original Geometry with the new coordinates
        feature = geojson.Feature(geometry=obj)
        feature = fix_geojson(feature)
        obj["coordinates"] = feature["geometry"]["coordinates"]
        return feature["geometry"]
    else:
        raise ValueError
