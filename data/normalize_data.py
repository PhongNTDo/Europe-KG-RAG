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


def main():
    with open(COUNTRIES_RAW_DATA_PATH) as f:
        data = json.load(f)

    countries = []
    for country in data['countries']:
        name = country['name']
        id = f"country:{name.upper()}"

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
    with open("data/database/europe_countries.json", "w") as f:
        json.dump({"countries": countries}, f, indent=4, ensure_ascii=False)




if __name__ == "__main__":
    main()