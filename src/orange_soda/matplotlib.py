from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
from geojson_pydantic import Feature, LineString
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
        self.figure = plt.figure(figsize=np.array([360, 180]) / 25, layout="tight")
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

    # def _add_line_string(self, feature: Feature) -> None:
    # for lat,

    def add_line_string(
        self,
        line_string: LineString,
        color: str = "b",
        size: float = 3,
        alpha: float = 0.5,
    ) -> None:
        x, y = [], []
        for lon, lat in line_string.coordinates:
            x.append(lon)
            y.append(lat)
        self.axes.plot(x, y, "-", color=color, ms=size, alpha=alpha)

    # def add_ground_track(
    #     self,
    #     lats: list[float],
    #     lons: list[float],
    #     # color: str = "blue",
    #     size: float = 3,
    # ) -> None:
    #     # Convert the lat/lons to coordinates in the figure axes using the basemap
    #     pts = [self.basemap(lon, lat) for lon, lat in zip(lons, lats)]
    #     xpts = [p[0] for p in pts]
    #     ypts = [p[1] for p in pts]
    #     self.axes.plot(xpts, ypts, "-", ms=size, alpha=0.5)
