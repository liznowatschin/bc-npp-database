from bc_npp_database import __version__


def test_package_exposes_version():
    assert __version__ == "0.1.0a1"
