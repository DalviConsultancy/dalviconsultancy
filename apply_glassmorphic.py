"""
apply_glassmorphic.py
=====================
L3 Execution — Glassmorphic design system propagation.

Converts every HTML file (index.html + projects/*.html) from the
Kinetic Brutalism theme back to Premium Glassmorphism / Modern Dark SaaS.

Idempotent: safe to run multiple times.
"""

import os
import re

ROOT_DIR     = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(ROOT_DIR, "projects")

# ── Google Fonts link tags to inject into <head> ────────────────────────────
GOOGLE_FONTS_LINKS = """\
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">"""


def make_replacements():
    """Return ordered (description, compiled_pattern, replacement) tuples."""
    return [

        # ── 1. Inject Google Fonts before </head> if not already there ───────
        # Handled separately in process_file() to avoid double-injection.

        # ── 2. Remove any leftover CDN tailwind script ───────────────────────
        (
            "Remove CDN Tailwind script",
            re.compile(
                r'<script\s+src="https://cdn\.tailwindcss\.com[^"]*"[^>]*>\s*</script>',
                re.IGNORECASE,
            ),
            "",
        ),

        # ── 3. Remove stale inline tailwind.config script blocks ─────────────
        (
            "Remove inline tailwind.config block",
            re.compile(
                r'<script[^>]*>\s*tailwind\.config\s*=\s*\{.*?\};\s*</script>',
                re.IGNORECASE | re.DOTALL,
            ),
            "",
        ),

        # ── 4. <html> — make sure dark class is present ─────────────────────
        # (body/html resets handled below)

        # ── 5. <body> class — glassmorphic base classes ──────────────────────
        (
            "Replace body class tokens (brutalist → glassmorphic)",
            re.compile(r'(<body[^>]*class=")[^"]*(")', re.IGNORECASE),
            r'\1bg-background-dark text-slate-100 font-sans overflow-x-hidden\2',
        ),
        (
            "Remove body inline background style",
            re.compile(
                r'(<body[^>]*)\s+style="background-color:\s*#030712;\s*color:\s*#f8fafc"',
                re.IGNORECASE,
            ),
            r"\1",
        ),

        # ── 6. Nav bar ───────────────────────────────────────────────────────
        (
            "Restore nav glass border (brutalist → glass)",
            re.compile(
                r'border-b-2\s+border-foreground\s+bg-background/90\s+backdrop-blur-sm',
                re.IGNORECASE,
            ),
            "border-b border-white/5 bg-background-dark/80 backdrop-blur-md",
        ),
        # Fallback for any remaining brutalist nav combo
        (
            "Restore nav glass border (fallback)",
            re.compile(
                r'border-b-2\s+border-foreground\s+bg-background/90',
                re.IGNORECASE,
            ),
            "border-b border-white/5 bg-background-dark/80 backdrop-blur-md",
        ),

        # ── 7. Nav CTA button ────────────────────────────────────────────────
        (
            "Restore nav CTA button style",
            re.compile(
                r'class="hidden md:block brutal-btn-primary px-5 py-2\.5 text-xs font-bold uppercase tracking-widest"',
                re.IGNORECASE,
            ),
            'class="hidden md:block btn-primary px-5 py-2.5"',
        ),

        # ── 8. Theme toggle button ───────────────────────────────────────────
        (
            "Restore desktop theme toggle style",
            re.compile(
                r'id="theme-toggle" class="brutal-btn-secondary[^"]*"',
                re.IGNORECASE,
            ),
            'id="theme-toggle" class="btn-ghost p-2 flex items-center justify-center"',
        ),
        (
            "Restore mobile theme toggle style",
            re.compile(
                r'id="theme-toggle-mobile" class="brutal-btn-secondary[^"]*"',
                re.IGNORECASE,
            ),
            'id="theme-toggle-mobile" class="btn-ghost p-2 flex items-center justify-center"',
        ),

        # ── 9. Mobile hamburger button ───────────────────────────────────────
        (
            "Restore hamburger button style",
            re.compile(
                r'id="mobile-menu-btn" class="brutal-border[^"]*"',
                re.IGNORECASE,
            ),
            'id="mobile-menu-btn" class="md:hidden text-white p-2" ',
        ),

        # ── 10. Mobile menu overlay ──────────────────────────────────────────
        (
            "Restore mobile menu overlay bg",
            re.compile(r'bg-background/95', re.IGNORECASE),
            "bg-background-dark/95",
        ),
        (
            "Remove brutalist left border on mobile overlay",
            re.compile(r'\s*border-l-2\s+border-foreground', re.IGNORECASE),
            "",
        ),
        (
            "Restore mobile close button",
            re.compile(
                r'id="mobile-menu-close" class="absolute top-6 right-6 brutal-btn-secondary[^"]*"',
                re.IGNORECASE,
            ),
            'id="mobile-menu-close" class="absolute top-6 right-6 text-slate-400 p-2 hover:text-white"',
        ),
        (
            "Restore mobile nav font",
            re.compile(
                r'<nav class="flex flex-col items-center gap-8 text-xl font-display font-black uppercase tracking-wider text-foreground"',
                re.IGNORECASE,
            ),
            '<nav class="flex flex-col items-center gap-8 text-xl font-display font-medium text-slate-300"',
        ),
        (
            "Restore mobile CTA button",
            re.compile(
                r'class="brutal-btn-primary px-8 py-4 text-base font-bold uppercase tracking-widest mt-4"',
                re.IGNORECASE,
            ),
            'class="btn-primary px-8 py-4 rounded-none mt-4"',
        ),
        (
            "Replace hover:text-accent with hover:text-primary",
            re.compile(r'\bhover:text-accent\b', re.IGNORECASE),
            "hover:text-primary",
        ),

        # ── 11. Logo box in nav ───────────────────────────────────────────────
        # Remove brutalist border-2 border-foreground wrapper, keep img
        (
            "Restore plain logo img in nav (project pages)",
            re.compile(
                r'<div class="w-10 h-10 bg-transparent flex items-center justify-center border-2 border-foreground">\s*'
                r'<img src="\.\./logo\.svg" alt="Dalvi Consultancy Logo"[^>]*>\s*</div>',
                re.IGNORECASE | re.DOTALL,
            ),
            '<img src="../logo.svg" alt="Dalvi Consultancy" class="w-10 h-10">',
        ),
        (
            "Restore plain logo img in nav (index)",
            re.compile(
                r'<div class="w-10 h-10 bg-transparent flex items-center justify-center brutal-border border-foreground">\s*'
                r'<img src="logo\.svg"[^>]*>\s*</div>',
                re.IGNORECASE | re.DOTALL,
            ),
            '<img src="logo.svg" alt="Dalvi Consultancy Logo" class="w-10 h-10">',
        ),
        (
            "Restore plain logo img in nav v2 (index)",
            re.compile(
                r'<div class="w-10 h-10 bg-transparent flex items-center justify-center border-2 border-foreground">\s*'
                r'<img src="logo\.svg"[^>]*>\s*</div>',
                re.IGNORECASE | re.DOTALL,
            ),
            '<img src="logo.svg" alt="Dalvi Consultancy Logo" class="w-10 h-10">',
        ),

        # ── 12. Brand name in nav ─────────────────────────────────────────────
        (
            "Restore brand name style",
            re.compile(
                r'class="font-display font-black text-(?:xl|2xl) tracking-tighter uppercase"',
                re.IGNORECASE,
            ),
            'class="font-display font-bold text-xl"',
        ),
        # Index specific with text-2xl
        (
            "Restore index brand name (text-2xl)",
            re.compile(
                r'class="font-display font-black text-2xl tracking-tighter uppercase"',
                re.IGNORECASE,
            ),
            'class="font-display font-bold text-xl"',
        ),

        # ── 13. Hero badge ────────────────────────────────────────────────────
        (
            "Restore hero badge (brutalist → pill glass)",
            re.compile(
                r'class="inline-block px-4 py-2 border-2 border-foreground bg-background text-foreground text-xs font-black uppercase tracking-widest mb-6"',
                re.IGNORECASE,
            ),
            'class="inline-block px-4 py-2 rounded-full glass border border-primary/20 text-primary text-sm font-semibold mb-6"',
        ),
        # Project pages hero badge
        (
            "Restore project hero badge (brutalist → pill glass)",
            re.compile(
                r'class="inline-block px-4 py-2 border-2 border-foreground bg-background text-foreground text-xs font-black uppercase tracking-widest mb-6"',
                re.IGNORECASE,
            ),
            'class="inline-block px-4 py-2 rounded-full glass border border-primary/20 text-primary text-sm font-semibold mb-6"',
        ),

        # ── 14. H1 headings ───────────────────────────────────────────────────
        (
            "Restore H1 style (brutalist → premium)",
            re.compile(
                r'class="font-display text-5xl md:text-7xl font-black uppercase tracking-tighter mb-6 text-foreground"',
                re.IGNORECASE,
            ),
            'class="font-display text-5xl md:text-7xl font-extrabold tracking-tight mb-6"',
        ),

        # ── 15. Hero subtitle ─────────────────────────────────────────────────
        (
            "Restore hero subtitle color",
            re.compile(
                r'class="text-xl text-secondary max-w-2xl mx-auto"',
                re.IGNORECASE,
            ),
            'class="text-xl text-slate-400 max-w-2xl mx-auto"',
        ),
        (
            "Restore strong text in hero",
            re.compile(r'<strong class="text-foreground">', re.IGNORECASE),
            '<strong class="text-white">',
        ),

        # ── 16. Section headings ──────────────────────────────────────────────
        (
            "Restore H2 (text-3xl mb-6)",
            re.compile(
                r'class="font-display text-3xl font-black uppercase tracking-tight mb-6 text-foreground"',
                re.IGNORECASE,
            ),
            'class="font-display text-3xl font-bold mb-6"',
        ),
        (
            "Restore H2 (text-3xl mb-10 text-center)",
            re.compile(
                r'class="font-display text-3xl font-black uppercase tracking-tight mb-10 text-center text-foreground"',
                re.IGNORECASE,
            ),
            'class="font-display text-3xl font-bold mb-10 text-center"',
        ),
        (
            "Restore H2 (text-2xl mb-8)",
            re.compile(
                r'class="font-display text-2xl font-black uppercase tracking-tight mb-8 text-foreground"',
                re.IGNORECASE,
            ),
            'class="font-display text-2xl font-bold mb-8"',
        ),
        (
            "Restore H3 (text-xl mb-2)",
            re.compile(
                r'class="font-display text-xl font-black uppercase tracking-tight mb-2 text-foreground"',
                re.IGNORECASE,
            ),
            'class="font-display text-xl font-bold mb-2"',
        ),
        (
            "Restore H3 FAQ (text-lg mb-3)",
            re.compile(
                r'class="font-display text-lg font-black uppercase tracking-tight mb-3 text-foreground"',
                re.IGNORECASE,
            ),
            'class="font-display text-lg font-bold mb-3"',
        ),

        # ── 17. About section card ────────────────────────────────────────────
        (
            "Restore about section glass card",
            re.compile(
                r'class="border-2 border-foreground bg-background p-10"',
                re.IGNORECASE,
            ),
            'class="glass rounded-3xl p-10"',
        ),

        # ── 18. Feature cards ─────────────────────────────────────────────────
        (
            "Restore feature cards (brutal → glass-card)",
            re.compile(
                r'class="brutal-card brutal-card-hover-yellow p-6 cursor-pointer"',
                re.IGNORECASE,
            ),
            'class="glass rounded-none p-6 card-hover"',
        ),
        (
            "Restore related project cards",
            re.compile(
                r'class="brutal-card brutal-card-hover-yellow p-6 block cursor-pointer"',
                re.IGNORECASE,
            ),
            'class="glass rounded-none p-6 hover:border-primary/50 transition-colors block"',
        ),
        # Any leftover brutal-card
        (
            "Restore any remaining brutal-card",
            re.compile(
                r'class="brutal-card([^"]*)"',
                re.IGNORECASE,
            ),
            r'class="glass rounded-2xl\1"',
        ),

        # ── 19. Icon colors ───────────────────────────────────────────────────
        (
            "Restore icon text-accent → text-primary",
            re.compile(
                r'(class="material-symbols-outlined [^"]*?)text-accent([^"]*?")',
                re.IGNORECASE,
            ),
            r'\1text-primary\2',
        ),

        # ── 20. Text color tokens ─────────────────────────────────────────────
        (
            "Replace text-secondary → text-slate-400",
            re.compile(r'\btext-secondary\b', re.IGNORECASE),
            "text-slate-400",
        ),
        (
            "Replace text-foreground (non-heading) → text-white",
            re.compile(r'\btext-foreground\b', re.IGNORECASE),
            "text-white",
        ),
        (
            "Replace text-accent → text-primary",
            re.compile(r'(?<!\w)text-accent(?!\w)', re.IGNORECASE),
            "text-primary",
        ),

        # ── 21. Background tokens ─────────────────────────────────────────────
        (
            "Replace bg-background → bg-background-dark",
            re.compile(r'\bbg-background\b(?!/)', re.IGNORECASE),
            "bg-background-dark",
        ),
        (
            "Replace bg-background/90 → bg-background-dark/80",
            re.compile(r'\bbg-background/90\b', re.IGNORECASE),
            "bg-background-dark/80",
        ),

        # ── 22. CTA section (RTO Buddy muted bg) ─────────────────────────────
        (
            "Restore CTA section glass",
            re.compile(
                r'class="border-2 border-foreground bg-muted p-10 text-center"',
                re.IGNORECASE,
            ),
            'class="glass rounded-3xl p-10 text-center"',
        ),

        # ── 23. CTA buttons in RTO section ───────────────────────────────────
        (
            "Restore primary CTA button in RTO",
            re.compile(
                r'class="brutal-btn-primary px-8 py-4 font-bold flex items-center gap-2"',
                re.IGNORECASE,
            ),
            'class="btn-primary px-8 py-4 rounded-none flex items-center gap-2"',
        ),
        (
            "Restore secondary CTA button in RTO",
            re.compile(
                r'class="brutal-btn-secondary px-8 py-4 font-bold"',
                re.IGNORECASE,
            ),
            'class="btn-ghost px-8 py-4 rounded-none"',
        ),

        # ── 24. All remaining brutal-btn-primary ─────────────────────────────
        (
            "Restore any remaining brutal-btn-primary",
            re.compile(r'\bbrutal-btn-primary\b', re.IGNORECASE),
            "btn-primary",
        ),
        (
            "Restore any remaining brutal-btn-secondary",
            re.compile(r'\bbrutal-btn-secondary\b', re.IGNORECASE),
            "btn-ghost",
        ),

        # ── 25. Footer ────────────────────────────────────────────────────────
        (
            "Restore footer (brutalist → glass)",
            re.compile(
                r'class="border-t-2 border-foreground py-10 px-6 bg-background-dark"',
                re.IGNORECASE,
            ),
            'class="border-t border-white/5 py-10 px-6 bg-background-dark"',
        ),
        (
            "Restore footer back link",
            re.compile(
                r'class="text-secondary hover:text-primary transition-colors font-bold uppercase tracking-wider text-sm"',
                re.IGNORECASE,
            ),
            'class="text-slate-400 hover:text-primary transition-colors"',
        ),
        (
            "Restore footer copyright text",
            re.compile(
                r'class="text-sm text-secondary font-bold uppercase tracking-wider"',
                re.IGNORECASE,
            ),
            'class="text-sm text-slate-500"',
        ),

        # ── 26. Restore any remaining border-2 border-foreground ─────────────
        (
            "Replace stray border-2 border-foreground → border border-white/10",
            re.compile(r'\bborder-2\s+border-foreground\b', re.IGNORECASE),
            "border border-white/10",
        ),
        (
            "Replace stray border-b-2 border-foreground → border-b border-white/5",
            re.compile(r'\bborder-b-2\s+border-foreground\b', re.IGNORECASE),
            "border-b border-white/5",
        ),
        (
            "Replace stray border-t-2 border-foreground → border-t border-white/5",
            re.compile(r'\bborder-t-2\s+border-foreground\b', re.IGNORECASE),
            "border-t border-white/5",
        ),

        # ── 27. Rounded-none on specific cards → rounded-2xl ─────────────────
        # (We already explicitly set rounded-none on some glass cards for style reasons — leave them)

        # ── 28. Fix selection color ───────────────────────────────────────────
        (
            "Restore selection color class",
            re.compile(r'\bselection:bg-accent/30\b', re.IGNORECASE),
            "selection:bg-primary/30",
        ),

        # ── 29. Foodle Be nav restore ─────────────────────────────────────────
        (
            "Restore Foodle Be nav class",
            re.compile(
                r'class="fixed top-0 w-full z-50 border-b-2 border-foreground bg-background/90 backdrop-blur-sm"',
                re.IGNORECASE,
            ),
            'class="glass-nav" style="position:fixed;top:0;width:100%;z-index:1000;padding:1rem 0;backdrop-filter:blur(10px);background:rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.1);"',
        ),
        (
            "Restore Foodle Be img container",
            re.compile(
                r'class="border-2 border-foreground overflow-hidden"',
                re.IGNORECASE,
            ),
            'class="project-img-container glass-card"',
        ),
        (
            "Restore Foodle Be glass-card",
            re.compile(
                r'class="border-2 border-foreground bg-background-dark p-8"',
                re.IGNORECASE,
            ),
            'class="glass-card" style="max-width:800px;margin:3rem auto;text-align:left;"',
        ),
        (
            "Restore Foodle Be cta-button",
            re.compile(r'class="btn-primary px-8 py-4 font-bold"', re.IGNORECASE),
            'class="cta-button"',
        ),
        (
            "Restore Foodle Be footer",
            re.compile(
                r'<footer class="border-t-2 border-foreground py-10 px-6 bg-background-dark text-center">',
                re.IGNORECASE,
            ),
            '<footer style="text-align:center;padding:2rem;color:#52525b;font-size:0.875rem;">',
        ),

        # ── 30. Stray brutal-border class ─────────────────────────────────────
        (
            "Remove brutal-border class",
            re.compile(r'\bbrutal-border\b\s*', re.IGNORECASE),
            "",
        ),

        # ── 31. Stray brutal-shadow class ─────────────────────────────────────
        (
            "Remove brutal-shadow class",
            re.compile(r'\bbrutal-shadow\b\s*', re.IGNORECASE),
            "",
        ),

        # ── 32. Clean double spaces in class attrs ────────────────────────────
        (
            "Clean double spaces in class attrs",
            re.compile(r'(class="[^"]*?)  +', re.IGNORECASE),
            r'\1 ',
        ),
    ]


# ── Google Fonts injection helper ────────────────────────────────────────────

def inject_google_fonts(content: str, is_project_page: bool) -> tuple[str, bool]:
    """Inject Google Fonts <link> tags before </head> if not already there."""
    if "fonts.googleapis.com/css2?family=Inter" in content:
        return content, False
    # Inject before </head>
    content = content.replace("</head>", GOOGLE_FONTS_LINKS + "\n</head>", 1)
    return content, True


# ── Core file processor ───────────────────────────────────────────────────────

def process_file(filepath: str, filename: str, replacements: list,
                 is_project_page: bool = False) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    change_log = []

    # Inject Google Fonts
    content, injected = inject_google_fonts(content, is_project_page)
    if injected:
        change_log.append("  + Injected Google Fonts (Inter + Plus Jakarta Sans)")

    # Apply class transformations
    for desc, pattern, repl in replacements:
        new_content, n = pattern.subn(repl, content)
        if n > 0:
            change_log.append(f"  [x{n}] {desc}")
            content = new_content

    if content != original:
        newline = "\r\n" if is_project_page else "\r\n"
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print(f"\n[{filename}] -- {len(change_log)} change(s):")
        for entry in change_log:
            print(entry)
    else:
        print(f"\n[{filename}] -- Already up-to-date.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    replacements = make_replacements()

    # Process index.html
    index_path = os.path.join(ROOT_DIR, "index.html")
    if os.path.exists(index_path):
        process_file(index_path, "index.html", replacements, is_project_page=False)
    else:
        print("WARNING: index.html not found")

    # Process all project pages
    if os.path.exists(PROJECTS_DIR):
        html_files = sorted(f for f in os.listdir(PROJECTS_DIR) if f.endswith(".html"))
        for filename in html_files:
            process_file(
                os.path.join(PROJECTS_DIR, filename),
                filename,
                replacements,
                is_project_page=True,
            )
    else:
        print(f"WARNING: projects/ directory not found at {PROJECTS_DIR}")

    print("\n" + "=" * 70)
    print("Done. Run: npm run css:build && python build.py")


if __name__ == "__main__":
    main()
