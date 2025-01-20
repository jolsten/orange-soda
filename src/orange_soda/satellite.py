import datetime

from skyfield.api import EarthSatellite, load, wgs84


def trange(
    start: datetime.datetime, stop: datetime.datetime, step: float
) -> list[datetime.datetime]:
    step = datetime.timedelta(seconds=step)
    times = []
    while start < stop:
        times.append(start)
        start += step
    return times


def ground_track(
    tle: tuple[str, str],
    start: datetime.datetime,
    stop: datetime.datetime,
    step: float = 60.0,
) -> tuple[list[float], list[float]]:
    # Generate and plot the ground track coordinates
    sat = EarthSatellite(tle[0], tle[1])

    ts = load.timescale()
    times = trange(start, stop, 60.0)
    times = ts.from_datetimes(times)
    geo = wgs84.subpoint_of(sat.at(times))

    return geo.latitude.degrees, geo.longitude.degrees
