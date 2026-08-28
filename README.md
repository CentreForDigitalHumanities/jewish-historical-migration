# Jewish Historical Migration

An interface for creating and curating a dataset to study Jewish Historical
Migration. See the [project description](https://www.uu.nl/en/news/new-interactive-platform-for-researching-historical-jewish-migration-data).

The application is a Django backend. Dataset editors use Django's admin
interface, while authenticated clients can read records through the Django
REST Framework API. The root URL redirects to `/admin/`; the API and its login
are available at `/api/` and `/api-auth/`.

## Development with containers

The development and test environment uses a containerized setup with
Podman Compose. The Podman commands can be changed to use Docker.

Copy `.env.example` to `.env` and set `DATA_DIR` to a host directory containing
source data. Then build and start PostgreSQL and Django:

```console
podman compose up --build
```

The backend runs at <http://localhost:8100/>. Migrations run automatically when
it starts, and both `backend/` and `DATA_DIR` are bind-mounted for development.
Stop the stack with Ctrl-C followed by:

```console
podman compose down
```

Create an administrator and run data-management commands in the running
backend container:

```console
podman compose exec backend python manage.py createsuperuser
podman compose exec backend python manage.py token USERNAME
podman compose exec backend python manage.py import_dataset /data/FILENAME.xlsx
```

## Tests

Run Django's unit tests in the development image:

```console
podman compose run --rm backend pytest
```

Run the Selenium tests in containerized Chromium. Compose starts the
backend and waits for its healthcheck before launching the browser tests:

```console
podman compose --profile tests run --rm functional-tests
```

The functional tests covers the root redirect, admin, API root, and DRF login.

## Python dependencies

`backend/requirements.in` and `backend/requirements.txt` contain the main
(production) dependencies. `backend/requirements-dev.in` extends this with
the test, browser, and dependency-management tools used by the development containers.
The development lock file is constrained by the production lock so runtime package
versions are the same and can be installed in a single venv.

To regenerate both lock files, in order, from the development image:

```console
podman compose run --rm --no-deps backend pip-compile requirements.in
podman compose run --rm --no-deps backend pip-compile --constraint requirements.txt --output-file requirements-dev.txt requirements-dev.in
```

Commit each input file with its compiled lockfile.
Production environments should install the production dependencies directly;
the container setup is for development use only:

```console
pip install -r backend/requirements.txt
```

## Releases

The version shown in the Django admin footer is maintained in
`backend/jhm/__init__.py`. Before creating a release, update `__version__` in
the release commit so it exactly matches the unprefixed Git tag, such as
`0.3.0`, and then tag that commit.

## Application commands

The only API endpoint is `/api/records/`, a read-only viewset available to
authenticated users through session or token authentication. Create or retrieve
a token with `python manage.py token <username>`.

Import the source Excel dataset with `python manage.py import_dataset <path>`.
See [backend/README.md](backend/README.md) for backend-specific notes and
[functional-tests/README.md](functional-tests/README.md) for functional test details.
