"""
fix_project_pages.py
====================
L3 Execution script — Cleanup pass for Premium Agency Light migration.

Fixes remaining issues after apply_project_styles.py:
1. Removes duplicate font link blocks
2. Replaces the old minified nav with the new responsive nav
3. Replaces old mobile overlay with new mobile menu
4. Fixes nav-scrolled in old inline nav

Idempotent.
"""

import os
import re

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

NEW_NAV_BLOCK = """<nav id="main-nav" class="fixed top-0 w-full z-50 bg-white border-b border-[#E2E8F0] transition-all duration-300">
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

NEW_SCRIPT = """<script>
const nav = document.getElementById('main-nav');
window.addEventListener('scroll', () => { nav.classList.toggle('nav-scrolled', window.scrollY > 20); });
const menuBtn = document.getElementById('mobile-menu-btn');
const menuClose = document.getElementById('mobile-menu-close');
const menu = document.getElementById('mobile-menu');
const toggleMenu = () => { menu.classList.toggle('open'); menu.setAttribute('aria-hidden', String(!menu.classList.contains('open'))); };
if (menuBtn) menuBtn.addEventListener('click', toggleMenu);
if (menuClose) menuClose.addEventListener('click', toggleMenu);
if (menu) menu.querySelectorAll('a').forEach(a => a.addEventListener('click', toggleMenu));
</script>"""


def fix_file(filepath: str, filename: str) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    change_log = []

    # ── 1. Remove duplicate font preconnect + font link blocks ────────────────
    # The pattern: two occurrences of the Syne/Manrope link — remove the second
    font_pattern = re.compile(
        r'(<!-- Fonts: Premium Agency Light -->[\s\S]*?</link>|'
        r'<link[^>]*family=Syne[^>]*>)',
        re.IGNORECASE
    )
    syne_links = list(font_pattern.finditer(content))
    if len(syne_links) > 1:
        # Find and remove the second block (lines 29-34 in berrybash)
        # The second block is surrounded by the preconnect links
        dup_block_pattern = re.compile(
            r'\s*<!-- Fonts: Premium Agency Light -->\s*\r?\n'
            r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*\r?\n'
            r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*\r?\n'
            r'\s*<link href="https://fonts\.googleapis\.com/css2\?family=Manrope[^>]*>\s*\r?\n'
            r'\s*<link href="https://fonts\.googleapis\.com/css2\?family=Material[^>]*>\s*\r?\n',
            re.IGNORECASE
        )
        matches = list(dup_block_pattern.finditer(content))
        if len(matches) >= 2:
            # Remove the last occurrence
            m = matches[-1]
            content = content[:m.start()] + content[m.end():]
            change_log.append("  ✔ Removed duplicate font link block")

    # ── 2. Replace old legacy nav (minified) with new nav ─────────────────────
    # Pattern: old nav from <nav class="fixed ... to end of mobile overlay </div>
    old_nav_pattern = re.compile(
        r'<nav class="fixed top-0 w-full z-50 border-b border-white/5 bg-white/80[^>]*>.*?</div>\s*</div>(?=\s*<main)',
        re.IGNORECASE | re.DOTALL
    )
    if old_nav_pattern.search(content):
        content = old_nav_pattern.sub(NEW_NAV_BLOCK, content)
        change_log.append("  ✔ Replaced old legacy nav + mobile overlay")

    # Also handle: old nav without bg-white/80 (original old dark nav that wasn't replaced)
    old_nav_pattern2 = re.compile(
        r'<nav class="fixed top-0 w-full z-50 border-b[^"]*"[^>]*>.*?</div>\s*</div>(?=\s*<main)',
        re.IGNORECASE | re.DOTALL
    )
    if old_nav_pattern2.search(content) and 'id="main-nav"' not in content:
        content = old_nav_pattern2.sub(NEW_NAV_BLOCK, content)
        change_log.append("  ✔ Replaced legacy dark nav + mobile overlay (2nd pass)")

    # ── 3. Make sure nav-scrolled is defined in style block ───────────────────
    if 'nav-scrolled' not in content:
        content = content.replace(
            '  </style>',
            '    .nav-scrolled { box-shadow: 0 1px 12px rgba(15,23,42,.06); }\n  </style>'
        )
        change_log.append("  ✔ Added .nav-scrolled rule")

    # ── 4. Fix mobile-menu overflow (old id=mobile-menu-overlay → id=mobile-menu)
    content = content.replace('id="mobile-menu-overlay"', 'id="mobile-menu"')
    if 'id="mobile-menu-overlay"' in original:
        change_log.append("  ✔ Fixed mobile-menu-overlay → mobile-menu id")

    # ── 5. Clean duplicate preconnect links ───────────────────────────────────
    # Remove duplicate identical preconnect tags
    seen_links = set()
    def dedup_link(m):
        tag = m.group(0).strip()
        if tag in seen_links:
            return ''
        seen_links.add(tag)
        return m.group(0)
    
    link_pat = re.compile(r'<link[^>]*(preconnect|googleapis|gstatic)[^>]*>', re.IGNORECASE)
    new_content = link_pat.sub(dedup_link, content)
    if new_content != content:
        content = new_content
        change_log.append("  ✔ Removed duplicate preconnect/font links")

    # ── 6. Ensure dark:bg-slate-700 corner markers become light ──────────────
    content = content.replace('dark:bg-slate-700', 'bg-[#CBD5E1]')
    if 'dark:bg-slate-700' in original:
        change_log.append("  ✔ Replaced dark:bg-slate-700 corner markers")

    # ── 7. Ensure section backgrounds are light ───────────────────────────────
    # Add alternating section bg like index.html for visual rhythm
    # (This is optional cleanup — keep sections white/surface)
    content = content.replace('<section class="max-w-4xl mx-auto px-6 mb-20"><h2 class="font-syne font-bold text-3xl',
                               '<section class="max-w-4xl mx-auto px-6 mb-20"><h2 class="font-syne font-bold text-3xl')

    if content != original:
        with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(content)
        if change_log:
            print(f"\n[{filename}] — {len(change_log)} fix(es) applied:")
            for entry in change_log:
                print(entry)
        else:
            print(f"\n[{filename}] — Written (whitespace only changes)")
    else:
        print(f"\n[{filename}] — Already clean, no fixes needed.")


def main():
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    html_files = sorted(f for f in os.listdir(PROJECTS_DIR) if f.endswith(".html"))
    print(f"Cleanup pass -> {len(html_files)} file(s)")
    print("=" * 70)

    for filename in html_files:
        fix_file(os.path.join(PROJECTS_DIR, filename), filename)

    print("\n" + "=" * 70)
    print("Cleanup done. Run `npm run css:build` then `python build.py`.")


if __name__ == "__main__":
    main()
