import re
from typing import Dict

_SECTION_START = re.compile(r'^(\S+)\s+(.*)')

def kvp_to_dict(text: str) -> dict:
    args = [kvp.split('=', maxsplit=1) for kvp in text.strip().split()]
    obj = {k.lower(): v for k, v in args}
    return obj

def parse_labelfile(text: str) -> Dict[str, dict]:
    sections: Dict[str, dict] = {}

    current_section = None
    for line in text.splitlines():
        if m := _SECTION_START.match(line):
            label, rest = m.groups()
            current_section = label.lower()
            if current_section in ('comments', 'comment'):
                current_section = 'comments'
                sections[current_section] = rest.strip()
            else:
                sections[current_section] = kvp_to_dict(rest)
        else:
            if current_section == 'comments':
                sections[current_section] += ' ' + line.strip()
            else:
                sections[current_section].update(kvp_to_dict(line))

    return sections
