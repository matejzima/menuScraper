import re
import json
import datetime

def build_html_from_json(menu_data):
    html_parts = []
    html_parts.append("<ul>")
    for section_name, items in menu_data.items():
        html_parts.append(f"  <li><strong>{section_name}</strong>")
        html_parts.append("    <ul>")
        for item in items:
            html_parts.append(f"      <li>{item}</li>")
        html_parts.append("    </ul>")
        html_parts.append("  </li>")
    html_parts.append("</ul>")
    return "\n".join(html_parts)

def main():
    # 1) Load JSON for Na Čepu
    with open("nacepu_menu.json", "r", encoding="utf-8") as f:
        nacepu_data = json.load(f)
    nacepu_html = build_html_from_json(nacepu_data)

    # 2) Load JSON for Sia
    with open("sia_menu.json", "r", encoding="utf-8") as f:
        sia_data = json.load(f)
    sia_html = build_html_from_json(sia_data)

    # 3) Read the existing index.html
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 4) For each menu, replace everything from
    #    id="nacepu-menu"> ... </div> or id="sia-menu"> ... </div>
    #    with our new HTML
    #
    #    Explanation of the regex:
    #    (id="nacepu-menu">)  => group 1: the literal text
    #    (.*?)                => group 2: anything, non-greedy
    #    (</div>)             => group 3: the closing div
    #
    #    We replace groups 2 (the old content) with the new HTML.

    pattern_nacepu = r'(id="nacepu-menu">)(.*?)(</div>)'
    replacement_nacepu = f'\\1{nacepu_html}\\3'
    html = re.sub(pattern_nacepu, replacement_nacepu, html, flags=re.DOTALL)

    pattern_sia = r'(id="sia-menu">)(.*?)(</div>)'
    replacement_sia = f'\\1{sia_html}\\3'
    html = re.sub(pattern_sia, replacement_sia, html, flags=re.DOTALL)

    # 5) Update the "Last Updated" timestamp
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html = html.replace(
        '<span id="last-updated">--</span>',
        f'<span id="last-updated">{now_str}</span>'
    )

    # 6) Write the updated HTML back to index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("index.html updated with new menu data!")

if __name__ == "__main__":
    main()
