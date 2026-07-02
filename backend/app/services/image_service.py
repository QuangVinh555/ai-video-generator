import requests

def search_images_service(query: str, limit: int):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": limit,
        "pithumbsize": 1200
    }
    headers = {"User-Agent": "AIVideoGenMVP/1.0"}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    images = []
    if "query" in data and "pages" in data["query"]:
        for page_id, page_info in data["query"]["pages"].items():
            if "thumbnail" in page_info:
                images.append(page_info["thumbnail"]["source"])
    return images
