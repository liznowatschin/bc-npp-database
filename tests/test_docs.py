import importlib.util
from pathlib import Path


def test_docs_conf_imports():
    conf_path = Path(__file__).resolve().parents[1] / "docs" / "conf.py"
    spec = importlib.util.spec_from_file_location("bc_npp_docs_conf", conf_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.project == "BC-NPPD"
