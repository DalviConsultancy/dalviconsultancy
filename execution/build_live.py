import os
import shutil
import re
import sys
import subprocess
import glob

# Try to import Pillow for image processing, install if necessary
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    try:
        install_package("Pillow")
        from PIL import Image
    except Exception as e:
        print(f"Failed to install Pillow: {e}. Image optimization will be skipped.")
        Image = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    try:
        install_package("beautifulsoup4")
        from bs4 import BeautifulSoup
    except Exception as e:
        print(f"Failed to install beautifulsoup4: {e}. HTML image updating will be skipped.")
        BeautifulSoup = None

# Regex-based minifiers to avoid external dependencies
def minify_css(content):
    # Remove comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Remove whitespace around separators
    content = re.sub(r'\s*([:;{}])\s*', r'\1', content)
    # Remove newlines and extra spaces
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def minify_js(content):
    # Simple regex minifier (use with caution, assumes well-formed JS)
    # Remove single line comments (careful with URLs)
    content = re.sub(r'//.*', '', content)
    # Remove multi-line comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Remove whitespace (very basic)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def minify_html(content):
    # Remove comments
    content = re.sub(r'<!--(?!\[if).*?-->', '', content, flags=re.DOTALL)
    # Collapse whitespace between tags
    content = re.sub(r'>\s+<', '><', content)
    return content.strip()

SOURCE_DIR = os.getcwd()
LIVE_DIR = os.path.join(SOURCE_DIR, 'live')
ASSETS_DIR = 'assets'
EXCLUDE_DIRS = {'.git', 'execution', 'node_modules', 'live', '.tmp', '.gemini', '__pycache__', '.vscode', '.idea'}
EXCLUDE_FILES = {'.gitignore', 'package-lock.json', 'README.md', 'requirements.txt', '.DS_Store', 'copy_file.py', 'build_live.py'} 

def clean_live_dir():
    if os.path.exists(LIVE_DIR):
        try:
            shutil.rmtree(LIVE_DIR)
        except Exception as e:
            print(f"Warning cleaning live dir: {e}")
    if not os.path.exists(LIVE_DIR):
        os.makedirs(LIVE_DIR)

def copy_files():
    print("Copying files...")
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        rel_path = os.path.relpath(root, SOURCE_DIR)
        
        if rel_path.startswith('live'):
            continue

        dest_root = os.path.join(LIVE_DIR, rel_path)
        if not os.path.exists(dest_root):
            os.makedirs(dest_root)
            
        for file in files:
            if file in EXCLUDE_FILES or file.endswith('.py') or file.endswith('.scss'):
                continue
            
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            try:
                shutil.copy2(src_file, dest_file)
            except Exception as e:
                print(f"Error copying {file}: {e}")
    print("Files copied.")

def optimize_images(root_dir):
    if not Image:
        print("Pillow not available, skipping image optimization.")
        return

    print("Optimizing images...")
    MAX_WIDTH = 800
    
    # Walk through all directories in live to find images
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            filename, ext = os.path.splitext(file)
            ext = ext.lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                # We process all images to ensure they are resized, even if they are already webp
                try:
                    with Image.open(file_path) as img:
                        # Resize if too large
                        if img.width > MAX_WIDTH:
                            print(f"Resizing {file} from {img.width}px to {MAX_WIDTH}px...")
                            img.thumbnail((MAX_WIDTH, MAX_WIDTH))
                            img.save(file_path, quality=85) # Save back to original path first if we just resized it
                        
                        # Generate WebP if original was not webp
                        if ext != '.webp':
                            webp_path = os.path.join(root, filename + '.webp')
                            if not os.path.exists(webp_path):
                                img.save(webp_path, 'WEBP', quality=85)
                                print(f"Generated WebP: {webp_path}")

                        # Generate Fallback PNG if original was webp and checks needed
                        if ext == '.webp':
                            fallback_exists = False
                            for fallback_ext in ['.png', '.jpg', '.jpeg']:
                                if os.path.exists(os.path.join(root, filename + fallback_ext)):
                                    fallback_exists = True
                                    break
                            
                            if not fallback_exists:
                                png_path = os.path.join(root, filename + '.png')
                                if not os.path.exists(png_path):
                                    img.save(png_path, 'PNG')
                                    print(f"Generated Fallback PNG: {png_path}")

                except Exception as e:
                    print(f"Failed to process {file}: {e}")

def update_html_with_picture_tags(file_path):
    if not BeautifulSoup:
        return

    print(f"Updating HTML images in: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        images = soup.find_all('img')
        modified = False
        
        for img in images:
            src = img.get('src')
            if not src or src.startswith('http') or src.startswith('data:'):
                continue
            
            if img.parent.name == 'picture':
                continue

            if '/' in src:
                path_parts = src.split('/')
                filename = path_parts[-1]
                path_dir = '/'.join(path_parts[:-1])
            else:
                filename = src
                path_dir = ''

            name_only, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            sources = []
            fallback_src = src
            html_dir = os.path.dirname(file_path)
            
            # Helper to check existence in live dir structure
            # Since we are modifying files IN live dir, we check relative to file_path
            
            # Check WebP existence
            webp_rel = os.path.join(path_dir, name_only + '.webp').replace('\\', '/')
            webp_abs = os.path.join(html_dir, path_dir, name_only + '.webp')
            
            if ext == '.webp':
                # Already WebP, look for fallback
                png_rel = os.path.join(path_dir, name_only + '.png').replace('\\', '/')
                png_abs = os.path.join(html_dir, path_dir, name_only + '.png')
                
                jpg_rel = os.path.join(path_dir, name_only + '.jpg').replace('\\', '/')
                jpg_abs = os.path.join(html_dir, path_dir, name_only + '.jpg')

                if os.path.exists(png_abs):
                    fallback_src = png_rel
                elif os.path.exists(jpg_abs):
                    fallback_src = jpg_rel
                
                sources.append({'srcset': src, 'type': 'image/webp'})

            elif ext in ['.png', '.jpg', '.jpeg']:
                if os.path.exists(webp_abs):
                    sources.append({'srcset': webp_rel, 'type': 'image/webp'})
                fallback_src = src

            if sources:
                picture = soup.new_tag('picture')
                for s in sources:
                    source_tag = soup.new_tag('source', srcset=s['srcset'], type=s['type'])
                    picture.append(source_tag)
                
                img_tag = soup.new_tag('img', **img.attrs)
                img_tag['src'] = fallback_src
                picture.append(img_tag)
                img.replace_with(picture)
                modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
                
    except Exception as e:
        print(f"Error processing HTML {file_path}: {e}")


import hashlib

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()[:8]

def version_assets(root_dir):
    print("Versioning assets...")
    renames = {} 
    target_files = ['styles.css', 'scripts.js']
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file in target_files:
                file_path = os.path.join(root, file)
                # Calculate relative path from root_dir to key it correctly for replacement if needed, 
                # but simple filename replacement is safer for now if unique.
                
                try:
                    file_hash = calculate_md5(file_path)
                    filename, ext = os.path.splitext(file)
                    new_filename = f"{filename}.{file_hash}{ext}"
                    new_file_path = os.path.join(root, new_filename)
                    
                    os.rename(file_path, new_file_path)
                    print(f"Versioned {file} -> {new_filename}")
                    
                    renames[file] = new_filename
                except Exception as e:
                    print(f"Error versioning {file}: {e}")

    if renames:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for original, new in renames.items():
                            content = content.replace(f'"{original}"', f'"{new}"')
                            content = content.replace(f"'{original}'", f"'{new}'")
                            
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"Error updating HTML {file}: {e}")

def minify_files(root_dir):
    print("Minifying files...")
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            try:
                if ext == '.html':
                    update_html_with_picture_tags(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    minified = minify_html(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(minified)
                        
                elif ext == '.css':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    minified = minify_css(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(minified)
                        
                elif ext == '.js':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    minified = minify_js(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(minified)
                        
            except Exception as e:
                print(f"Error minimizing {file}: {e}")

def inline_css(root_dir):
    print("Inlining CSS...")
    # Find styles.css
    css_file = os.path.join(root_dir, 'styles.css')
    
    if not os.path.exists(css_file):
        print("styles.css not found for inlining.")
        return

    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        css_content = minify_css(css_content)

        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.html'):
                    html_path = os.path.join(root, file)
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Regex to match <link ... href="styles.css" ...> allow any attributes and whitespace
                    # Matches: <link rel="stylesheet" href="styles.css">
                    # Matches: <link href="styles.css" rel="stylesheet" />
                    pattern = re.compile(r'<link[^>]*href=["\']styles\.css["\'][^>]*>', re.IGNORECASE)
                    match = pattern.search(html_content)
                    if match:
                        print(f"FOUND MATCH in {file}")
                        print(f"Match: {match.group(0)}")
                        new_style_tag = f'<style>{css_content}</style>'
                        # Use string replace for safety against regex group formatting in css_content
                        html_content = html_content.replace(match.group(0), new_style_tag)
                        
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
        
        # Remove the CSS file
        try:
             os.remove(css_file)
             print(f"Removed inlined file: {css_file}")
        except Exception as e:
             print(f"Could not remove css file: {e}")
                            
    except Exception as e:
        print(f"Error inlining CSS: {e}")

def main():
    print("Starting build process for 'live' folder...")

    # Run Tailwind Build
    print("Running Tailwind CSS build...")
    try:
        # Use npx with shell=True to ensure it works on Windows
        subprocess.run(["npx", "tailwindcss", "-i", "input.css", "-o", "styles.css", "--minify"], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Tailwind build failed: {e}")
        sys.exit(1)

    clean_live_dir()
    copy_files()
    optimize_images(LIVE_DIR)
    
    # Inline CSS BEFORE versioning, so we find styles.css easily
    inline_css(LIVE_DIR)
    
    version_assets(LIVE_DIR)

    minify_files(LIVE_DIR)

    print("Build complete. 'live' folder is ready.")

if __name__ == "__main__":
    main()
