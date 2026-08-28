from . import __version__


def application_metadata(_request):
    return {'jhm_version': __version__}
