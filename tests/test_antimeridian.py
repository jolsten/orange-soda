import itertools

import geojson
import pytest

from orange_soda.antimeridian import fix_geojson

VALID_GEOMETRIES = [
    geojson.Point(coordinates=[30, -90], validate=True),
    geojson.MultiPoint(coordinates=[(30, -90), (45, -60)], validate=True),
    geojson.LineString(coordinates=[(30, -90), (45, -60)], validate=True),
    geojson.MultiLineString(
        coordinates=[[(30, -90), (45, -60)], [(-30, 90), (-45, 60)]], validate=True
    ),
    geojson.Polygon(
        coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]], validate=True
    ),
    geojson.MultiPolygon(
        coordinates=[
            [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
            [[(20, 20), (30, 20), (30, 30), (20, 30), (20, 20)]],
        ],
        validate=True,
    ),
]


@pytest.mark.parametrize(
    "geometry",
    VALID_GEOMETRIES,
)
def test_fix_feature(geometry):
    feature = geojson.Feature(geometry=geometry)
    result = fix_geojson(feature)
    assert feature == result


@pytest.mark.parametrize("geometries", itertools.permutations(VALID_GEOMETRIES, 2))
def test_fix_geometry_collection(geometries):
    geometry = geojson.GeometryCollection(geometries=geometries)
    result = fix_geojson(geometry)
    assert geometry == result


@pytest.mark.parametrize("geometries", itertools.permutations(VALID_GEOMETRIES, 2))
def test_fix_feature_collection(geometries):
    geometry = geojson.FeatureCollection(
        features=[geojson.Feature(geometry=geometry) for geometry in geometries]
    )
    result = fix_geojson(geometry)
    assert geometry == result
