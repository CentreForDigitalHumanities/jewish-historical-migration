from pathlib import Path

from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index(request):
    """ Thin wrapper for the static index.html that adds the CSRF cookie."""
    index_path = finders.find('index.html')
    if index_path is None:
        raise Http404('No frontend index.html is configured.')

    return HttpResponse(
        content=Path(index_path).read_bytes(),
        content_type='text/html',
    )
