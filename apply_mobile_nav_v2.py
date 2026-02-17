import os
import re

PROJECTS_DIR = 'projects'

HAMBURGER_BUTTON = """
            <!-- Mobile Menu Button -->
            <button id="mobile-menu-btn" class="md:hidden text-white p-2" aria-label="Open Menu">
                <span class="material-symbols-outlined text-3xl">menu</span>
            </button>
"""

MOBILE_OVERLAY = """
    <!-- Mobile Menu Overlay -->
    <div id="mobile-menu-overlay"
        class="fixed inset-0 z-[60] bg-background-dark/95 backdrop-blur-xl transition-transform duration-300 translate-x-full md:hidden flex flex-col items-center justify-center gap-8">
        <button id="mobile-menu-close" class="absolute top-6 right-6 text-slate-400 p-2 hover:text-white"
            aria-label="Close Menu">
            <span class="material-symbols-outlined text-3xl">close</span>
        </button>
        
        <nav class="flex flex-col items-center gap-8 text-xl font-display font-medium text-slate-300">
            <a class="hover:text-primary transition-colors" href="../index.html#services">Our Services</a>
            <a class="hover:text-primary transition-colors" href="../index.html#our-products">Our Products</a>
            <a class="hover:text-primary transition-colors" href="../index.html#client-projects">Client Work</a>
            <a class="hover:text-primary transition-colors" href="../index.html#tech-stack">Technologies</a>
            <a class="px-8 py-4 bg-primary text-white rounded-2xl shadow-lg shadow-primary/20 hover:scale-105 transition-transform mt-4"
                href="../index.html#contact">Start a Project</a>
        </nav>
    </div>
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. HIDE DESKTOP BUTTON
    # Pattern to match the button class, allowing for 'hidden md:block' to be already present or not.
    # We want to ensure 'hidden md:block' is there.
    # The class usually starts with "px-5 py-2.5" or "hidden md:block px-5 py-2.5".
    
    class_pattern = r'class="(hidden md:block )?px-5 py-2\.5 bg-primary text-white rounded-full'
    
    def add_hidden_class(match):
        if match.group(1): # Already has hidden md:block
            return match.group(0)
        else:
            return 'class="hidden md:block px-5 py-2.5 bg-primary text-white rounded-full'

    new_content = re.sub(class_pattern, add_hidden_class, content)
    if new_content != content:
        content = new_content
        # print(f"Updated class in {filepath}")

    # 2. ADD HAMBURGER BUTTON
    # Find the closing </div> of the header container.
    # The button (View All ...) is followed by </a> and then </div>.
    # We look for `</a>\s*</div>` where the anchor contains "View All".
    
    if 'id="mobile-menu-btn"' in content:
        # print(f"Hamburger already present in {filepath}")
        pass
    else:
        # Regex to find the closing div of the header flex container
        # It matches: ← View All ... </a> ... </div>
        # We capture everything up to </a> and the following whitespace, then </div>
        # And insert hamburger before </div>
        
        button_container_end = r'(← View All [^<]+</a>\s*)</div>'
        
        if re.search(button_container_end, content):
            content = re.sub(button_container_end, r'\1' + HAMBURGER_BUTTON + '</div>', content)
            # print(f"Added Hamburger to {filepath}")
        else:
            print(f"Warning: Could not find button container end in {filepath}")

    # 3. ADD OVERLAY
    if 'id="mobile-menu-overlay"' in content:
        pass
    else:
        if '</nav>' in content:
            content = content.replace('</nav>', '</nav>' + MOBILE_OVERLAY)
            # print(f"Added Overlay to {filepath}")
        else:
            print(f"Warning: Could not find </nav> in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed {filepath}")

def main():
    if not os.path.exists(PROJECTS_DIR):
        print(f"Directory {PROJECTS_DIR} not found.")
        return

    for filename in os.listdir(PROJECTS_DIR):
        if filename.endswith(".html"):
            filepath = os.path.join(PROJECTS_DIR, filename)
            process_file(filepath)

if __name__ == "__main__":
    main()
