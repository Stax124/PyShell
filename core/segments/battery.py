from psutil import sensors_battery


def main(segment):
    battery = sensors_battery()

    if battery:
        percent = str(battery.percent)

        return percent, False

    return "", True
