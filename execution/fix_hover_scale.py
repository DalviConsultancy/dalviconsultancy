import os

FILE_PATH = 'index.html'

def fix_hover_scale():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Target: group-hover:scale-[1.02] 
        # distinct from just scale-[1.02] or hover:scale-[1.02]
        # We need to be careful not to double apply if ran multiple times
        
        target = 'group-hover:scale-[1.02]'
        replacement = 'group-hover:scale-x-[1.02] group-hover:scale-y-[1.032]'
        
        if target in content:
            new_content = content.replace(target, replacement)
            
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Successfully updated {FILE_PATH}. Replaced uniform scale with non-uniform scale.")
        else:
            print(f"Target string '{target}' not found in {FILE_PATH}. It might have been already updated.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_hover_scale()
