"""
Goal: provide access to the version information
"""

DEFAULT_VERISON = '0.0.6'

try:
    import pkg_resources
    __version__ = pkg_resources.require("deduper")[0].version
except Exception:
    from setuptools_scm import get_version
    try:
        __version__ = get_version()
    except Exception:
        __version__ = DEFAULT_VERISON


if __name__ == "__main__":
    print(__version__)
