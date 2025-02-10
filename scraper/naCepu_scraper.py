import requests
from bs4 import BeautifulSoup
import json
import re

def clean_text(text):
    """
    1) Remove portion sizes like '130g', '0,3l'.
    2) Remove bracketed info like '(1,3,9)'.
    3) Remove prices like '55,-' or '199 ,-',
       even if it appears at end of line or followed by punctuation.
    4) Collapse spaces.
    5) Capitalize first letter.
    """

    # 1) Remove portion patterns: '130g', '0,3l', etc.
    text = re.sub(r"\b\d+([.,]\d+)?\s*[gGlL]\b", "", text)

    # 2) Remove bracketed info: '(1,3,9)', etc.
    text = re.sub(r"\([^)]*\)", "", text)

    # 3) Remove prices.
    #    Pattern explanation:
    #      - \b\d+([.,]\d+)? => integer or float (with . or ,)
    #      - \s*,?\s*-\s*    => optional comma, dash, optional whitespace
    #      - (?=$|\W)        => lookahead ensures we're at end-of-string or a non-word char
    #
    #    This handles '55,-' at line end and variations like '55 ,-', '129.90,-'.
    price_pattern = r"\b\d+([.,]\d+)?\s*,?\s*-\s*(?=$|\W)"
    text = re.sub(price_pattern, "", text)

    # 4) Collapse multiple spaces, trim
    text = re.sub(r"\s+", " ", text).strip()

    # 5) Capitalize first letter (if not empty)
    if text:
        text = text[0].upper() + text[1:]

    return text

def scrape_nacepu_menu():
    url = "https://nacepu.com/poledni-menu/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", id="post-22")
    if not content_div:
        print("Could not find the div with id='post-22'. The page structure may have changed.")
        return {}

    p_tags = content_div.find_all("p")

    recognized_headings = {
        "POLÉVKY": "Polévky",
        "HLAVNÍ JÍDLA": "Hlavní jídla",
        "MENU": "Menu"
    }

    menu_data = {
        "Polévky": [],
        "Hlavní jídla": [],
        "Menu": []
    }

    current_section = None

    for p in p_tags:
        text_raw = p.get_text(strip=True)
        text_upper = text_raw.upper()

        # Stop collecting if we see "NÁPOJE K OBĚDU"
        if "NÁPOJE K OBĚDU" in text_upper:
            break

        # If this p-tag is a recognized heading, switch section
        if text_upper in recognized_headings:
            current_section = recognized_headings[text_upper]
            continue

        # Otherwise, if we're in a heading section, clean & add
        if current_section is not None:
            cleaned = clean_text(text_raw)
            if cleaned:
                menu_data[current_section].append(cleaned)

    return menu_data

def main():
    scraped_menu = scrape_nacepu_menu()
    with open("nacepu_menu.json", "w", encoding="utf-8") as f:
        json.dump(scraped_menu, f, ensure_ascii=False, indent=2)
    print("Scraped menu data saved to nacepu_menu.json")

if __name__ == "__main__":
    main()
