from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
from geojson_pydantic import Feature, LineString, Point
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.basemap import Basemap


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

    def _add_point(
        self,
        point: Point,
        color: str = "b",
        size: float = 3,
        alpha: float = 0.5,
    ) -> None:
        lon, lat = self.basemap(point.longitude, point.latitude)
        self.axes.plot([lon], [lat], color=color, ms=size, alpha=alpha)

    def _add_line_string(
        self,
        line_string: LineString,
        color: str = "b",
        size: float = 3,
        alpha: float = 0.5
    ) -> None:
        lons, lats = [], []
        for point in line_string.coordinates:
            lon, lat = self.basemap(point.longitude, point.latitude)
            lons.append(lon)
            lats.append(lat)
        self.axes.plot(lons, lats, "-", color=color, ms=size, alpha=alpha)

    def add_feature(self, feature: Feature) -> None:
        geometry = feature.geometry
        match geometry.type:
            case "LineString":
                self._add_line_string(geometry)
            case _:
                msg = f"GeoJSON Feature type {feature.type!r} is not implemented"
                raise TypeError(msg)
