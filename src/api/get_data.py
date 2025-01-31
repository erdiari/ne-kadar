from typing_extensions import Tuple
import requests
import json
import random
from pydantic import BaseModel

class ProductData(BaseModel):
    title: str
    img_url: str
    min_price: float
    max_price: float

def make_cimri_request(page: int = 10, keyword: str = "*", sort: str = "rank,desc"):
    url = "https://www.cimri.com/api/cimri"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.6",
        "cimri-platform-name": "CIMRI_DESKTOP_V2",
        "content-type": "application/json",
        "origin": "https://www.cimri.com",
        "priority": "u=1, i",
        "referer": f"https://www.cimri.com/arama?q={keyword}&page={max(0, page-1)}",
        "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    payload = {
        "queryName": "infiniteScrollSearchQuery",
        "variables": {
            "filters": "",
            "criterias": "",
            "categoryId": None,
            "keyword": keyword,
            "page": page,
            "sort": sort,
        },
        "platform": "CIMRI_DESKTOP_V2",
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def _get_data(*args, **kwargs) -> dict | None:
    page = random.randint(0, 100)
    result: dict | None = make_cimri_request(*args, **kwargs, page=page)

    if result:
        try:
            products = result.get("data").get("search").get("products")
            return random.sample(products, k=1)[0]
        except AttributeError as e:
            print(e)


def get_data(*args, **kwargs) -> dict | None:
    prod = _get_data()
    img_url, prod_title, offers = None, None, None
    if prod:
        prod_title = prod.get("title")
        prod_img_id = prod.get("imageId")
        offers = [offer["price"] for offer in prod["topOffers"]]
        if prod_title and prod_img_id:
            img_url = get_image(prod_title, prod_img_id)
    if img_url and prod_title and offers:
        return ProductData(title=prod_title, img_url=img_url, min_price=min(offers), max_price=max(offers) )


def get_image(title: str, image_id: int):
    def _to_url_title(text):
        text = text.lower()
        turkish_map = {
            "ı": "i",
            "ğ": "g",
            "ü": "u",
            "ş": "s",
            "ö": "o",
            "ç": "c",
            "â": "a",
            "î": "i",
            "û": "u",
            " ": "-",
        }
        for turkish_char, ascii_char in turkish_map.items():
            text = text.replace(turkish_char, ascii_char)
        return text

    url_title = _to_url_title(title)
    url = f"https://cdn.cimri.io/image/560x560/{url_title}_{image_id}.jpg"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open("current_product.jpg", "wb") as file:
            file.write(response.content)

        return url
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False


if __name__ == "__main__":
    prod = _get_data()
    with open("current_product.json", "w") as f:
        json.dump(prod, f, indent=2, ensure_ascii=False)

    img_url = None

    if prod:
        prod_title = prod.get("title")
        prod_img_id = prod.get("imageId")
        if prod_title and prod_img_id:
            img_url = get_image(prod_title, prod_img_id)
            if not img_url:
                print(f"Could not download: {prod_title=} {prod_img_id}")

    if prod:
        offers = [offer["price"] for offer in prod["topOffers"]]
        with open("current_values.json", "w") as f:
            json.dump(
                {"minPrice": min(offers), "maxPrice": max(offers), "img": img_url},
                f,
                indent=2,
                ensure_ascii=False,
            )

    print(json.dumps(prod, indent=2))
