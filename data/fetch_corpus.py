# Project: European Knowledge Graph
# Author: Felix Do
# Data: 2025-10-12

import json
import wikipediaapi
import time

def create_text_corpus():
    try:
        with open("data/europe_data.json", "r") as file:
            europe_data = json.load(file)
    except FileNotFoundError:
        print("Error: europe_data.json not found.")
        return

    wiki = wikipediaapi.Wikipedia(language='en', user_agent='MyCoolAIResearch/1.0 (phongdntvn@gmail.com)')

    corpus = []
    entities = set()

    for country in europe_data["countries"]:
        entities.add(country["name"])
        entities.add(country['capital'])

    print(f"Found {len(entities)} entities.")

    for i, entity_name in enumerate(entities):
        if not entity_name:
            continue
        page = wiki.page(entity_name)
        if page.exists():
            summary = page.summary.split('.')
            short_summary = '.'.join(summary[:3]) + '.'

            corpus.append({
                "id": entity_name,
                "text": short_summary
            })
        else:
            print(f"Entity {entity_name} not found on Wikipedia.")

        time.sleep(1)

    output_path = "data/text_corpus.json"
    with open(output_path, "w") as file:
        json.dump(corpus, file, indent=4, ensure_ascii=False)
    
    print(f"Text corpus saved to {output_path}")


if __name__ == "__main__":
    create_text_corpus()
    
        