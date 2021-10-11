import sys
import os


def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix


def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix


def main(segment: dict):
    if in_virtualenv():
        return os.path.basename(sys.prefix), False
    else:
        return "", True
