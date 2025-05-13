# maybe not the best name for this module idk


def build_url(url: str, **query_params):
    url += "?"
    for name, value in query_params.items():
        url += f"{name}={value}"
    return url
