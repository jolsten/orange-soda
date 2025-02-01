import datetime

from orange_soda.geometry.compute import ground_track
from orange_soda.io.tle import TLEReader
from orange_soda.matplotlib import Map
from orange_soda.orbit import Propagator

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
    t1 = datetime.datetime(2021, 3, 7, 0, 30, 0, tzinfo=datetime.UTC)

    track = ground_track(prop, t0, t1)
    map.add_line_string(track.geometry)
    print(track.geometry.coordinates)

    map.figure.show()


if __name__ == "__main__":
    test()
    input("press any key to close...")
