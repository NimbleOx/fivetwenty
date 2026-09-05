# Install FiveTwenty

You need Python 3.10 or later and access to an OANDA v20 account. This page installs
the library and verifies that Python can import it; it makes no API requests.

## Create an environment and install

With uv:

```bash
uv init my-oanda-app
cd my-oanda-app
uv add fivetwenty python-dotenv
uv run python -c "from importlib.metadata import version; print(version('fivetwenty'))"
```

Or use a virtual environment and pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install fivetwenty python-dotenv
python -c "from importlib.metadata import version; print(version('fivetwenty'))"
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.
`python-dotenv` is optional; the tutorials use it to load configuration from `.env`.
The SDK's direct runtime dependencies are HTTPX and Pydantic.

## Verify the interpreter

If importing fails after installation, check that the script uses the interpreter
from the environment where the package was installed. Use `uv run` consistently in
a uv project, or `python -m pip` with the activated interpreter.

An import check does not validate OANDA credentials. Continue with
[authentication](authentication.md) to configure and test a read-only request.

## Upgrades

This is beta software. Pin the version in your application's dependency file, keep
its lockfile, and review compatibility notes before upgrading. The repository
[testing guide](../../contributing/testing-guide.md) describes the Python versions
and minimum dependencies exercised by CI.
