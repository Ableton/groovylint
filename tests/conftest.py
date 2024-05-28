# Copyright (c) 2021 Ableton AG, Berlin. All rights reserved.

"""Test configuration for groovylint tests."""

from typing import Dict

import pytest


@pytest.fixture()
def default_jar_versions() -> Dict[str, str]:
    """Return a dict for default JAR versions."""
    return {
        "CodeNarc": "1.0.0",
        "GMetrics": "1.0.0",
        "activation": "1.0.0",
        "jaxb-api": "1.0.0",
        "slf4j-api": "1.0.0",
        "slf4j-simple": "1.0.0",
    }
