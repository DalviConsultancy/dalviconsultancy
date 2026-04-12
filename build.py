import os
import shutil
import re
import sys
import subprocess
import hashlib
from datetime import datetime

# Try to import Pillow for image processing
try:
    from PIL import Image
except ImportError:
    Image = None

# Try to import BeautifulSoup for HTML processing
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Configuration
SOURCE_DIR = '.'
DEST_DIR = 'live'
BASE_URL = 'https://consult.dalvigroup.co.in'

# Build system exclusions
EXCLUDE_DIRS = {
    '.git', 'dist', 'node_modules', '.tmp', '.gemini', '__pycache__', 
    '.vscode', '.idea', 'live', 'skill-assets'
}

# Source files to exclude from the production build
EXCLUDE_FILES = {
    '.gitignore', 'package-lock.json', 'README.md', 'requirements.txt', 
    '.DS_Store', 'build.py', 'build_archive.py', 'package.json', 
    'tailwind.config.js', 'task.md', 'AGENTS.md', 'SKILL.md', 
    'DEPLOYMENT.md', 'analyze_report.py', 'apply_mobile_nav.py', 
    'apply_mobile_nav_v2.py', 'apply_project_styles.py', 'check_score.py',
    'download_fonts.py', 'fix_hover_scale.py', 'update_corners.py'
}

def minify_css(content):
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    content = re.sub(r'\s*([:;{}])\s*', r'\1', content)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def minify_js(content):
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def minify_html(content):
    content = re.sub(r'<!--(?!\[if).*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'>\s+<', '><', content)
    return content.strip()

def clean_dest():
    if os.path.exists(DEST_DIR):
        print(f"Cleaning {DEST_DIR}...")
        try:
            shutil.rmtree(DEST_DIR)
        except Exception as e:
            print(f"Warning: Could not fully clean {DEST_DIR}: {e}")
    os.makedirs(DEST_DIR, exist_ok=True)

def copy_files():
    print("Copying files...")
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        rel_path = os.path.relpath(root, SOURCE_DIR)
        if rel_path == '.':
            rel_path = ''
            
        dest_root = os.path.join(DEST_DIR, rel_path)
        if not os.path.exists(dest_root):
            os.makedirs(dest_root)
            
        for file in files:
            # Filter files
            if file in EXCLUDE_FILES or file.endswith('.py'):
                continue
            
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            try:
                shutil.copy2(src_file, dest_file)
            except Exception as e:
                print(f"Error copying {file}: {e}")

def optimize_images():
    if not Image:
        print("Pillow not available, skipping image optimization.")
        return

    print("Optimizing images...")
    MAX_WIDTH = 1200
    
    for root, _, files in os.walk(DEST_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            filename, ext = os.path.splitext(file)
            ext = ext.lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    with Image.open(file_path) as img:
                        if img.width > MAX_WIDTH:
                            img.thumbnail((MAX_WIDTH, MAX_WIDTH))
                            img.save(file_path, quality=85)
                except Exception as e:
                    print(f"Failed to process {file}: {e}")

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()[:8]

def version_assets():
    print("Versioning assets...")
    renames = {} 
    target_files = ['styles.css', 'scripts.js']
    
    for root, _, files in os.walk(DEST_DIR):
        for file in files:
            if file in target_files:
                file_path = os.path.join(root, file)
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
        for root, _, files in os.walk(DEST_DIR):
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

def process_minification():
    print("Minifying files in dist...")
    for root, _, files in os.walk(DEST_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            try:
                if ext == '.html':
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
                print(f"Error minifying {file}: {e}")

def generate_sitemap():
    """Generates sitemap.xml in the destination directory."""
    print("Generating sitemap.xml...")
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Collect all HTML files
    html_files = []
    for root, _, files in os.walk(DEST_DIR):
        for file in files:
            if file.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, file), DEST_DIR)
                html_files.append(rel_path)
    
    for relative_path in html_files:
        url_path = relative_path.replace(os.path.sep, '/')
        if url_path == 'index.html':
            url_path = ''
        elif url_path.endswith('index.html'):
            url_path = url_path.replace('index.html', '')
        
        url = f"{BASE_URL}/{url_path}"
        sitemap_content.append(f'  <url><loc>{url}</loc><lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod></url>')
    
    sitemap_content.append('</urlset>')
    
    with open(os.path.join(DEST_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))

def main():
    print(f"Starting build process: {SOURCE_DIR} -> {DEST_DIR}")
    
    # 1. Run Tailwind
    print("Running Tailwind CSS build...")
    try:
        npx_cmd = "npx.cmd" if os.name == 'nt' else "npx"
        subprocess.run(
            [npx_cmd, "tailwindcss", "-i", "input.css", "-o", "styles.css", "--minify"], 
            check=True, shell=True
        )
    except Exception as e:
        print(f"Tailwind build failed: {e}")
    
    # 2. Prepare Dest
    clean_dest()
    
    # 3. Copy Files
    copy_files()
    
    # 4. Cleanup/Optimize
    optimize_images()
    version_assets()
    process_minification()
    generate_sitemap()
    
    print("Build complete.")

if __name__ == "__main__":
    main()
