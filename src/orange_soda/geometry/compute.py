import datetime

from geojson_pydantic import Feature, LineString
from sgp4.conveniences import sat_epoch_datetime
from skyfield.api import EarthSatellite, load, wgs84

from orange_soda.geometry.properties import Properties
from orange_soda.orbit import Propagator


def _convert_to_utc(time: datetime.datetime) -> datetime.datetime:
    """Convert a datetime.datetime to UTC.

    If there is no timezone information, assume the time is UTC.
    """
    if time.tzinfo is None:
        time = time.replace(tzinfo=datetime.timezone.utc)
    else:
        time = time.astimezone(datetime.timezone.utc)
    return time


def _trange(
    start: datetime.datetime, stop: datetime.datetime, step: float
) -> list[datetime.datetime]:
    start = _convert_to_utc(start)
    stop = _convert_to_utc(stop)
    step = datetime.timedelta(seconds=step)
    times = []
    while start < stop:
        times.append(start)
        start += step
    return times


def ground_track(
    propagator: Propagator,
    start: datetime.datetime,
    stop: datetime.datetime,
    step: float = 10.0,
) -> Feature:
    # Generate and plot the ground track coordinates
    ts = load.timescale()
    satrec = propagator.find_satrec(start)
    sat = EarthSatellite.from_satrec(satrec, ts)

    ts = load.timescale()
    times = _trange(start, stop, step=step)
    times = ts.from_datetimes(times)
    geo = wgs84.subpoint_of(sat.at(times))

    coords = [
        (lon, lat) for lon, lat in zip(geo.longitude.degrees, geo.latitude.degrees)
    ]
    print(coords)
    line_string = LineString(type="LineString", coordinates=coords)
    properties = Properties(
        satnum=satrec.satnum_str,
        start=start,
        stop=stop,
    )
    feature = Feature(type="Feature", geometry=line_string, properties=properties)

    return feature
