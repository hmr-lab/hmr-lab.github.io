import json
from scholarly import scholarly
from tqdm import tqdm
from pathlib import Path

OUTPUT_PATH = Path("_data/publications.json")

def fetch_publications(user_id):
    author = scholarly.search_author_id(user_id)
    author = scholarly.fill(author, sections=["publications"])
    
    publications = []
    for pub in tqdm(author.get("publications", []), desc="Fetching publications"):
        filled_pub = scholarly.fill(pub)
        bib = filled_pub.get("bib", {})
        year = int(bib.get("pub_year", 0))
        month = None  # Not available from Google Scholar
        authors = bib.get("author", "").split(" and ")
        title = bib.get("title", "")
        
        publication = {
            "id": filled_pub.get("id_citations", "")[:9],  # Short unique ID
            "type": "article-journal",
            "title": title,
            "container-title": bib.get("venue", ""),
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
                "date-parts": [[year] if not month else [year, month]]
            }
        }

        publications.append(publication)

    # Sort publications by recency (newest first)
    publications.sort(key=lambda p: p["issued"]["date-parts"][0], reverse=True)
    return publications

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
