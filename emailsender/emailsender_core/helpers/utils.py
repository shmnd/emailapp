
def get_absolute_url(request, path):
    """
    Returns an absolute URL based on the environment.
    Uses HTTP for local development and HTTPS for production.
    """
    return request.build_absolute_uri(path)