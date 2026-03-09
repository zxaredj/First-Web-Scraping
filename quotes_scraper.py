import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = "https://quotes.toscrape.com"
url = base_url

headers = {
    "User-Agent": "Mozilla/5.0"
}

data = []

while url:
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve page: {url}")
        break

    soup = BeautifulSoup(response.text, "html.parser")

    quote_blocks = soup.find_all("div", class_="quote")

    for quote in quote_blocks:
        text_tag = quote.find("span", class_="text")
        author_tag = quote.find("small", class_="author")
        tag_elements = quote.find_all("a", class_="tag")
        author_link_tag = quote.find("a")

        text = text_tag.get_text(strip=True) if text_tag else "N/A"
        author = author_tag.get_text(strip=True) if author_tag else "N/A"

        # Clean special quotation marks
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")
        text = text.strip()

        tags = [tag.get_text(strip=True) for tag in tag_elements]
        tags_joined = ", ".join(tags) if tags else "N/A"

        birth_date = "N/A"
        birth_location = "N/A"

        if author_link_tag:
            author_link = author_link_tag.get("href")
            author_url = base_url + author_link

            author_response = requests.get(author_url, headers=headers)

            if author_response.status_code == 200:
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                birth_date_tag = author_soup.find("span", class_="author-born-date")
                birth_location_tag = author_soup.find("span", class_="author-born-location")

                birth_date = birth_date_tag.get_text(strip=True) if birth_date_tag else "N/A"
                birth_location = birth_location_tag.get_text(strip=True) if birth_location_tag else "N/A"

            time.sleep(1)

        record = {
            "quote": text,
            "author": author,
            "tags": tags_joined,
            "birth_date": birth_date,
            "birth_location": birth_location
        }

        data.append(record)

    next_button = soup.find("li", class_="next")

    if next_button:
        next_page = next_button.find("a")["href"]
        url = base_url + next_page
        time.sleep(1)
    else:
        url = None

df = pd.DataFrame(data)

print(df.head())
print(df.info())

df.to_csv("scraped_quotes_dataset.csv", index=False, encoding="utf-8-sig")

print("Scraping finished. File saved as scraped_quotes_dataset.csv")