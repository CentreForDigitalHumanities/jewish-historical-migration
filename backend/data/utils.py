import re

pattern = re.compile(r'(\d+)˚ (\d+)\'(( \d+)\'\')? ?(.)')

def to_decimal(x: str):
    """Transform the manually provided coordinates into decimal values.
    These are patterns like 39˚ 39' 4''N, but also 39˚ 15' N
    """
    if not x or x.strip() == 'unknown':
        return None
    try:
        _, d, m, _, s, direc, _ = pattern.split(x)
    except ValueError:
        # Invalid value; return None
        print('Warning: {} -> invalid coordinates'.format(x))
        return None
    else:
        if s is None:
            s = 0
        dec = int(d) + int(m) / 60. + int(s) / 3600.
        if direc == 'W' or direc == 'S':
            dec = -dec
        return dec
