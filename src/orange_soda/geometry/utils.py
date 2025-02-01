from typing import Union

from geojson_pydantic import LineString, MultiLineString


def split_lines_antimeridian(
    line_string: LineString,
) -> Union[LineString, MultiLineString]:
    new_coords = []
    return line_string
