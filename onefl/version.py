"""
Goal: provide access to the version information
"""

try:
    import pkg_resources
    __version__ = pkg_resources.require("deduper")[0].version
except Exception:
    from setuptools_scm import get_version
    __version__ = get_version()


if __name__ == "__main__":
    print(__version__)
