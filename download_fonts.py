import os
import urllib.request
import re

# Font URLs from index.html
FONT_URLS = [
    "https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap",
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap"
]

ASSETS_FONTS_DIR = os.path.join("assets", "fonts")
if not os.path.exists(ASSETS_FONTS_DIR):
    os.makedirs(ASSETS_FONTS_DIR)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_filename(url):
    name = url.split('/')[-1]
    name = name.split('?')[0]
    return name

combined_css = "/* Local Google Fonts */\n"

for url in FONT_URLS:
    print(f"Processing {url}...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            css = response.read().decode('utf-8')
        
        # Find all url(...) patterns
        matches = re.finditer(r'url\((https://[^)]+)\)', css)
        
        for match in matches:
            remote_url = match.group(1)
            filename = clean_filename(remote_url)
            local_path = os.path.join(ASSETS_FONTS_DIR, filename)
            
            # Download file if not exists
            if not os.path.exists(local_path):
                print(f"Downloading {filename}...")
                try:
                    font_req = urllib.request.Request(remote_url, headers=HEADERS)
                    with urllib.request.urlopen(font_req) as font_resp:
                        with open(local_path, 'wb') as f:
                            f.write(font_resp.read())
                except Exception as e:
                    print(f"Failed to download {filename}: {e}")
            
            # Replace URL in CSS.
            # We are generating fonts.css in root, and fonts are in assets/fonts.
            css = css.replace(remote_url, f'assets/fonts/{filename}')
            
        combined_css += css + "\n"
        
    except Exception as e:
        print(f"Error processing {url}: {e}")

with open("fonts.css", "w", encoding="utf-8") as f:
    f.write(combined_css)

print("Fonts downloaded and fonts.css created.")
print("Now add '@import \"fonts.css\";' to the top of input.css")
