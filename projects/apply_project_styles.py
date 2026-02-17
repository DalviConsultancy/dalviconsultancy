
import os
import re

PROJECTS_DIR = r"c:\Users\ishaa\Work\dalviconsultancy\projects"
rto_buddy_file = "rtobuddy.html"
foodlebe_file = "foodlebe.html"

# Improved Regex to be more flexible with whitespace and attributes
target_container_pattern = re.compile(
    r'<div\s+class="rounded-3xl\s+overflow-hidden\s+border\s+border-white/10\s+shadow-2xl"\s*>\s*<img\s+src="([^"]+)"\s+alt="([^"]+)"\s+class="w-full\s+h-auto"([^>]*)>\s*</div>',
    re.IGNORECASE | re.DOTALL
)

replacement_template = """<div class="relative w-full aspect-[16/10] flex items-center justify-center bg-transparent">
                <!-- Decorative Corner Squares -->
                <div class="absolute -top-3 -left-3 w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded-sm z-0"></div>
                <div class="absolute -top-3 -right-3 w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded-sm z-0"></div>
                <div class="absolute -bottom-3 -left-3 w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded-sm z-0"></div>
                <div class="absolute -bottom-3 -right-3 w-6 h-6 bg-slate-200 dark:bg-slate-700 rounded-sm z-0"></div>

                <img src="{src}" alt="{alt}"
                    class="relative z-10 object-cover w-full h-full rounded-none shadow-2xl"{extra_attrs}>
            </div>"""



def process_file(filepath, filename):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False


    # 1. Add overflow-x-hidden to body and html
    
    # HTML Tag
    if "overflow-x-hidden" not in content[:500]: # Check start of file for html tag
        html_pattern = re.compile(r'(<html[^>]*class="[^"]*)(")', re.IGNORECASE)
        if html_pattern.search(content):
            content = html_pattern.sub(r'\1 overflow-x-hidden\2', content)
            print(f"[{filename}] Added overflow-x-hidden to html class.")
            modified = True
        elif '<html' in content:
            # html tag exists but no class, inject it
            content = content.replace('<html', '<html class="overflow-x-hidden"', 1)
            print(f"[{filename}] Added class='overflow-x-hidden' to html.")
            modified = True

    # Body Tag
    if "overflow-x-hidden" not in content and "body" in content: # stricter check might be needed if html tag edit added it? 
        # Actually checking 'content' generically handles it, but let's be specific for body
        # regex for body tag specifically 
        pass 

    # Re-implement body check more carefully to ensure we don't skip if html check passed
    # Check if body specifically has the class
    body_has_class = False
    body_tag_match = re.search(r'<body[^>]*>', content)
    if body_tag_match:
        if 'overflow-x-hidden' in body_tag_match.group(0):
            body_has_class = True
    
    if not body_has_class:
        # Check if body has a class attribute
        if 'class="' in content and '<body' in content: 
             # Use regex to find body tag with class
             body_pattern = re.compile(r'(<body[^>]*class="[^"]*)(")', re.IGNORECASE)
             if body_pattern.search(content):
                content = body_pattern.sub(r'\1 overflow-x-hidden\2', content)
                print(f"[{filename}] Added overflow-x-hidden to existing body class.")
                modified = True
        elif '<body' in content:
            # Body exists but no class attribute (or valid one we found easily), inject class
            content = content.replace('<body', '<body class="overflow-x-hidden"', 1)
            print(f"[{filename}] Added class='overflow-x-hidden' to body.")
            modified = True
        else:
             print(f"[{filename}] Could not find <body> tag.")

    # 2. Apply Corner Squares (Skip RTO Buddy and Foodle Be)
    if filename != rto_buddy_file and filename != foodlebe_file:
        # Flexible pattern: Match matching any div with 'rounded-3xl' and 'overflow-hidden' 
        # that directly wraps an image
        wrapper_pattern = re.compile(
            r'(<div\s+[^>]*class="[^"]*rounded-3xl[^"]*overflow-hidden[^"]*"[^>]*>)\s*(<img[^>]+>)\s*(</div>)',
            re.IGNORECASE | re.DOTALL
        )
        
        match = wrapper_pattern.search(content)
        if match:
            whole_block = match.group(0)
            img_tag = match.group(2)
            
            # Extract src and alt from img_tag
            src_match = re.search(r'src="([^"]+)"', img_tag)
            alt_match = re.search(r'alt="([^"]+)"', img_tag)
            
            if src_match and alt_match:
                src = src_match.group(1)
                alt = alt_match.group(1)
                
                extra_attrs = ""
                if 'loading="eager"' in img_tag:
                    extra_attrs += ' loading="eager"'
                if 'width=' in img_tag:
                     w_match = re.search(r'width="([^"]+)"', img_tag)
                     if w_match: extra_attrs += f' width="{w_match.group(1)}"'
                if 'height=' in img_tag:
                     h_match = re.search(r'height="([^"]+)"', img_tag)
                     if h_match: extra_attrs += f' height="{h_match.group(1)}"'

                new_html = replacement_template.format(src=src, alt=alt, extra_attrs=extra_attrs)
                content = wrapper_pattern.sub(new_html, content)
                print(f"[{filename}] Applied Corner Squares design.")
                modified = True
            else:
                 print(f"[{filename}] Image tag found but missing src or alt. Skipping.")
        else:
            print(f"[{filename}] Specific image container pattern not found. Skipping design update.")
    else:
        print(f"[{filename}] Skipping design update (Excluded file).")

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[{filename}] Saved changes.")
    else:
        print(f"[{filename}] No changes made.")

def main():
    if not os.path.exists(PROJECTS_DIR):
        print(f"Directory not found: {PROJECTS_DIR}")
        return

    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".html"):
            process_file(os.path.join(PROJECTS_DIR, filename), filename)

if __name__ == "__main__":
    main()
