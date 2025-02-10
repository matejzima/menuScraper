import requests
import re
import html as html_lib
from bs4 import BeautifulSoup
import json

def scrape_sia_from_js():
    js_url = "https://www.menubot.cz/app/users/sia484626412569856654/export/dailymenu_a.js"

    #### OPTION A: Try setting response.encoding before reading .text ####
    # This works if the server is sending correct bytes, but the headers
    # or auto-detection are incorrect. If 'windows-1250' doesn't work,
    # try other encodings, e.g. 'cp1250' or 'iso-8859-2'.
    response = requests.get(js_url)
    response.raise_for_status()
    response.encoding = "utf-8"  
    js_text = response.text  # Now this uses the forced encoding

    #### OPTION B: Manually decode from response.content ####
    # If Option A doesn't fix it, comment that out and try this approach:
    # raw_bytes = response.content
    # js_text = raw_bytes.decode('windows-1250', errors='replace')

    # 2) Extract the HTML portion between document.write(' ... ');
    match = re.search(r"document\.write\(\s*'(.*?)'\s*\);", js_text, re.DOTALL)
    if not match:
        print("Couldn't find document.write(...) in the JS file. The format may have changed.")
        return {}

    raw_html = match.group(1)

    # 3) Unescape HTML entities (like &nbsp;, etc.)
    unescaped_html = html_lib.unescape(raw_html)

    # If you still see garbled Czech characters, try re-encoding + decoding:
    #   unescaped_html = (
    #       unescaped_html
    #       .encode('latin-1', errors='replace')
    #       .decode('utf-8', errors='replace')
    #   )
    # or you can try other combos, e.g. .encode('cp1250').decode('utf-8'), etc.

    # 4) Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(unescaped_html, "html.parser")

    # 5) Find the dm-cat blocks and build JSON
    dm_cats = soup.find_all("div", class_="dm-cat")
    menu_data = {}

    for dm_cat in dm_cats:
        title_div = dm_cat.find("div", class_="dm-cat-title")
        h2_tag = title_div.find("h2") if title_div else None
        if not h2_tag:
            continue

        section_title = h2_tag.get_text(strip=True)
        if section_title not in menu_data:
            menu_data[section_title] = []

        dm_items = dm_cat.find_all("div", class_="dm-item")
        for item in dm_items:
            content_div = item.find("div", class_="dm-content")
            if not content_div:
                continue

            h3_tag = content_div.find("h3")
            p_tag = content_div.find("p")

            dish_name = h3_tag.get_text(strip=True) if h3_tag else ""
            description = p_tag.get_text(strip=True) if p_tag and p_tag.get_text(strip=True) else ""

            if description:
                combined_text = f"{dish_name}: {description}"
            else:
                combined_text = dish_name

            if combined_text:
                menu_data[section_title].append(combined_text)

    return menu_data

def main():
    sia_menu = scrape_sia_from_js()
    with open("sia_menu.json", "w", encoding="utf-8") as f:
        json.dump(sia_menu, f, ensure_ascii=False, indent=2)
    print("Scraped Sia menu saved to sia_menu.json")

if __name__ == "__main__":
    main()
