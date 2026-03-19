import sys
from pathlib import Path

import pytest


pytest_plugins = ("pytest_asyncio",)


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

    # Also reset the non-prefixed import path (channels.marine_base) to handle
    # dual-import scenarios where both sys.path entries resolve the same file.
    try:
        from channels import marine_base as channels_marine_base
        if channels_marine_base is not backend_marine_base:
            channels_marine_base._default_registry = channels_marine_base.ChannelRegistry()
    except ImportError:
        pass

    yield

    backend_marine_base._default_registry = backend_marine_base.ChannelRegistry()
    try:
        from channels import marine_base as channels_marine_base
        if channels_marine_base is not backend_marine_base:
            channels_marine_base._default_registry = channels_marine_base.ChannelRegistry()
    except ImportError:
        pass