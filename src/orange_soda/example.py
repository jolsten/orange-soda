import datetime

from orange_soda.geometry.compute import ground_track
from orange_soda.geometry.ground_site import GroundSite
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

    # from sgp4.conveniences import sat_epoch_datetime
    # print([sat_epoch_datetime(sat) for sat in prop.satrecs])

    t0 = datetime.datetime(2021, 3, 7, 1, 0, 0, tzinfo=datetime.UTC)
    t1 = t0 + datetime.timedelta(minutes=60)

    track = ground_track(prop, t0, t1, step=60)
    map.add_feature(track, "b-")

    gs = GroundSite(lat=30, lon=-60, alt=0, name="Site A")
    gs_point = gs.to_geojson()
    gs_circle = gs.satellite_visibility_ring(500)
    map.add_feature(gs_point, "b*", markersize=5)
    print(gs_circle)
    map.add_feature(gs_circle)

    # gs_vis = ground_site(0, 30, target_alt=500_000)
    # map.add_feature_collection(gs_vis)

    map.figure.show()


if __name__ == "__main__":
    test()
    input("press any key to close...")
