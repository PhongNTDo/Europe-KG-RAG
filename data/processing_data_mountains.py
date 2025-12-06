import json
from collections import defaultdict
from pathlib import Path
import argparse


with open("data/database/entities/europe_countries.json") as f:
    data_countries = json.load(f)
list_countries = [country['name'].lower() for country in data_countries['countries']]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="create database for mountains."
    )
    parser.add_argument(
        "--input-json",
        help="path to json file",
    )
    parser.add_argument(
        "--output",
        default=Path("data/database/entities/europe_mountains.json"),
        help="path to output json file"
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    with open(args.input_json) as f:
        data = json.load(f)
    mountains = []
    located_in_relations = []
    for mountain in data['mountains']:
        name = mountain['Peak']
        if "/" in name:
            name = name.split("/")[0].strip()
        id = f"mountain:{name.upper().replace(' ', '_')}"
        
        elavation = mountain['Elevation (m)']
        countries = [c.lower().strip() for c in mountain['Country'].split("/")]
        prominence = mountain['Prominence (m)']
        for country in countries:
            if country not in list_countries:
                print(country)
        
        mountains.append({
            "id": id,
            "name": name,
            "elavation": elavation,
            "prominence": prominence
        })
        for country in countries:
            for country_data in data_countries['countries']:
                if country_data['name'].lower() == country:
                    id_mountain = id
                    id_country = country_data['id']
                    located_in_relations.append({
                        "source_id": id_mountain,
                        "target_id": id_country,
                        "type": "LOCATED_IN"
                    })
                    break
    with open(args.output, "w") as f:
        json.dump({"mountains": mountains}, f, indent=4, ensure_ascii=False)
    with open("./data/database/relations/LOCATED_IN_1.json", "w") as f:
        json.dump({"relations": located_in_relations}, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    main()