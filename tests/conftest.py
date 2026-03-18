import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BACKEND = SRC / "backend"

for path in (str(ROOT), str(SRC), str(BACKEND)):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture(autouse=True)
def reset_default_registry():
    from backend.channels import marine_base as backend_marine_base

    backend_marine_base._default_registry = backend_marine_base.ChannelRegistry()
    yield
    backend_marine_base._default_registry = backend_marine_base.ChannelRegistry()