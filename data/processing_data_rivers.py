import json


def load_dict_country():
    with open("data/crawled_data/mapping_country_name.txt") as f:
        dict_country = {}
        for line in f.readlines():
            line = line.strip()
            if line:
                dict_country[line.split(" ", 1)[0]] = line.split(" ", 1)[1]
    return dict_country


def process_country_name(data):
    dict_country = load_dict_country()
    non_exist_country = []

    for river in data['rivers']:
        for country in river['countries'].split():
            if country not in dict_country and country not in non_exist_country:
                non_exist_country.append(country)
    if not non_exist_country:
        print("All countries of rivers database are available.")

    with open("data/database/updated_europe_data.json") as f:
        europe_data = json.load(f)
    list_countries = list(dict_country.values())
    for country in europe_data['countries']:
        if country['name'] not in list_countries and country['name'] not in non_exist_country:
            non_exist_country.append(country['name'])
    if not non_exist_country:
        print("All countries of europe database are available.")
    print("\n".join(non_exist_country))

    for i, river in enumerate(data['rivers']):
        countries = []
        for country in river['countries'].split():
            countries.append(dict_country[country])
        data['rivers'][i]['countries'] = countries

    return data


def main():
    with open("data/crawled_data/rivers/list_of_rivers_of_europe.json", "r") as file:
        data = json.load(file)

    processed_data = process_country_name(data)
    with open("data/database/europe_rivers.json", "w") as file:
        json.dump(processed_data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
