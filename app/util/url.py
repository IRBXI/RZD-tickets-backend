def build_url(url: str, **query_params):
    if "?" not in url:
        url += "?"
        items = list(query_params.items())
        url += f"{items[0][0]}={items[0][1]}"
        for name, value in list(query_params.items())[1:]:
            url += f"&{name}={value}"
        return url
    for name, value in list(query_params.items()):
        url += f"&{name}={value}"
    return url
