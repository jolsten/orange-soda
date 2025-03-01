import datetime

import geojson
from skyfield.api import EarthSatellite, load, wgs84

from orange_soda.utils import trange
from thistle import Propagator


def ground_track(
    propagator: Propagator,
    start: datetime.datetime,
    stop: datetime.datetime,
    step: float = 10.0,
) -> geojson.Feature:
    # Generate and plot the ground track coordinates
    ts = load.timescale()
    satrec = propagator.find_satrec(start)
    sat = EarthSatellite.from_satrec(satrec, ts)

    times = trange(start, stop, step=step)
    times = ts.from_datetimes(times)
    geo = wgs84.subpoint_of(sat.at(times))

    coords = [
        (lon, lat) for lon, lat in zip(geo.longitude.degrees, geo.latitude.degrees)
    ]
    line_string = geojson.LineString(type="LineString", coordinates=coords)
    properties = {
        "satnum": satrec.satnum_str,
        "start": start.isoformat(timespec="milliseconds", sep="T"),
        "stop": stop.isoformat(timespec="milliseconds", sep="T"),
    }
    feature = geojson.Feature(
        type="Feature", geometry=line_string, properties=properties
    )

    return feature
