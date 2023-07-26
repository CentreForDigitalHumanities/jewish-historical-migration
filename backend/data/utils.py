import re

pattern = re.compile(r"[˚';]")

def to_decimal(x: str):
    """Transform the manually provided coordinates into decimal values.
    These are patterns like 39˚ 39' 4'' N, but also 39˚15'N
    """
    if not x or x.strip() == 'unknown':
        return None
    values = pattern.split(x)
    if len(values) == 2:
        # only degrees provided
        d, direc = values
        m = s = 0
    elif len(values) == 3:
        # degrees and minutes provided
        d, m, direc = values
        s = 0
    elif len(values) == 5:
        d, m, s = values[:3]
        direc = values[-1].strip()
    else:
        # Invalid value; return None
        print('Warning: {} -> invalid coordinates'.format(x))
        return None
    dec = int(float(d)) + int(float(m)) / 60. + int(float(s)) / 3600.
    if direc == 'W' or direc == 'S':
        dec = -dec
    return dec
