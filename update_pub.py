import json
from scholarly import scholarly
from tqdm import tqdm
from pathlib import Path

OUTPUT_PATH = Path("_data/publications.json")

def fetch_publications(user_id):
    author = scholarly.search_author_id(user_id)
    author = scholarly.fill(author, sections=["publications"], sortby = "year")
    
    publications = []
    for pub in tqdm(author.get("publications", []), desc="Fetching publications"):
        filled_pub = scholarly.fill(pub)
        bib = filled_pub.get("bib", {})
        year = int(bib.get("pub_year", 0))
        authors = bib.get("author", "").split(" and ")
        title = bib.get("title", "")

        publication = {
            "id": filled_pub.get("id_citations", "")[:9],  # Short unique ID
            "type": "article-journal",
            "title": title,
            "container-title": bib.get("journal", "") or bib.get("venue", ""),
            "page": bib.get("pages", ""),
            "volume": bib.get("volume", ""),
            "issue": bib.get("issue", ""),
            "source": "Google Scholar",
            "abstract": bib.get("abstract", ""),
            "DOI": "",  # Not available from Google Scholar
            "author": [
                {
                    "family": a.strip().split()[-1],
                    "given": " ".join(a.strip().split()[:-1])
                } for a in authors if a.strip()
            ],
            "link": filled_pub.get("pub_url", ""),  # Add publication link
            "issued": {
                "date-parts": [[year]]
            }
        }

        publications.append(publication)

    # Reformat publication to:
    # {'year': 2023, 'pub_list': []}
    publications_by_year = {}
    for pub in publications:
        year = pub["issued"]["date-parts"][0][0]
        if year not in publications_by_year:
            publications_by_year[year] = []
        publications_by_year[year].append(pub)
    new_publications = []
    for year, pub_list in publications_by_year.items():
        new_publications.append({
            "year": year,
            "pub_list": pub_list
        })
    # Sort by year descending
    new_publications.sort(key=lambda x: x["year"], reverse=True)

    return new_publications

def save_publications(publications, output_path=OUTPUT_PATH):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(publications, f, indent=4, ensure_ascii=False)

def main():
    user_id = "iIiVrrQAAAAJ"
    publications = fetch_publications(user_id)
    save_publications(publications)
    print(f"✅ Saved {len(publications)} publications to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
