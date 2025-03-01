import warnings
from typing import Literal, Optional, Union

import antimeridian
import geojson
import geojson_pydantic as geopy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap

from orange_soda.features import VisibilityRing
from orange_soda.utils import Coordinate

Geometry = Union[
    geojson.Point,
    geojson.MultiPoint,
    geojson.LineString,
    geojson.MultiLineString,
    geojson.Polygon,
    geojson.MultiPolygon,
]


class Map:
    figure: Figure
    axes: Axes
    basemap: Basemap

    def __init__(
        self,
        style: Literal["gray", "bluemarble"] = "gray",
        parallels: Optional[int] = 30,
        meridians: Optional[int] = 60,
        limits: tuple[float, float, float, float] = (-90, 90, -180, 180),
    ) -> None:
        self.figure = plt.figure(figsize=np.array([360, 180]) / 40, layout="tight")
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.basemap = Basemap(
            ax=self.axes,
            projection="cyl",
            llcrnrlat=limits[0],
            urcrnrlat=limits[1],
            llcrnrlon=limits[2],
            urcrnrlon=limits[3],
            resolution="l",
            rsphere=(6378137.00, 6356752.3142),
        )

        if style == "gray":
            self.basemap.drawcoastlines(linewidth=0.5)
            self.basemap.drawcountries(linewidth=0.5)
            self.basemap.fillcontinents(color="silver", lake_color="gainsboro")
            self.basemap.drawmapboundary(fill_color="gainsboro")
        elif style == "bluemarble":
            self.basemap.bluemarble(ax=self.axes, scale=0.5)
        else:
            msg = f"Map style choice {style!r} not valid"
            raise ValueError(msg)

        if parallels is not None:
            self.basemap.drawparallels(np.arange(-90.0, 91.0, parallels))

        if meridians is not None:
            self.basemap.drawmeridians(np.arange(-180.0, 181.0, meridians))

    def plot_vis_ring(self, vis_ring: VisibilityRing, color: Optional[str] = None):
        vis_ring = antimeridian.fix_geojson(vis_ring)

    def _plot_point(
        self, geometry: geopy.Point, label: Optional[str] = None, *args, **kwargs
    ):
        coord = geometry.coordinates
        x, y = self.basemap(coord.lon, coord.lat)
        self.axes.plot(x, y, *args, **kwargs)
        # TODO: Add a label for the point name?

    def plot_multi_point(self, coords: list[Coordinate], *args, **kwargs):
        for c in coords:
            self.plot_point(c, *args, **kwargs)

    def plot_line(self, coords: list[Coordinate], *args, **kwargs):
        x, y = [], []
        for c in coords:
            a, b = self.basemap(c.lon, c.lat)
            x.append(a)
            y.append(b)
        self.axes.plot(x, y, *args, **kwargs)

    def plot_multi_line(self, coords: list[list[Coordinate]], *args, **kwargs):
        for c in coords:
            self.add_line(c, *args, **kwargs)

    def plot_polygon(self, coords: list[Coordinate], *args, **kwargs):
        x, y = [], []
        for c in coords:
            a, b = self.basemap(c.lon, c.lat)
            x.append(a)
            y.append(b)
        self.axes.plot(x, y, *args, **kwargs)

    def plot_multi_polygon(self, coords: list[list[Coordinate]], *args, **kwargs):
        for c in coords:
            self.plot_polygon(c, *args, **kwargs)

    def coords_to_map(
        self, coords: list[Coordinate]
    ) -> tuple[list[float], list[float], list[float]]:
        x, y, z = [], [], []
        for c in coords:
            a, b = self.basemap(c.lon, c.lat)
            x.append(a)
            y.append(b)
            z.append(c.alt)
        return x, y, z

    def geometry_to_coords(self, geometry: Geometry) -> list[Coordinate]:
        result = []
        for coords in np.atleast_2d(geometry["coordinates"]):
            if len(coords) == 2:
                lon, lat = coords
                c = Coordinate(lon=lon, lat=lat)
            elif len(coords) == 3:
                lon, lat, alt = coords
                c = Coordinate(lon=lon, lat=lat, alt=alt)
            else:
                raise ValueError
            result.append(c)
        return result

    def plot_coords(self, coords: list[Coordinate], *args, **kwargs):
        x, y, _ = self.coords_to_map(coords)
        self.axes.plot(x, y, *args, **kwargs)

    def _add_point(
        self,
        point: geojson.Point,
        *args,
        **kwargs,
    ) -> None:
        lon, lat = point["coordinates"][0:2]
        lon, lat = self.basemap(lon, lat)
        self.axes.plot([lon], [lat], *args, **kwargs)

    def _add_line_string(self, geometry: geojson.LineString, *args, **kwargs) -> None:
        x, y = [], []
        for coords in geometry["coordinates"]:
            lon, lat, *_ = coords
            a, b = self.basemap(lon, lat)
            x.append(a)
            y.append(b)
        self.axes.plot(x, y, *args, **kwargs)

    def _add_polygon(self, geometry: geojson.Polygon, *args, **kwargs) -> None:
        lons, lats = [], []
        for coords in geometry["coordinates"][0]:
            lon, lat = self.basemap(coords[0], coords[1])
            lons.append(lon)
            lats.append(lat)
        self.axes.fill(lons, lats, *args, **kwargs)

        if len(geometry["coordinates"]) > 1:
            warnings.warn("Cannot un-fill inner shapes!")

    def add_feature_collection(
        self, feature_collection: geojson.FeatureCollection, *args, **kwargs
    ) -> None:
        if not isinstance(feature_collection, geojson.FeatureCollection):
            raise TypeError

        for feature in feature_collection["features"]:
            self.add_feature(feature, *args, **kwargs)

    def add_geojson(
        self, object: Union[geojson.Feature, geojson.FeatureCollection], *args, **kwargs
    ):
        if object["type"] == "Feature":
            geometry = object["geometry"]
            self._add_geometry(geometry, *args, **kwargs)
        elif object["type"] == "FeatureCollection":
            for feature in object["features"]:
                geometry = feature["geometry"]
                self._add_geometry(geometry, *args, **kwargs)
        else:
            msg = f"object must look like a GeoJSON Feature or FeatureCollection but got {type(object)}"
            raise TypeError(msg)

    def _add_geometry(self, geometry: Geometry, *args, **kwargs):
        type_ = geometry["type"]
        if type_ in ("Point", "MultiPoint"):
            coords = self.geometry_to_coords(geometry)
            self.plot_coords(coords, *args, **kwargs)
        elif type_ == "LineString":
            coords = self.geometry_to_coords(geometry)
            self.plot_coords(coords, *args, **kwargs)
        elif type_ == "MultiLineString":
            for coord in geometry["coordinates"]:
                coords = self.geometry_to_coords(geometry)

    def _add_feature(self, feature: geojson.Feature, *args, **kwargs) -> None:
        if not isinstance(feature, geojson.Feature):
            msg = f"add_feature() expects argument of type 'Feature', not {feature.type!r}"
            raise TypeError(msg)

        try:
            feature = antimeridian.fix_geojson(feature)
        except ValueError:
            pass

        geometry = feature.geometry
        match geometry["type"]:
            case "Point":
                self._add_point(geometry, *args, **kwargs)
            case "LineString":
                self._add_line_string(geometry, *args, **kwargs)
            case "MultiLineString":
                for segment in geometry["coordinates"]:
                    tmp_feature = geojson.Feature(
                        geometry=geojson.LineString(coordinates=segment)
                    )
                    self.add_feature(tmp_feature, *args, **kwargs)
            case "Polygon":
                self._add_polygon(geometry, *args, **kwargs)
            case "MultiPolygon":
                for polygon in geometry["coordinates"]:
                    tmp_feature = geojson.Feature(
                        geometry=geojson.Polygon(coordinates=polygon),
                    )
                    self.add_feature(tmp_feature, *args, **kwargs)
            case _:
                msg = f"GeoJSON Feature type {feature.type!r} is not implemented"
                raise TypeError(msg)
