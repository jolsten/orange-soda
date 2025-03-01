import datetime
import webbrowser

import folium

from orange_soda.antimeridian import fix_geojson
from orange_soda.ground_site import point, visibility_circle
from orange_soda.satellite import ground_track
from thistle import Propagator, TLEReader

sample_tle = (
    "1 25544U 98067A   21066.03644377  .00001043  00000-0  28659-4 0  9998",
    "2 25544  51.6440  98.4988 0002384  73.8823  47.6565 15.48970718398728",
)


def test():
    # map = Map()
    map = folium.Map(location=[0, 0], zoom_start=1)

    tle_reader = TLEReader()
    tle_reader.read("tests/data/25544.tle")
    prop = Propagator(tle_reader.select(25544), method="epoch")

    t0 = datetime.datetime(2021, 3, 7, 1, 0, 0, tzinfo=datetime.UTC)
    t1 = t0 + datetime.timedelta(minutes=60)

    track = ground_track(prop, t0, t1, step=60)
    folium.GeoJson(fix_geojson(track)).add_to(map)
    # map.add_feature(track, color="r")
    # map.add_feature(track)

    gs = point(lat=30, lon=30, name="Site A")
    folium.GeoJson(gs)

    vis = visibility_circle(lat=30, lon=-45, alt_m=0, sat_alt_m=500_000, min_el=0.0)
    vis = fix_geojson(vis)
    folium.GeoJson(vis).add_to(map)

    map.save("index.html")
    webbrowser.open("index.html")

    # gs = GroundSite(lat=30, lon=-60, alt=0, name="Site A")
    # gs_point = gs.to_geojson()
    # gs_circle = gs.satellite_visibility_ring(500)
    # map.add_feature(gs_point, color="b", marker=".", markersize=5)
    # map.add_feature(gs_circle, color="b")

    # gs_vis = ground_site(0, 30, target_alt=500_000)
    # map.add_feature_collection(gs_vis)

    # map.figure.show()


if __name__ == "__main__":
    test()
    # input("press any key to close...")
