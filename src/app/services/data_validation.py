from src.app.services.external_apis import ExternalAPIError


def validate(genderize, agify, nationalize) -> None | ExternalAPIError:
    """

    :param genderize: genderize API JSON response
    :param agify: agify API JSON response
    :param nationalize: nationalize API JSON response
    :return: None

    Edge Case Handling

    genderize returns gender: null or count: 0 → return 502, do not store
    agify returns age: null → return 502, do not store
    nationalize returns no country data → return 502, do not store
    """

    if genderize.get("gender") is None or genderize.get("count") == 0:
        raise ExternalAPIError("Genderize")

    if agify.get("age") is None:
        raise ExternalAPIError("Agify")

    if not nationalize.get("country"):
        raise ExternalAPIError("Nationalize")
