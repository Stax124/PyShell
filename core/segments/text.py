def main(segment):
    text = segment.get("properties", {}).get("text", "")
    return text, False if text else True
