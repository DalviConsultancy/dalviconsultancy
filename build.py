import os
import shutil
import re
import sys
from datetime import datetime

# Configuration
SOURCE_DIR = '.'
DEST_DIR = 'live'
BASE_URL = 'https://consultancy.dalvigroup.co.in'

# Extensions to minify
HTML_EXT = {'.html', '.htm'}
CSS_EXT = {'.css'}
JS_EXT = {'.js'}

# Directories to exclude
EXCLUDE_DIRS = {
    'live', '.git', '.vscode', '__pycache__', 'venv', 'env', '.idea', 'node_modules', '.gemini'
}

# Files to exclude from processing (but maybe not copying if handled by else)
EXCLUDE_FILES = {
    'build.py', 'deploy.py', 'minify_assets.py', 'package.json', 'package-lock.json', '.gitignore'
}

def clean_dest():
    """Removes the destination directory if it exists and recreates it."""
    if os.path.exists(DEST_DIR):
        print(f"Cleaning {DEST_DIR}...")
        try:
            shutil.rmtree(DEST_DIR)
        except Exception as e:
            print(f"Warning: Could not fully clean {DEST_DIR}: {e}")
    os.makedirs(DEST_DIR, exist_ok=True)

def generate_sitemap(files):
    """Generates sitemap.xml in the destination directory."""
    print("Generating sitemap.xml...")
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for relative_path in files:
        # Convert file path to URL
        url_path = relative_path.replace(os.path.sep, '/')
        if url_path.endswith('index.html'):
            url_path = url_path.replace('index.html', '')
        
        url = f"{BASE_URL}/{url_path}"
        
        # Get last modified time
        try:
            mtime = os.path.getmtime(relative_path)
            lastmod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except:
            lastmod = datetime.now().strftime('%Y-%m-%d')
            
        sitemap_content.append(f'  <url>')
        sitemap_content.append(f'    <loc>{url}</loc>')
        sitemap_content.append(f'    <lastmod>{lastmod}</lastmod>')
        sitemap_content.append(f'    <changefreq>weekly</changefreq>')
        sitemap_content.append(f'    <priority>{1.0 if url_path == "" else 0.8}</priority>')
        sitemap_content.append(f'  </url>')
        
    sitemap_content.append('</urlset>')
    
    with open(os.path.join(DEST_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))

def generate_robots():
    """Generates robots.txt in the destination directory."""
    print("Generating robots.txt...")
    robots_content = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {BASE_URL}/sitemap.xml"
    ]
    with open(os.path.join(DEST_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(robots_content))

def minify_html(content):
    """Minifies HTML content."""
    # Remove HTML comments <!-- ... -->
    content = re.sub(r'<!--(.*?)-->', '', content, flags=re.DOTALL)
    
    # Collapse whitespace between tags: >   <  becomes ><
    content = re.sub(r'>\s+<', '><', content)
    
    # Conservative whitespace reduction:
    # We CANNOT blindly replace all \s+ with ' ' because that merges lines
    # and breaks inline JS with // comments or missing semicolons.
    # Instead, we will strip leading/trailing whitespace from each line
    # and remove empty lines. We keep \n to be safe for inline JS.
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
            
    return '\n'.join(cleaned_lines)

def minify_css(content):
    """Minifies CSS content."""
    # Remove comments /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove whitespace around delimiters { } ; : ,
    content = re.sub(r'\s*([\{\};:,])\s*', r'\1', content)
    
    # Collapse multiple spaces to one
    content = re.sub(r'\s+', ' ', content)
    
    # Remove last semicolon in block (optional optimization)
    content = re.sub(r';\}', '}', content)
    
    return content.strip()

def minify_js(content):
    """
    Minifies JS content.
    SAFE MODE:
    1. Remove single-line comments // (only if they start the line or follow typical patterns)
    2. Remove multi-line comments /* ... */
    3. Remove empty lines
    4. Trim lines
    We DO NOT collapse newlines to avoid breaking ASI (Automatic Semicolon Insertion).
    """
    lines = content.split('\n')
    minified_lines = []
    
    in_multiline = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle multi-line comments
        if in_multiline:
            if '*/' in line:
                in_multiline = False
                line = line.split('*/', 1)[1].strip()
                if not line: continue
            else:
                continue
                
        if '/*' in line:
            if '*/' in line:
                # Single line block comment
                line = re.sub(r'/\*.*?\*/', '', line).strip()
                if not line: continue
            else:
                in_multiline = True
                line = line.split('/*', 1)[0].strip()
                if not line: continue

        # Handle single-line comments using regex to avoid matching inside strings (simple heuristic)
        # We only strip // if it's likely not part of a url "http://"
        # A simple robust check for // at start of line
        if line.startswith('//'):
            continue
            
        # For inline comments, it's risky without a parser. 
        # We will skip inline comment removal to be safe against "http://..." strings
        
        minified_lines.append(line)
        
    return '\n'.join(minified_lines)

def process_file(root, filename):
    src_path = os.path.join(root, filename)
    
    # Skip if file is in exclusion list
    if filename in EXCLUDE_FILES or filename.startswith('.'):
        return

    # Compute relative path to maintain structure
    rel_path = os.path.relpath(src_path, SOURCE_DIR)
    dest_path = os.path.join(DEST_DIR, rel_path)
    
    # Create dest directory if needed
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        content = ""
        encoding = 'utf-8'
        
        # Determine if we should attempt minification
        if ext in HTML_EXT or ext in CSS_EXT or ext in JS_EXT:
             try:
                with open(src_path, 'r', encoding=encoding) as f:
                    content = f.read()
             except UnicodeDecodeError:
                # Fallback for binary files masquerading as text or bad encoding
                shutil.copy2(src_path, dest_path)
                return

        if ext in HTML_EXT:
            minified = minify_html(content)
            with open(dest_path, 'w', encoding=encoding) as f:
                f.write(minified)
            print(f"Minified HTML: {rel_path} ({len(content)} -> {len(minified)} bytes)")
            
        elif ext in CSS_EXT:
            minified = minify_css(content)
            with open(dest_path, 'w', encoding=encoding) as f:
                f.write(minified)
            print(f"Minified CSS : {rel_path} ({len(content)} -> {len(minified)} bytes)")
            
        elif ext in JS_EXT:
            minified = minify_js(content)
            with open(dest_path, 'w', encoding=encoding) as f:
                f.write(minified)
            print(f"Minified JS  : {rel_path} ({len(content)} -> {len(minified)} bytes)")
            
        else:
            # Copy all other files (images, fonts, etc.)
            shutil.copy2(src_path, dest_path)
            # print(f"Copied       : {rel_path}") # kept silent for cleanliness
            
    except Exception as e:
        print(f"FAILED {rel_path}: {e}")


def generate_llms_txt(files):
    llms_content = ["# Dalvi Consultancy Website Content\n"]
    llms_content.append(f"Base URL: {BASE_URL}\n\n")
    
    for relative_path in files:
        file_path = os.path.join(DEST_DIR, relative_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', content, re.IGNORECASE | re.DOTALL)
            
            title = title_match.group(1).strip() if title_match else relative_path
            desc = desc_match.group(1).strip() if desc_match else "No description available."
            # Clean up newlines in description
            desc = ' '.join(desc.split())
            
            url_path = relative_path.replace(os.path.sep, '/')
            if url_path.endswith('index.html'):
                url_path = url_path.replace('index.html', '')
            
            full_url = f"{BASE_URL}/{url_path}"
            
            llms_content.append(f"## {title}\n")
            llms_content.append(f"URL: {full_url}\n")
            llms_content.append(f"Description: {desc}\n\n")
            
        except Exception as e:
            print(f"Error processing {relative_path} for llms.txt: {e}")

    with open(os.path.join(DEST_DIR, 'llms.txt'), 'w', encoding='utf-8') as f:
        f.writelines(llms_content)
    print("Generated llms.txt")

def main():
    print(f"Source: {os.path.abspath(SOURCE_DIR)}")
    print(f"Dest  : {os.path.abspath(DEST_DIR)}")
    
    clean_dest()
    
    print("Starting build process...")
    
    processed_files = []
    count = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Filter excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for filename in files:
            process_file(root, filename)
            
            # Track HTML files for sitemap
            if filename.endswith('.html') and filename not in EXCLUDE_FILES:
                rel_path = os.path.relpath(os.path.join(root, filename), SOURCE_DIR)
                processed_files.append(rel_path)
            
            count += 1
            
    generate_sitemap(processed_files)
    generate_robots()
    generate_llms_txt(processed_files)
    
    print(f"\nBuild complete! Processed {count} files. Output available in '{DEST_DIR}/'")

if __name__ == "__main__":
    main()
