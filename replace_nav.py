"""
replace_nav.py
==============
Direct nav replacement — handles minified/multiline HTML of project subpages.
Replaces from <nav class="fixed top-0 w-full z-50... to closing </div> before <main.
"""
import os
import re

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

NEW_NAV = """<nav id="main-nav" class="fixed top-0 w-full z-50 bg-white border-b border-[#E2E8F0] transition-all duration-300">
  <div class="max-w-7xl mx-auto px-6 md:px-10 h-20 flex items-center justify-between">
    <a href="../index.html" class="flex items-center gap-3 group" aria-label="Dalvi Consultancy Homepage">
      <div class="w-9 h-9 rounded-lg bg-[#0369A1] flex items-center justify-center shrink-0">
        <img src="../logo.svg" alt="Dalvi Consultancy" class="w-7 h-7 object-contain brightness-0 invert">
      </div>
      <span class="font-syne font-extrabold text-xl tracking-tight text-[#0F172A] group-hover:text-[#0369A1] transition-colors">Dalvi Consultancy</span>
    </a>
    <div class="hidden md:flex items-center gap-8">
      <a href="../index.html#services"        class="font-manrope font-medium text-sm text-[#475569] hover:text-[#0369A1] transition-colors">Services</a>
      <a href="../index.html#products"        class="font-manrope font-medium text-sm text-[#475569] hover:text-[#0369A1] transition-colors">Products</a>
      <a href="../index.html#client-projects" class="font-manrope font-medium text-sm text-[#475569] hover:text-[#0369A1] transition-colors">Our Work</a>
      <a href="../index.html#contact" class="ml-2 inline-flex items-center justify-center px-5 py-2.5 bg-[#0369A1] text-white font-manrope font-semibold text-sm rounded-lg hover:bg-[#0284C7] transition-colors shadow-sm">Start a Project</a>
    </div>
    <button id="mobile-menu-btn" class="md:hidden p-2 text-[#475569] hover:text-[#0F172A] transition-colors" aria-label="Open menu">
      <span class="material-symbols-outlined text-2xl">menu</span>
    </button>
  </div>
</nav>
<div id="mobile-menu" class="fixed inset-0 z-[60] bg-white flex flex-col items-center justify-center gap-8 md:hidden" aria-hidden="true">
  <button id="mobile-menu-close" class="absolute top-6 right-6 p-2 text-[#475569] hover:text-[#0F172A]" aria-label="Close menu">
    <span class="material-symbols-outlined text-2xl">close</span>
  </button>
  <nav class="flex flex-col items-center gap-7 text-xl font-syne font-bold text-[#0F172A]">
    <a href="../index.html#services"        class="hover:text-[#0369A1] transition-colors">Services</a>
    <a href="../index.html#products"        class="hover:text-[#0369A1] transition-colors">Products</a>
    <a href="../index.html#client-projects" class="hover:text-[#0369A1] transition-colors">Our Work</a>
    <a href="../index.html#contact" class="mt-2 px-8 py-3.5 bg-[#0369A1] text-white rounded-lg font-manrope font-bold text-base hover:bg-[#0284C7] transition-colors">Start a Project</a>
  </nav>
</div>"""


def process(filepath, filename):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    if 'id="main-nav"' in content:
        print(f"[{filename}] — Already has new nav id, skipping")
        return

    # Strategy: slice from nav start to <main start, replace that whole block
    idx_nav = content.find('<nav class="fixed top-0 w-full z-50')
    idx_main = content.find('<main class=')

    if idx_nav == -1:
        print(f"[{filename}] ✗ No old nav found")
        return
    if idx_main == -1:
        print(f"[{filename}] ✗ No <main> found")
        return

    # Replace the nav+mobile block (everything from nav start to main start)
    content = content[:idx_nav] + NEW_NAV + "\n" + content[idx_main:]
    print(f"[{filename}] ✔ Replaced nav + mobile overlay")

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)


def main():
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    html_files = sorted(f for f in os.listdir(PROJECTS_DIR) if f.endswith(".html"))
    print(f"Nav replacement pass -> {len(html_files)} files")
    print("=" * 60)
    for fn in html_files:
        process(os.path.join(PROJECTS_DIR, fn), fn)
    print("=" * 60)
    print("Done.")

if __name__ == "__main__":
    main()
