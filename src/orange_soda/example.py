import datetime

from orange_soda.geometry.compute import ground_track
from orange_soda.matplotlib import Map
from thistle import Propagator, TLEReader

sample_tle = (
    "1 25544U 98067A   21066.03644377  .00001043  00000-0  28659-4 0  9998",
    "2 25544  51.6440  98.4988 0002384  73.8823  47.6565 15.48970718398728",
)


def test():
    map = Map()

    tle_reader = TLEReader()
    tle_reader.read("tests/data/25544.tle")
    prop = Propagator(tle_reader.select(25544), method="epoch")

    t0 = datetime.datetime(2021, 3, 7, 0, 0, 0, tzinfo=datetime.UTC)
    t1 = t0 + datetime.timedelta(minutes=180)

    track = ground_track(prop, t0, t1)
    map.add_feature(track)

    map.figure.show()


if __name__ == "__main__":
    test()
    input("press any key to close...")
