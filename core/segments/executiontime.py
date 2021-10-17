import promptvar, utils


def main(segment):
    text_inside = ""
    skip = False

    timer = promptvar.variables.get("timer", 0)

    if segment["type"] == "executiontime":
        if timer >= segment["properties"].get("threshold", 0):
            text_inside = utils.time_reformat_short(timer)
        else:
            skip = True

    return text_inside, skip
