"""AC-040: the app needs no external service, payment provider or API key."""

import os
import re
import subprocess
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent.parent
_SETTINGS = ("DATABASE_URL", "JWT_SECRET_KEY", "ALLOWED_ORIGINS")
_EXTERNAL = ("stripe", "paypal", "braintree", "openai", "sendgrid", "twilio", "boto3", "mailgun")


def _run_without_settings(code: str) -> str:
    env = {k: v for k, v in os.environ.items() if k not in _SETTINGS}
    done = subprocess.run(
        [sys.executable, "-c", code],
        cwd=_BACKEND,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout.strip()


def test_ac040_the_default_database_is_a_local_file() -> None:
    url = _run_without_settings("from app.database import DATABASE_URL; print(DATABASE_URL)")
    assert url.startswith("sqlite:///")


def test_ac040_the_app_loads_with_no_setting_at_all() -> None:
    out = _run_without_settings("import app.main, app.auth; print('loaded')")
    assert out == "loaded"


def test_ac040_no_external_service_package_is_required() -> None:
    requirements = (_BACKEND / "requirements.txt").read_text().lower()
    assert not [name for name in _EXTERNAL if name in requirements]


def test_ac040_app_code_imports_no_external_service_client() -> None:
    pattern = re.compile(r"^\s*(?:import|from)\s+(" + "|".join(_EXTERNAL) + r")\b", re.M)
    found = [
        path.name for path in (_BACKEND / "app").rglob("*.py") if pattern.search(path.read_text())
    ]
    assert found == []
