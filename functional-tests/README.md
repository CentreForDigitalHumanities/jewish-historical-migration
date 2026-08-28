# Functional tests

This pytest/Selenium suite checks the backend through a Chromium browser.
It covers the root-to-admin redirect, and direct access to the Django admin,
API root, and DRF login page.

Run it from the repository root with the Compose test profile:

```console
podman compose --profile tests run --rm functional-tests
```

The `functional-tests` service uses the Dockerfile's `browser-tests` stage,
which adds Debian Chromium and its matching WebDriver to the shared development
Python environment. Compose starts the backend and waits until it is healthy
before pytest connects to `http://backend:8100/`.

To target another already-running instance from a compatible environment, pass
a URL with a trailing slash:

```console
pytest functional-tests --base-address http://localhost:8100/
```

The test browser used in the container is Chromium. The browser selection can be
overridden with pytest's `webdriver` ini option when running outside the container.
