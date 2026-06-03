"""
apply_project_styles.py
=======================
L3 Execution script — Premium Agency Light design system propagation.

Migrates every HTML file under projects/ from the legacy dark glassmorphic
design to the Premium Agency Light system matching the redesigned index.html
(Syne + Manrope, cobalt blue #0369A1, white background, rounded-2xl cards).

Idempotent: running multiple times produces the same result.
"""

import os
import re

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

# ---------------------------------------------------------------------------
# New nav + header HTML fragments (shared across all project subpages)
# ---------------------------------------------------------------------------

NEW_HEAD_FONTS = """\
  <!-- Fonts: Premium Agency Light -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">"""

NEW_HEAD_STYLE = """\
  <style>
    :root {
      --bg:         #FFFFFF;
      --surface:    #F8FAFC;
      --muted:      #F1F5F9;
      --text:       #0F172A;
      --text-muted: #475569;
      --accent:     #0369A1;
      --accent-h:   #0284C7;
      --border:     #E2E8F0;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Manrope', sans-serif; background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; overflow-x: hidden; }
    ::selection { background: var(--accent); color: #fff; }
    #mobile-menu { transform: translateX(100%); transition: transform .3s ease; }
    #mobile-menu.open { transform: translateX(0); }
    .nav-scrolled { box-shadow: 0 1px 12px rgba(15,23,42,.06); }
  </style>"""

NEW_NAVBAR = """\
<nav id="main-nav" class="fixed top-0 w-full z-50 bg-white border-b border-[#E2E8F0] transition-all duration-300">
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
<!-- Mobile menu -->
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

NEW_FOOTER = """\
<footer class="border-t border-[#E2E8F0] bg-white mt-20">
  <div class="max-w-7xl mx-auto px-6 md:px-10 py-10 flex flex-col md:flex-row items-center justify-between gap-6">
    <a href="../index.html" class="font-manrope text-sm text-[#475569] hover:text-[#0369A1] transition-colors">← Back to Dalvi Consultancy</a>
    <p class="font-manrope text-sm text-[#475569]">© 2025 Dalvi Consultancy. Built in Pune, India.</p>
  </div>
</footer>"""

NEW_SCRIPT = """\
<script>
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


# ---------------------------------------------------------------------------
# Ordered list of (description, pattern, replacement) tuples.
# ---------------------------------------------------------------------------

def make_replacements():
    return [

        # ── 1. Remove CDN Tailwind script ──────────────────────────────────
        (
            "Remove CDN Tailwind script",
            re.compile(
                r'<script\s+src="https://cdn\.tailwindcss\.com[^"]*"[^>]*>\s*</script>',
                re.IGNORECASE,
            ),
            "",
        ),

        # ── 2. Remove inline tailwind.config block ─────────────────────────
        (
            "Remove inline tailwind.config block",
            re.compile(
                r'<script[^>]*>\s*tailwind\.config\s*=\s*\{.*?\};\s*</script>',
                re.IGNORECASE | re.DOTALL,
            ),
            "",
        ),

        # ── 3. Remove old Google Fonts (Inter / Plus Jakarta) ──────────────
        (
            "Remove Google Fonts Inter/Jakarta link",
            re.compile(
                r'<link[^>]*fonts\.googleapis\.com/css2\?family=Inter[^>]*>',
                re.IGNORECASE,
            ),
            "",
        ),
        (
            "Remove preconnect googleapis",
            re.compile(
                r'<link[^>]*rel="preconnect"[^>]*fonts\.googleapis\.com[^>]*>',
                re.IGNORECASE,
            ),
            "",
        ),
        (
            "Remove preconnect gstatic",
            re.compile(
                r'<link[^>]*(?:crossorigin[^>]*fonts\.gstatic\.com|fonts\.gstatic\.com[^>]*crossorigin)[^>]*>',
                re.IGNORECASE,
            ),
            "",
        ),
        # Remove duplicate Material Symbols CDN link (keep only one)
        (
            "Remove duplicate Material Symbols link",
            re.compile(
                r'(<link href="https://fonts\.googleapis\.com/css2\?family=Material\+Symbols[^>]*>\s*)(<link href="https://fonts\.googleapis\.com/css2\?family=Material\+Symbols[^>]*>)',
                re.IGNORECASE,
            ),
            r'\1',
        ),

        # ── 4. Replace <html> attributes ───────────────────────────────────
        (
            "Replace html tag — remove dark class, keep lang",
            re.compile(
                r'<html\s[^>]*(lang="en")[^>]*>',
                re.IGNORECASE,
            ),
            r'<html \1>',
        ),

        # ── 5. Replace <body> class ─────────────────────────────────────────
        (
            "Replace body — remove dark/glass bg classes",
            re.compile(
                r'<body[^>]*class="[^"]*"[^>]*>',
                re.IGNORECASE,
            ),
            '<body>',
        ),

        # ── 6. Inline .glass style block ───────────────────────────────────
        (
            "Remove inline .glass style block",
            re.compile(
                r'<style>\s*\.glass\s*\{[^}]*\}\s*</style>',
                re.IGNORECASE | re.DOTALL,
            ),
            NEW_HEAD_STYLE,
        ),

        # ── 7. Old Material Symbols font link → upgrade with Syne+Manrope ─
        (
            "Replace Material Symbols link with full font stack",
            re.compile(
                r'<link href="https://fonts\.googleapis\.com/css2\?family=Material\+Symbols[^>]*>',
                re.IGNORECASE,
            ),
            NEW_HEAD_FONTS,
        ),

        # ── 8. Replace old nav+mobile overlay block ────────────────────────
        # Pattern: from <nav ... to end of mobile overlay div
        (
            "Replace legacy nav + mobile overlay",
            re.compile(
                r'<nav class="fixed top-0 w-full z-50.*?</div>\s*</div>(?=\s*<main)',
                re.IGNORECASE | re.DOTALL,
            ),
            NEW_NAVBAR,
        ),

        # ── 9. Hero badge — rounded-full glass → clean pill ────────────────
        (
            "Replace hero badge glass style",
            re.compile(
                r'class="inline-block px-4 py-2 rounded-full glass border border-primary/20 text-primary text-sm font-semibold mb-6"',
                re.IGNORECASE,
            ),
            'class="inline-block px-3 py-1 bg-[#EFF6FF] border border-[#BFDBFE] text-[#0369A1] text-xs font-manrope font-bold uppercase tracking-widest rounded-full mb-6"',
        ),

        # ── 10. H1 title ────────────────────────────────────────────────────
        (
            "Update H1 font-display → font-syne, remove tracking-tight → tracking-tight text-[#0F172A]",
            re.compile(
                r'class="font-display text-5xl md:text-7xl font-extrabold tracking-tight mb-6"',
                re.IGNORECASE,
            ),
            'class="font-syne font-extrabold text-5xl md:text-7xl tracking-tight mb-6 text-[#0F172A]"',
        ),

        # ── 11. Hero subtitle text color ────────────────────────────────────
        (
            "Update hero subtitle text color (text-slate-400 → text-[#475569])",
            re.compile(
                r'class="text-xl text-slate-400 max-w-2xl mx-auto"',
                re.IGNORECASE,
            ),
            'class="font-manrope text-xl text-[#475569] max-w-2xl mx-auto"',
        ),
        (
            "Replace strong text-white in hero → text-[#0F172A]",
            re.compile(r'<strong class="text-white">', re.IGNORECASE),
            '<strong class="text-[#0F172A]">',
        ),

        # ── 12. About section glass rounded-3xl → white card ───────────────
        (
            "Replace glass rounded-3xl about section",
            re.compile(
                r'class="glass rounded-3xl p-10"',
                re.IGNORECASE,
            ),
            'class="bg-white rounded-2xl border border-[#E2E8F0] p-10 shadow-sm"',
        ),

        # ── 13. Section H2 headings ─────────────────────────────────────────
        (
            "Update H2 font-display text-3xl mb-6 → font-syne",
            re.compile(
                r'class="font-display text-3xl font-bold mb-6"',
                re.IGNORECASE,
            ),
            'class="font-syne font-bold text-3xl text-[#0F172A] mb-6"',
        ),
        (
            "Update H2 font-display text-3xl mb-10 text-center → font-syne",
            re.compile(
                r'class="font-display text-3xl font-bold mb-10 text-center"',
                re.IGNORECASE,
            ),
            'class="font-syne font-bold text-3xl text-[#0F172A] mb-10 text-center"',
        ),
        (
            "Update H2 font-display text-2xl mb-8 → font-syne",
            re.compile(
                r'class="font-display text-2xl font-bold mb-8"',
                re.IGNORECASE,
            ),
            'class="font-syne font-bold text-2xl text-[#0F172A] mb-8"',
        ),
        (
            "Update H3 font-display text-xl mb-2 → font-syne",
            re.compile(
                r'class="font-display text-xl font-bold mb-2"',
                re.IGNORECASE,
            ),
            'class="font-syne font-bold text-xl text-[#0F172A] mb-2"',
        ),
        (
            "Update H3 font-display text-lg mb-3 → font-syne",
            re.compile(
                r'class="font-display text-lg font-bold mb-3"',
                re.IGNORECASE,
            ),
            'class="font-syne font-bold text-lg text-[#0F172A] mb-3"',
        ),
        (
            "Update H3 font-display font-bold mb-2 (any inline headings)",
            re.compile(
                r'class="font-display font-bold mb-2"',
                re.IGNORECASE,
            ),
            'class="font-syne font-bold text-[#0F172A] mb-2"',
        ),

        # ── 14. Feature cards glass → rounded-2xl card ─────────────────────
        (
            "Replace feature article glass rounded-none p-6 → rounded-2xl card",
            re.compile(
                r'class="glass rounded-none p-6(?:\s+card-hover)?"',
                re.IGNORECASE,
            ),
            'class="group p-6 rounded-2xl border border-[#E2E8F0] bg-white hover:border-[#0369A1] hover:-translate-y-1 hover:shadow-lg hover:shadow-[#0369A1]/5 transition-all duration-300"',
        ),

        # ── 15. Related project link cards ──────────────────────────────────
        (
            "Replace related project link cards glass → rounded-2xl",
            re.compile(
                r'class="glass rounded-none p-6 hover:border-primary/50 transition-colors block"',
                re.IGNORECASE,
            ),
            'class="p-6 rounded-2xl border border-[#E2E8F0] bg-white hover:border-[#0369A1] hover:-translate-y-1 hover:shadow-md transition-all duration-300 block"',
        ),

        # ── 16. Icon colors (text-primary → text-[#0369A1]) ─────────────────
        (
            "Replace icon text-primary → text-[#0369A1]",
            re.compile(
                r'(class="material-symbols-outlined [^"]*?)text-primary([^"]*?")',
                re.IGNORECASE,
            ),
            r'\1text-[#0369A1]\2',
        ),

        # ── 17. Body text colors ─────────────────────────────────────────────
        (
            "Replace text-slate-400 → text-[#475569]",
            re.compile(r'\btext-slate-400\b', re.IGNORECASE),
            "text-[#475569]",
        ),
        (
            "Replace text-slate-500 → text-[#475569]",
            re.compile(r'\btext-slate-500\b', re.IGNORECASE),
            "text-[#475569]",
        ),
        (
            "Replace text-slate-300 → text-[#64748B]",
            re.compile(r'\btext-slate-300\b', re.IGNORECASE),
            "text-[#64748B]",
        ),
        (
            "Replace text-slate-100 → text-[#0F172A]",
            re.compile(r'\btext-slate-100\b', re.IGNORECASE),
            "text-[#0F172A]",
        ),
        (
            "Replace standalone text-primary → text-[#0369A1]",
            re.compile(r'(?<!\w)text-primary(?!\w)', re.IGNORECASE),
            "text-[#0369A1]",
        ),

        # ── 18. Background tokens ────────────────────────────────────────────
        (
            "Replace bg-background-dark-dark → bg-white",
            re.compile(r'\bbg-background-dark-dark\b', re.IGNORECASE),
            "bg-white",
        ),
        (
            "Replace bg-background-dark → bg-white",
            re.compile(r'\bbg-background-dark\b', re.IGNORECASE),
            "bg-white",
        ),
        (
            "Replace bg-background → bg-white",
            re.compile(r'\bbg-background\b', re.IGNORECASE),
            "bg-white",
        ),

        # ── 19. <main> padding top ───────────────────────────────────────────
        (
            "Update main pt-32 → pt-28 (new nav height)",
            re.compile(r'<main class="pt-32">', re.IGNORECASE),
            '<main class="pt-28 bg-white">',
        ),

        # ── 20. Footer ───────────────────────────────────────────────────────
        (
            "Replace legacy dark footer",
            re.compile(
                r'<footer[^>]*class="border-t[^"]*py-10[^"]*"[^>]*>.*?</footer>',
                re.IGNORECASE | re.DOTALL,
            ),
            NEW_FOOTER,
        ),

        # ── 21. Old script tag (scripts.js) → new inline script ─────────────
        (
            "Replace <script src=scripts.js> → new inline script",
            re.compile(
                r'<script src="\.\./scripts\.js">\s*</script>',
                re.IGNORECASE,
            ),
            NEW_SCRIPT,
        ),

        # ── 22. CTA section glass rounded-3xl → light bg card ───────────────
        (
            "Replace CTA glass rounded-3xl p-10 text-center",
            re.compile(
                r'class="glass rounded-3xl p-10 text-center"',
                re.IGNORECASE,
            ),
            'class="bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] p-10 text-center"',
        ),
        (
            "Replace CTA primary button → new style",
            re.compile(
                r'class="px-8 py-4 bg-primary text-white font-bold rounded-none hover:scale-105 transition-transform flex items-center gap-2"',
                re.IGNORECASE,
            ),
            'class="inline-flex items-center gap-2 px-8 py-4 bg-[#0369A1] text-white font-manrope font-bold rounded-lg hover:bg-[#0284C7] hover:-translate-y-0.5 transition-all shadow-lg shadow-[#0369A1]/20"',
        ),
        (
            "Replace CTA secondary button → new style (glass border)",
            re.compile(
                r'class="px-8 py-4 glass text-white font-bold rounded-none hover:bg-white/10 transition-colors border border-white/10"',
                re.IGNORECASE,
            ),
            'class="px-8 py-4 border-2 border-[#0369A1] text-[#0369A1] font-manrope font-bold rounded-lg hover:bg-[#EFF6FF] transition-all"',
        ),

        # ── 23. Mobile btn-primary → new button style ────────────────────────
        (
            "Replace btn-primary nav link → new button",
            re.compile(
                r'class="hidden md:block btn-primary px-5 py-2\.5"',
                re.IGNORECASE,
            ),
            'class="hidden md:block px-5 py-2.5 bg-[#0369A1] text-white font-manrope font-semibold text-sm rounded-lg hover:bg-[#0284C7] transition-colors"',
        ),
        (
            "Replace mobile btn-primary → new button",
            re.compile(
                r'class="btn-primary px-8 py-4 rounded-none mt-4"',
                re.IGNORECASE,
            ),
            'class="mt-4 px-8 py-3.5 bg-[#0369A1] text-white font-manrope font-bold rounded-lg hover:bg-[#0284C7] transition-colors"',
        ),

        # ── 24. Foodle Be / legacy inline nav styles ─────────────────────────
        (
            "Replace Foodle Be glass-nav inline style",
            re.compile(
                r'class="glass-nav"\s+style="[^"]*"',
                re.IGNORECASE,
            ),
            'class="fixed top-0 w-full z-50 bg-white border-b border-[#E2E8F0] transition-all duration-300"',
        ),
        (
            "Replace Foodle Be glass-card → white card",
            re.compile(r'class="glass-card"', re.IGNORECASE),
            'class="bg-white rounded-2xl border border-[#E2E8F0] p-8 shadow-sm"',
        ),
        (
            "Replace Foodle Be project-img-container glass-card",
            re.compile(r'class="project-img-container glass-card"', re.IGNORECASE),
            'class="rounded-2xl overflow-hidden border border-[#E2E8F0]"',
        ),
        (
            "Replace Foodle Be cta-button",
            re.compile(r'class="cta-button[^"]*"', re.IGNORECASE),
            'class="inline-flex items-center gap-2 px-8 py-4 bg-[#0369A1] text-white font-manrope font-bold rounded-lg hover:bg-[#0284C7] transition-colors"',
        ),
        (
            "Replace Foodle Be footer inline style tag",
            re.compile(
                r'<footer style="text-align: center; padding: 2rem; color: #52525b; font-size: 0\.875rem;">',
                re.IGNORECASE,
            ),
            '<footer class="border-t border-[#E2E8F0] bg-white py-10 text-center">',
        ),

        # ── 25. Strip stray .glass references ────────────────────────────────
        (
            "Remove stray 'glass' class tokens",
            re.compile(
                r'(?<=class=")([^"]*)\bglass\b([^"]*)',
                re.IGNORECASE,
            ),
            r'\1\2',
        ),

        # ── 26. rounded-full on badges (keep pill shapes) ────────────────────
        # We keep rounded-full only on avatar/badge items; remove from cards:
        (
            "Replace rounded-3xl → rounded-2xl",
            re.compile(r'\brounded-3xl\b', re.IGNORECASE),
            "rounded-2xl",
        ),
        (
            "Replace rounded-xl → rounded-xl (keep, it's fine for icons)",
            re.compile(r'\brounded-none\b', re.IGNORECASE),
            "rounded-2xl",
        ),

        # ── 27. Clean double spaces in class attrs ────────────────────────────
        (
            "Clean double spaces in class attrs",
            re.compile(r'(?<=class=")(\s{2,})', re.IGNORECASE),
            " ",
        ),
    ]


# ---------------------------------------------------------------------------
# Core processor
# ---------------------------------------------------------------------------

def process_file(filepath: str, filename: str, replacements: list) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    change_log = []

    for desc, pattern, repl in replacements:
        new_content, n = pattern.subn(repl, content)
        if n > 0:
            change_log.append(f"  ✔ [{n}x] {desc}")
            content = new_content

    # Ensure <html> does NOT have dark class (light theme)
    content = re.sub(r'<html([^>]*)\bclass="[^"]*dark[^"]*"', r'<html\1', content)

    # Ensure stylesheets order: design tokens style block + fonts are in <head>
    # If the new head style isn't in place, inject before </head>
    if 'font-family: \'Manrope\'' not in content and '--accent' not in content:
        content = content.replace('</head>', NEW_HEAD_STYLE + '\n</head>', 1)
        change_log.append("  ✔ Injected design token <style> block")
    if "family=Syne" not in content:
        content = content.replace('</head>', NEW_HEAD_FONTS + '\n</head>', 1)
        change_log.append("  ✔ Injected Syne+Manrope font links")

    # Ensure styles.css is linked
    if '../styles.css' not in content:
        content = content.replace('</head>', '  <link rel="stylesheet" href="../styles.css">\n</head>', 1)
        change_log.append("  ✔ Added ../styles.css link")

    if content != original:
        with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(content)
        print(f"\n[{filename}] — {len(change_log)} change(s) applied:")
        for entry in change_log:
            print(entry)
    else:
        print(f"\n[{filename}] — Already up-to-date, no changes needed.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(PROJECTS_DIR):
        print(f"ERROR: Directory not found: {PROJECTS_DIR}")
        return

    replacements = make_replacements()
    html_files = sorted(f for f in os.listdir(PROJECTS_DIR) if f.endswith(".html"))

    if not html_files:
        print("No HTML files found in projects/")
        return

    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    print(f"Premium Agency Light propagation -> {len(html_files)} file(s) in {PROJECTS_DIR}")
    print("=" * 70)

    for filename in html_files:
        process_file(os.path.join(PROJECTS_DIR, filename), filename, replacements)

    print("\n" + "=" * 70)
    print("Done. Run `npm run css:build` then `python build.py` to rebuild.")


if __name__ == "__main__":
    main()
