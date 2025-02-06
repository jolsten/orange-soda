import numpy as np

# Define the WGS84 ellipsoid parameters
class Ellipsoid:
    def __init__(self, a, b, e2, el2):
        self.a = a  # semi-major axis
        self.b = b  # semi-minor axis
        self.e2 = e2  # eccentricity squared
        self.el2 = el2  # second eccentricity squared

# WGS84 Ellipsoid constants
WGS84_ELLIPSOID = Ellipsoid(
    a=6378137.0,         # semi-major axis (meters)
    b=6356752.314245,    # semi-minor axis (meters)
    e2=0.00669437999014, # first eccentricity squared
    el2=0.00673949674228 # second eccentricity squared
)

def angle_to_dcm(azimuth, elevation, tilt, convention):
    """
    Computes the Direction Cosine Matrix (DCM) for converting NED to ECEF.
    """
    sin_az, cos_az = np.sin(azimuth), np.cos(azimuth)
    sin_el, cos_el = np.sin(elevation), np.cos(elevation)
    sin_tilt, cos_tilt = np.sin(tilt), np.cos(tilt)

    if convention == 'XYZ':
        return np.array([
            [cos_az * cos_el, -sin_az, cos_az * sin_el],
            [sin_az * cos_el, cos_az, sin_az * sin_el],
            [-sin_el, 0, cos_el]
        ])
    else:
        raise ValueError(f"Unsupported convention: {convention}")

def ned_to_ecef(r_ned, lat, lon, h, translate=False):
    """
    Converts NED coordinates to ECEF coordinates. Optionally translates the result by the ECEF position of the NED origin.
    """
    # Convert input NED vector to numpy array
    r_ned = np.array(r_ned, dtype=float)
    
    # Convert lat and lon to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # Direction cosine matrix for converting NED to ECEF
    D_ecef_ned = angle_to_dcm(0, lat_rad + np.pi / 2, -lon_rad, 'XYZ')
    
    # Compute the ECEF coordinates
    r_ecef = np.dot(D_ecef_ned, r_ned)
    
    if not translate:
        return r_ecef
    else:
        # If translation is needed, calculate the ECEF position of the NED origin
        r_ned_ecef = geodetic_to_ecef(lat, lon, h)
        return r_ecef + np.array(r_ned_ecef)

def geodetic_to_ecef(lat, lon, h):
    """
    Converts geodetic coordinates (latitude, longitude, altitude) to ECEF.
    """
    # Convert latitude and longitude to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # WGS84 Ellipsoid parameters
    a = WGS84_ELLIPSOID.a
    e2 = WGS84_ELLIPSOID.e2

    # Prime vertical radius of curvature
    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)

    # ECEF coordinates
    x = (N + h) * np.cos(lat_rad) * np.cos(lon_rad)
    y = (N + h) * np.cos(lat_rad) * np.sin(lon_rad)
    z = ((1 - e2) * N + h) * np.sin(lat_rad)

    return x, y, z

def ecef_to_geodetic(r_e, ellipsoid=WGS84_ELLIPSOID):
    """
    Converts ECEF coordinates to geodetic coordinates (latitude, longitude, height).
    """
    # ECEF coordinates
    x, y, z = r_e
    
    # Ellipsoid parameters
    a = ellipsoid.a
    b = ellipsoid.b
    e2 = ellipsoid.e2
    el2 = ellipsoid.el2
    
    # Auxiliary calculations
    p = np.sqrt(x**2 + y**2)
    theta = np.arctan((z * a) / (p * b))
    
    sin_theta, cos_theta = np.sin(theta), np.cos(theta)
    
    # Longitude
    lon = np.arctan2(y, x)
    
    # Latitude
    lat = np.arctan2(z + el2 * b * sin_theta**3, p - e2 * a * cos_theta**3)
    
    # Calculate the radius of curvature
    sin_lat, cos_lat = np.sin(lat), np.cos(lat)
    N = a / np.sqrt(1 - e2 * sin_lat**2)
    
    # Height (altitude)
    if not (-0.01745240643728351 < cos_lat < 0.01745240643728351):
        h = p / cos_lat - N
    else:
        h = z / sin_lat - N * (1 - e2)
    
    return lat, lon, h

def ground_facility_visibility_circle(gf_wgs84, satellite_position_norm, azimuth_step=0.1, minimum_elevation=10):
    """
    Compute the ground facility visibility circle from the position `gf_wgs84` (WGS84) to a
    satellite in which its distance from the Earth's center is `satellite_position_norm` [m].
    It returns a vector of `NTuple{2, Float64}` where the first element is the latitude [rad]
    and the second is the longitude [rad] of each point in the visibility circle.
    """
    # Unpack the ground facility coordinates (latitude, longitude, altitude)
    gf_lat, gf_lon, gf_h = gf_wgs84

    # Create a vector of azimuth angles to consider in the analysis.
    vazimuth = np.arange(-np.pi, np.pi + azimuth_step, azimuth_step)

    # Obtain the ground facility position in the ECEF reference frame.
    gf_ecef = geodetic_to_ecef(gf_lat, gf_lon, gf_h)

    # Distance between the Earth's center and the ground station.
    r_gf = np.linalg.norm(gf_ecef)

    # Compute the distance `r` from the ground facility to the satellite considering the
    # minimum elevation angle.
    sin_theta, cos_theta = np.sin(minimum_elevation), np.cos(minimum_elevation)
    print(satellite_position_norm**2)
    print((r_gf * cos_theta)**2)
    print(satellite_position_norm**2 - (r_gf * cos_theta)**2)
    r = -r_gf * sin_theta + np.sqrt(satellite_position_norm**2 - (r_gf * cos_theta)**2)

    # Allocate the list for the visibility circle.
    gf_visibility = []

    for az in vazimuth:
        # Compute the direction to the intersection of the visibility region considering the
        # minimum elevation angle and the current azimuth.
        D_l_ned = angle_to_dcm(az, minimum_elevation, 0, 'XYZ')
        D_ned_l = D_l_ned.T
        r_ned = np.dot(D_ned_l, np.array([r, 0, 0]))

        # Convert the position vector to ECEF and obtain the latitude and longitude of the
        # intersection point.
        r_ecef = ned_to_ecef(r_ned, gf_lat, gf_lon, gf_h, translate=True)
        lat, lon, _ = ecef_to_geodetic(r_ecef)

        # Add the result to the list.
        gf_visibility.append((np.rad2deg(lat), np.rad2deg(lon)))

    return gf_visibility
