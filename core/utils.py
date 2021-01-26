def time_reformat(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)

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
