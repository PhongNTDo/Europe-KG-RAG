import os
import json


COUNTRIES_RAW_DATA_PATH = "./data/raw_data/europe_countries.json"
DATA_COUNTRIES_PATH = "./data/crawled_data/total-population-by-country-2025.json"

with open(DATA_COUNTRIES_PATH) as f:
        data_countries = json.load(f)

def find_country(country_name):
    for country in data_countries:
        if country['country'].lower() == country_name.lower():
            return country
    return None


def standardization_countries():
    with open(COUNTRIES_RAW_DATA_PATH) as f:
        data = json.load(f)

    countries = []
    for country in data['countries']:
        name = country['name']
        id = f"country:{name.upper().replace(' ', '_')}"

        country_information = find_country(name)
        if country_information is None:
            print(f"Country {name} not found")

        population = country_information['pop2025']
        area_km2 = country_information['area']
        density = country_information['density']
        cca2 = country_information['cca2']
        cca3 = country_information['cca3']
        population_work_rank = country_information['rank']

        item = {
            "id": id,
            "name": name,
            "population": population,
            "area_km2": area_km2,
            "density": density,
            "iso2": cca2,
            "iso3": cca3,
            "population_work_rank": population_work_rank
        }

        countries.append(item)
    with open("data/database/entities/europe_countries.json", "w") as f:
        json.dump({"countries": countries}, f, indent=4, ensure_ascii=False)


def standardization_rivers():
    RIVER_RAW_DATA = "./data/raw_data/europe_rivers.json"
    STANDARD_DATABASE_RIVER = "./data/database/entities/europe_rivers.json"
    with open(RIVER_RAW_DATA) as f:
        data = json.load(f)

    rivers = []
    for river in data['rivers']:
        name = river['name']
        id = f"river:{name.upper().replace(' ', '_')}"
        length = river['length']
        basin = river['basin']
        flow = river['flow']
        parent = river['parent']
        mounth = river['mounth']
        if length >= 100:
            item = {
                "id": id,
                "name": name,
                "length": length,
                "basin": basin,
                "flow": flow,
                "mounth": mounth
            }
        rivers.append(item)
    with open(STANDARD_DATABASE_RIVER, "w") as f:
        json.dump({"rivers": rivers}, f, indent=4, ensure_ascii=False)


def establish_relation_borders_with():
    COUNTRY_DATABASE = "./data/database/entities/europe_countries.json"
    COUNTRY_RAW_DATA = "./data/raw_data/europe_countries.json"
    with open(COUNTRY_DATABASE) as f:
        data_countries = json.load(f)
    with open(COUNTRY_RAW_DATA) as f:
        data = json.load(f)

    relations = []
    for country in data['countries']:
        for country_data in data_countries['countries']:
            if country_data['name'] == country['name']:
                source_id = country_data['id']
        for country_name in country['borders_with']:
            seen = False
            for country_data in data_countries['countries']:
                if country_data['name'] == country_name:
                    id = country_data['id']
                    relations.append({
                        "source_id": source_id,
                        "target_id": id,
                        "type": "BORDERS_WITH"
                    })
                    seen = True
                    break
            if not seen:
                print(f"Country {country_name} not found")

    with open("./data/database/relations/BORDERS_WITH.json", "w") as f:
        json.dump({"relations": relations}, f, indent=4, ensure_ascii=False)


def establish_relation_river_tributary():
    COUNTRY_DATABASE = "./data/database/entities/europe_rivers.json"
    COUNTRY_RAW_DATA = "./data/raw_data/europe_rivers.json"
    SEA_DATABASE = "./data/database/entities/sea.json"
    with open(COUNTRY_DATABASE) as f:
        data_rivers = json.load(f)
    with open(COUNTRY_RAW_DATA) as f:
        data = json.load(f)

    relations = []
    sea_database = []
    for river in data['rivers']:
        for river_data in data_rivers['rivers']:
            if river_data['name'] == river['name']:
                source_id = river_data['id']
        seen = False
        for river_data in data_rivers['rivers']:
            if river_data['name'] == river['parent']:
                target_id = river_data['id']
                seen = True
                break
        if not seen:
            print(f"River {river['parent']} not found")
            sea_id = f"sea:{river['parent'].upper().replace(' ', '_')}"
            if sea_id not in [sea['id'] for sea in sea_database]:

                sea_database.append({
                    "name": river['parent'],
                    "id": sea_id
                })
            target_id = sea_id
        relations.append({
            "source_id": source_id,
            "target_id": target_id,
            "type": "TRIBUTARY_OF"
        })


    with open("./data/database/relations/TRIBUTARY_OF.json", "w") as f:
        json.dump({"relations": relations}, f, indent=4, ensure_ascii=False)
    with open("./data/database/entities/europe_sea.json", "w") as f:
        json.dump({"sea": sea_database}, f, indent=4, ensure_ascii=False)


def standardization_cities():
    CITY_RAW_DATA = "data/crawled_data/europe-cities-by-population-2025.json"
    CITY_DATABASE = "data/database/entities/europe_cities.json"
    COUNTRY_RAW_DATA = "data/raw_data/europe_countries.json"
    COUNTRY_DATABASE = "data/database/entities/europe_countries.json"

    with open(CITY_RAW_DATA) as f:
        raw_data_city = json.load(f)
    with open(COUNTRY_RAW_DATA) as f:
        raw_data_country = json.load(f)
    with open(COUNTRY_DATABASE) as f:
        database_country = json.load(f)


    cities = []
    relations = []
    for city in raw_data_city:
        name = city['city']
        id = f"city:{name.upper().replace(' ', '_')}"
        population = city['population']
        lat = city['lat']
        lon = city['lng']
        country = city['country']

        seen_country = False
        for country_data in database_country['countries']:
            if country_data['name'].lower() == country.lower():
                country_id = country_data['id']
                seen_country = True

                break
        if not seen_country:
            print(f"Country {country} not found")

        cities.append({
            "id": id,
            "name": name,
            "population": population,
            "lat": lat,
            "lon": lon
        })
        relations.append({
            "source_id": id,
            "target_id": country_id,
            "type": "LOCATED_IN"
        })

    for country in raw_data_country['countries']:
        capital_name = country['capital']
        country_id = f"country:{country['name'].upper().replace(' ', '_')}"
        seen = False
        for city in cities:
            if city['name'] == capital_name:
                capital_id = city['id']
                seen = True
                break
        if not seen:
            print(f"Capital {capital_name} not found")
        relations.append({
            "source_id": capital_id,
            "target_id": country_id,
            "type": "CAPITAL_OF"
        })


    with open(CITY_DATABASE, "w") as f:
        json.dump({"cities": cities}, f, indent=4, ensure_ascii=False)
    with open("./data/database/relations/LOCATED_IN.json", "w") as f:
        json.dump({"relations": relations}, f, indent=4, ensure_ascii=False)
    with open("./data/database/relations/CAPITAL_OF.json", "w") as f:
        json.dump({"relations": relations}, f, indent=4, ensure_ascii=False)


def main():
    # standardization_countries()
    # standardization_rivers()
    standardization_cities()

    # establish_relation_borders_with()
    # establish_relation_river_tributary()


if __name__ == "__main__":
    main()