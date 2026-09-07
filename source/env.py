import os
import sys

_ANDROID = (
    hasattr(sys, "getandroidapilevel")
    or "ANDROID_ARGUMENT" in os.environ
    or "ANDROID_BOOTLOGO" in os.environ
    or os.path.isdir("/system/app")
)


def is_android() -> bool:
    return _ANDROID
