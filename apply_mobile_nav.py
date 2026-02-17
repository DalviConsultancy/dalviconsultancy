import os

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

    if 'id="mobile-menu-overlay"' in content:
        print(f"Skipping {filepath}: Already has mobile menu")
        return

    # Hide Desktop Button on Mobile
    content = content.replace(
        'class="px-5 py-2.5 bg-primary text-white rounded-full font-medium"',
        'class="hidden md:block px-5 py-2.5 bg-primary text-white rounded-full font-medium"'
    )

    # Add Hamburger Button
    # Look for the closing div of the flex container inside nav
    # The structure is <div class="..."> ... <a ...>← View All Client Work</a></div>
    # We want to insert before that last </div>
    
    # We will search for the specific closing tag sequence of the header div
    # It ends with ...View All Client Work</a></div>
    
    if 'View All Client Work</a></div>' in content:
        content = content.replace(
            'View All Client Work</a></div>',
            'View All Client Work</a>' + HAMBURGER_BUTTON + '</div>'
        )
    else:
        print(f"Warning: Could not find header div end in {filepath}")

    # Add Overlay after </nav>
    if '</nav>' in content:
        content = content.replace('</nav>', '</nav>' + MOBILE_OVERLAY)
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
