# data_processing.py

def serialize(genderize, agify, nationalize) -> dict:
    countries = nationalize.get("country")
    country = max(countries, key=lambda x: x["probability"])

    data = {
        "name": genderize.get("name"),
        "gender": genderize.get("gender"),
        "gender_probability": genderize.get("probability"),
        "sample_size": genderize.get("count"),
        "age": agify.get("age"),
        "country_id": country.get("country_id"),
        "country_probability": country.get("probability"),
    }

    return data
