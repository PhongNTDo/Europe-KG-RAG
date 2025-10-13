# Project: European Knowledge Graph
# Author: Felix Do
# Data: 2025-10-12

import requests
import json
from collections import defaultdict


def fetch_europe_data_from_wikipedia():
    url = "https://query.wikidata.org/sparql"

    query = """
    SELECT ?country ?countryLabel ?capitalLabel ?borderLabel
    WHERE {
      ?country wdt:P31 wd:Q6256.        # Country
      ?country wdt:P30 wd:Q46.          # In Europe
      OPTIONAL { ?country wdt:P36 ?capital. }
      OPTIONAL {
        ?country wdt:P47 ?border.
        ?border wdt:P31 wd:Q6256.      
      }

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    ORDER BY ?countryLabel
    """

    headers = {
        "User-Agent": "MyCoolGeoAIResearch/1.0 (thuanphong180100@gmail.com)",
        "Accept": "application/sparql-results+json"
    }

    try:
        response = requests.get(url, params={'query': query, 'format': 'json'}, headers=headers)
        response.raise_for_status()
        data = response.json()["results"]["bindings"]
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Wikidata: {e}")
        return None


def process_wikipedia_data(data):
    countries = []
    country_set = {result['countryLabel']['value'] for result in data}
    print("Number of countries:", len(country_set))
    print("Countries:", country_set)

    country_info = defaultdict(lambda: {"capital": None, "borders": set()})

    for entry in data:
        name = entry["countryLabel"]["value"]
        capital = entry.get("capitalLabel", {}).get("value")
        border = entry.get("borderLabel", {}).get("value")

        if capital:
            country_info[name]["capital"] = capital
        if border:
            country_info[name]["borders"].add(border)

    for country, info in country_info.items():
        countries.append({
            "name": country,
            "eu_member": None,
            "capital": info["capital"],
            "borders_with": list(sorted(info["borders"]))
        })

    formatted_data = {
        "countries": countries,
        "rivers": [],
        "landmarks": []
    }

    return formatted_data


if __name__ == "__main__":
    wikipedia_data = fetch_europe_data_from_wikipedia()
    if wikipedia_data:
        formatted_data = process_wikipedia_data(wikipedia_data)

        output_path = "data/europe_data.json"
        with open(output_path, "w") as file:
            json.dump(formatted_data, file, indent=4, ensure_ascii=False)
        print(f"Data saved to {output_path}")





        

