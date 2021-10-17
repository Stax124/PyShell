from io import StringIO
from html.parser import HTMLParser


def time_reformat(duration: int) -> str:
    "Format seconds to time in hours, minutes and seconds"

    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append('{} days'.format(int(days)))
    if hours > 0:
        duration.append('{} hours'.format(int(hours)))
    if minutes > 0:
        duration.append('{} minutes'.format(int(minutes)))
    if seconds > 0:
        duration.append('{} seconds'.format(seconds))

    return ', '.join(duration)


def time_reformat_short(duration: int) -> str:
    "Format miliseconds to time in hours, minutes, seconds and miliseconds"

    seconds, miliseconds = divmod(duration, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append('{}d'.format(days))
    if hours > 0:
        duration.append('{}h'.format(hours))
    if minutes > 0:
        duration.append('{}m'.format(minutes))
    if seconds > 0:
        duration.append('{}s'.format(seconds))
    if miliseconds > 0:
        duration.append('{}ms'.format(miliseconds))

    return ' '.join(duration)


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MiB'
        1253656678 => '1.17GiB'
    """
    factor = 1024
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_from_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MiB'
        1253656678 => '1.17GiB'
    """
    factor = 1024
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes *= factor


def prime(l: list) -> list:
    """
    Returns prime factors of n as a list.
    """
    for item in l:
        n = item
        i = 2
        factors = []
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        if n > 1:
            factors.append(n)
        print(f"{item}={factors}")


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
