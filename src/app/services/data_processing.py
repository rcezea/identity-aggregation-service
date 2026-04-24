# data_processing.py

def serialize(genderize, agify, nationalize) -> dict:
    """
    Data aggregation
    :param genderize: genderize API JSON response
    :param agify: agify API JSON response
    :param nationalize: nationalize API JSON response
    :return: a normalized object from raw API responses
    """
    countries = nationalize.get("country")
    country = max(countries, key=lambda x: x["probability"])

    data = {
        "name": genderize.get("name"),
        "gender": genderize.get("gender"),
        "gender_probability": genderize.get("probability"),
        "age": agify.get("age"),
        "country_id": country.get("country_id"),
        "country_name": country.get("country_name", ""),
        "country_probability": country.get("probability"),
    }

    return data


def serializer(data) -> dict:
    """
    Data presentation
    :param data: stored user object from database
    :return: a normalized object from database
    """
    return {
        "id": data.id,
        "name": data.name,
        "gender": data.gender,
        "gender_probability": data.gender_probability,
        "age": data.age,
        "age_group": data.age_group,
        "country_id": data.country_id,
        "country_name": data.country_name,
        "country_probability": data.country_probability,
        "created_at": data.created_at.isoformat() + "Z",
    }
