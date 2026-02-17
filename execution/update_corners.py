import os

PROJECTS_DIR = 'projects'
ROOT_FILES = ['index.html']
TARGET_STRING = 'rounded-2xl'
REPLACEMENT_STRING = 'rounded-none'

def update_files():
    count = 0
    # Update projects directory
    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith('.html') or filename == 'apply_project_styles.py':
            filepath = os.path.join(PROJECTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if TARGET_STRING in content:
                    new_content = content.replace(TARGET_STRING, REPLACEMENT_STRING)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filename}")
                    count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Update root files
    for filename in ROOT_FILES:
        filepath = filename 
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if TARGET_STRING in content:
                new_content = content.replace(TARGET_STRING, REPLACEMENT_STRING)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filename}")
                count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Process complete. Updated {count} files.")

if __name__ == "__main__":
    update_files()
