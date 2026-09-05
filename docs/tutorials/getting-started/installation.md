# Install FiveTwenty

Install FiveTwenty in a Python 3.10 or later environment. You will need an OANDA
v20 account for the next tutorial, where you configure and test API access.

## Create an environment and install

Choose uv or pip. With uv, create a project, install the packages and print the
installed FiveTwenty version:

```bash
uv init my-oanda-app
cd my-oanda-app
uv add fivetwenty python-dotenv
uv run python -c "from importlib.metadata import version; print(version('fivetwenty'))"
```

With pip, create and activate a virtual environment, then install the packages and
print the version:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install fivetwenty python-dotenv
python -c "from importlib.metadata import version; print(version('fivetwenty'))"
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.
`python-dotenv` is optional; the tutorials use it to load configuration from `.env`.
Both commands install HTTPX and Pydantic automatically as FiveTwenty dependencies.

## Check your installation

The final command in either sequence should print a version number. If it reports
that the package cannot be found, check that you are using the environment where
you installed it. Use `uv run` in a uv project, or activate your virtual environment
before running Python.

Once the package is installed, continue with [authentication](authentication.md)
to load your credentials and make a read-only request.

## Upgrades

While FiveTwenty is below version 1.0, minor releases may include breaking changes.
Pin the version in your application's dependency file, keep its lockfile, and read
the [changelog](https://github.com/NimbleOx/fivetwenty/blob/main/CHANGELOG.md) before
upgrading. The [testing guide](../../contributing/testing-guide.md) lists the Python
versions and minimum dependencies tested in CI.
