# Backend

The backend is a Django and Django REST Framework application backed by
PostgreSQL/PostGIS. It provides the Django admin at `/admin/`, an authenticated
read-only records API at `/api/records/`, and DRF session login at `/api-auth/`.
The root URL redirects to the admin interface.

Use the repository's Compose workflow for development. From the repository
root:

```console
podman compose up --build
podman compose run --rm backend pytest
```

The backend container waits for PostgreSQL, applies migrations, and serves on
<http://localhost:8100/>. The source directory is bind-mounted, so Django's
development server reloads changes without rebuilding the image. Rebuild after
changing a requirements lock or the Dockerfile.

Common management commands can run in the active service:

```console
podman compose exec backend python manage.py createsuperuser
podman compose exec backend python manage.py token USERNAME
podman compose exec backend python manage.py import_dataset /data/FILENAME.xlsx
podman compose exec backend python manage.py makemigrations
```

Production Python dependencies are pinned in `requirements.txt`; development
and test dependencies are pinned in `requirements-dev.txt`. A non-containerized
production environment installs only:

```console
pip install -r backend/requirements.txt
```

Deployments should provide Django settings, static-file handling, a WSGI server,
and the database.
