import datetime

from orange_soda.map import Map2D
from orange_soda.satellite import ground_track

sample_tle = (
    "1 25544U 98067A   21066.03644377  .00001043  00000-0  28659-4 0  9998",
    "2 25544  51.6440  98.4988 0002384  73.8823  47.6565 15.48970718398728",
)


def test():
    map = Map2D()

    t0 = datetime.datetime(2021, 3, 7, 0, 0, 0, tzinfo=datetime.UTC)
    t1 = datetime.datetime(2021, 3, 7, 1, 0, 0, tzinfo=datetime.UTC)

    lats, lons = ground_track(sample_tle, t0, t1)
    map.add_ground_track(lats, lons)

    map.figure.show()


if __name__ == "__main__":
    test()
    input("press any key to close...")
