"""
apply_project_styles.py
=======================
L3 Execution script — 3D Cinematic Dark design system propagation.

Migrates every HTML file under projects/ from the Premium Agency Light system
to the 3D Cinematic Dark system matching the redesigned index.html
(Syne + Manrope, deep space background #030712, glassmorphic card elements,
cyan #0ea5e9 neon glows, and interactive 3D tilt controls).

Idempotent: running multiple times produces the same result.
"""

import os
import re

PROJECTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

# ---------------------------------------------------------------------------
# New nav + header HTML fragments (shared across all project subpages)
# ---------------------------------------------------------------------------

NEW_HEAD_FONTS = """\
  <!-- Fonts: 3D Cinematic Dark -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">"""

NEW_HEAD_STYLE = """\
  <style>
    /* -- Design System Tokens ----------------------------------- */
    :root {
      --bg:         #030712;
      --surface:    rgba(255, 255, 255, 0.03);
      --muted:      #0b1329;
      --text:       #F8FAFC;
      --text-muted: #94A3B8;
      --accent:     #0ea5e9;
      --accent-h:   #0284C7;
      --border:     rgba(255, 255, 255, 0.08);
    }

    /* -- Base --------------------------------------------------- */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: 'Manrope', sans-serif;
      background: var(--bg);
      color: var(--text);
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }
    ::selection { background: var(--accent); color: #000; }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(to bottom, var(--accent), #818cf8);
        border-radius: 9999px;
        border: 2px solid var(--bg);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(to bottom, #0284c7, #6366f1);
    }

    /* -- Typography --------------------------------------------- */
    .font-syne   { font-family: 'Syne', sans-serif; }
    .font-manrope { font-family: 'Manrope', sans-serif; }

    /* -- Nav scroll shadow -------------------------------------- */
    .nav-scrolled {
      background-color: rgba(3, 7, 18, 0.75) !important;
      backdrop-filter: blur(16px);
      border-color: rgba(255, 255, 255, 0.08) !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    #main-nav { border-color: rgba(255, 255, 255, 0.05); }

    /* -- Mobile menu -------------------------------------------- */
    #mobile-menu { transform: translateX(100%); transition: transform .3s ease; background-color: rgba(3, 7, 18, 0.95); backdrop-filter: blur(20px); }
    #mobile-menu.open { transform: translateX(0); }

    /* -- Card base depth --------------------------------------- */
    .depth-card {
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.06);
      transition: all .3s cubic-bezier(0.25, 1, 0.5, 1);
    }
    .depth-card:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(14, 165, 233, 0.3) !important;
      box-shadow: 0 20px 45px rgba(14, 165, 233, 0.15);
      transform: translateY(-5px) scale(1.01);
    }

    /* -- 3D Tilt Card Base ---------------------------------------------- */
    .tilt-card {
        transform-style: preserve-3d;
        transition: transform 0.15s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .tilt-card:hover {
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }

    .glow-border-cyan:hover {
        border-color: rgba(14, 165, 233, 0.4);
        box-shadow: 0 0 25px rgba(14, 165, 233, 0.2);
    }

    /* -- Upgraded $1000 Premium Design System Extensions ----------------- */
    #scroll-progress {
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(to right, #0ea5e9, #818cf8);
        z-index: 100;
        width: 0%;
        transition: width 0.1s ease-out;
        box-shadow: 0 0 10px rgba(14, 165, 233, 0.6);
    }

    .magnetic-card {
        position: relative;
    }
    .magnetic-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1px;
        background: radial-gradient(
            350px circle at var(--mouse-x, 0px) var(--mouse-y, 0px),
            rgba(14, 165, 233, 0.35),
            transparent 50%
        );
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        z-index: 5;
        transition: opacity 0.4s ease;
        opacity: 0;
    }
    .magnetic-card:hover::before {
        opacity: 1;
    }

    /* -- Laser Glow Border Tracer ------------------------------------- */
    .laser-glow-wrapper {
        position: relative;
    }
    .laser-glow-border {
        position: absolute;
        inset: -1px; /* border thickness */
        pointer-events: none;
        border-radius: inherit;
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: 10;
        
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    .tilt-card:hover .laser-glow-border,
    .product-card:hover .laser-glow-border,
    .bento-item:hover .laser-glow-border,
    .depth-card:hover .laser-glow-border {
        opacity: 1;
    }
    .laser-glow-cyan-purple {
        background: repeating-conic-gradient(
            from calc(var(--start, 0) * 1deg) at 50% 50%,
            rgba(14, 165, 233, 1) 0%,
            rgba(129, 140, 248, 1) 15%,
            rgba(168, 85, 247, 0.95) 30%,
            transparent 50%,
            transparent 90%,
            rgba(14, 165, 233, 1) 100%
        );
    }
    .laser-glow-purple-cyan {
        background: repeating-conic-gradient(
            from calc(var(--start, 0) * 1deg) at 50% 50%,
            rgba(168, 85, 247, 1) 0%,
            rgba(129, 140, 248, 1) 15%,
            rgba(14, 165, 233, 0.95) 30%,
            transparent 50%,
            transparent 90%,
            rgba(168, 85, 247, 1) 100%
        );
    }

    /* -- Grid Beam Background ----------------------------------------- */
    .grid-beam-bg {
        position: absolute;
        inset: 0;
        background-image: 
            linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 60px 60px;
        background-position: center top;
        mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 100%);
        -webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 100%);
        pointer-events: none;
        z-index: 1;
    }
    .grid-beam-container {
        position: absolute;
        inset: 0;
        overflow: hidden;
        pointer-events: none;
        z-index: 2;
    }
    .grid-beam {
        position: absolute;
        background: linear-gradient(90deg, transparent, var(--accent, #0ea5e9), transparent);
        height: 1px;
        width: 150px;
        opacity: 0.5;
        animation: beam-move-horizontal 6s infinite linear;
    }
    .grid-beam-vertical {
        position: absolute;
        background: linear-gradient(180deg, transparent, rgba(168, 85, 247, 0.8), transparent);
        width: 1px;
        height: 150px;
        opacity: 0.5;
        animation: beam-move-vertical 8s infinite linear;
    }
    @keyframes beam-move-horizontal {
        0% { left: -150px; }
        100% { left: 100%; }
    }
    @keyframes beam-move-vertical {
        0% { top: -150px; }
        100% { top: 100%; }
    }

    /* -- Noise Overlay ------------------------------------------------- */
    .noise-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        opacity: 0.015;
        z-index: 9997;
        pointer-events: none;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    }

    /* -- Glare sheen effect on cards ----------------------------------- */
    .card-sheen {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at var(--sheen-x, 0%) var(--sheen-y, 0%), rgba(255, 255, 255, 0.08) 0%, transparent 60%);
        pointer-events: none;
        z-index: 3;
        transition: opacity 0.5s ease;
        opacity: 0;
        border-radius: inherit;
    }
    .tilt-card:hover .card-sheen {
        opacity: 1;
    }
  </style>"""

NEW_NAVBAR = """\
<div class="noise-overlay" aria-hidden="true"></div>

<div id="custom-context-menu" role="menu" aria-label="Quick Actions">
  <div class="context-menu-item" onclick="toggleParticles()">
    <span class="material-symbols-outlined text-sm">filter_vintage</span>
    <span>Toggle Particles</span>
  </div>
  <div class="context-menu-item" onclick="toggleSounds()">
    <span class="material-symbols-outlined text-sm">volume_up</span>
    <span id="sound-status-text">Enable Sounds</span>
  </div>
  <div class="context-menu-divider"></div>
  <div class="context-menu-item" onclick="copyEmail()">
    <span class="material-symbols-outlined text-sm">content_copy</span>
    <span>Copy Email</span>
  </div>
  <div class="context-menu-divider"></div>
  <div class="context-menu-item" onclick="window.location.href='../index.html#services'">
    <span class="material-symbols-outlined text-sm">code</span>
    <span>Services</span>
  </div>
  <div class="context-menu-item" onclick="window.location.href='../index.html#client-projects'">
    <span class="material-symbols-outlined text-sm">folder</span>
    <span>Portfolio</span>
  </div>
  <div class="context-menu-item" onclick="window.location.href='../index.html#contact'">
    <span class="material-symbols-outlined text-sm">mail</span>
    <span>Contact Us</span>
  </div>
</div>

<nav id="main-nav" class="fixed top-0 w-full z-50 bg-[#030712]/75 backdrop-blur-md border-b border-white/5 transition-all duration-300" role="navigation" aria-label="Main navigation">
  <div class="max-w-7xl mx-auto px-6 md:px-10 h-20 flex items-center justify-between">
    <a href="../index.html" class="flex items-center gap-3 group" aria-label="Dalvi Consultancy Homepage">
      <div class="w-9 h-9 rounded-lg bg-gradient-to-r from-[#0ea5e9] to-[#818cf8] flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(14,165,233,0.3)]">
        <img src="../logo.svg" alt="Dalvi Consultancy" class="w-7 h-7 object-contain brightness-0">
      </div>
      <span class="font-syne font-extrabold text-xl tracking-tight text-white group-hover:text-[#0ea5e9] transition-colors">Dalvi Consultancy</span>
    </a>
    <div class="hidden md:flex items-center gap-8">
      <a href="../index.html#services"        class="font-manrope font-medium text-sm text-slate-300 hover:text-[#0ea5e9] hover:-translate-y-0.5 transition-all duration-200">Services</a>
      <a href="../index.html#products"        class="font-manrope font-medium text-sm text-slate-300 hover:text-[#0ea5e9] hover:-translate-y-0.5 transition-all duration-200">Products</a>
      <a href="../index.html#client-projects" class="font-manrope font-medium text-sm text-slate-300 hover:text-[#0ea5e9] hover:-translate-y-0.5 transition-all duration-200">Our Work</a>
      
      <!-- Search Button Trigger -->
      <button onclick="toggleCommandPalette(true)" class="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 hover:border-white/20 text-slate-400 hover:text-white rounded-lg transition-all text-xs font-manrope cursor-pointer focus:outline-none" aria-label="Search or run commands">
        <span class="material-symbols-outlined text-base">search</span>
        <span>Search</span>
        <kbd class="hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] font-sans font-medium text-slate-500 bg-white/5 border border-white/10 rounded">Ctrl K</kbd>
      </button>

      <a href="../index.html#contact" class="ml-2 inline-flex items-center justify-center px-5 py-2.5 bg-gradient-to-r from-[#0ea5e9] to-[#818cf8] text-[#030712] font-manrope font-bold text-sm rounded-lg hover:shadow-[0_0_20px_rgba(14,165,233,0.4)] hover:-translate-y-0.5 transition-all duration-200 shadow-sm">Start a Project</a>
    </div>
    <button id="mobile-menu-btn" class="md:hidden p-2 text-slate-300 hover:text-white transition-colors" aria-label="Open menu">
      <span class="material-symbols-outlined text-2xl">menu</span>
    </button>
  </div>
</nav>
<!-- Mobile menu -->
<div id="mobile-menu" class="fixed inset-0 z-[60] flex flex-col items-center justify-center gap-8 md:hidden" aria-hidden="true">
  <button id="mobile-menu-close" class="absolute top-6 right-6 p-2 text-slate-300 hover:text-white transition-colors" aria-label="Close menu">
    <span class="material-symbols-outlined text-2xl">close</span>
  </button>
  <nav class="flex flex-col items-center gap-6 text-xl font-syne font-bold text-white">
    <a href="../index.html#services"        class="hover:text-[#0ea5e9] transition-colors">Services</a>
    <a href="../index.html#products"        class="hover:text-[#0ea5e9] transition-colors">Products</a>
    <a href="../index.html#client-projects" class="hover:text-[#0ea5e9] transition-colors">Our Work</a>
    
    <!-- Mobile Search Trigger -->
    <button onclick="toggleCommandPalette(true); document.getElementById('mobile-menu').classList.remove('open');" class="flex items-center justify-center gap-2 w-full max-w-[240px] px-4 py-2 bg-white/5 border border-white/10 text-slate-300 rounded-lg text-sm font-manrope">
      <span class="material-symbols-outlined text-lg">search</span>
      <span>Search...</span>
    </button>

    <a href="../index.html#contact" class="mt-4 inline-flex items-center justify-center px-8 py-3.5 bg-gradient-to-r from-[#0ea5e9] to-[#818cf8] text-[#030712] font-manrope font-bold text-base rounded-lg hover:shadow-[0_0_25px_rgba(14,165,233,0.5)] transition-all">Start a Project</a>
  </nav>
</div>

<!-- Command Palette Modal -->
<div id="command-palette" class="fixed inset-0 z-[100] bg-slate-950/70 backdrop-blur-md flex items-start justify-center pt-[10vh] px-4" aria-hidden="true" role="dialog" aria-modal="true">
  <!-- Click outside overlay to close -->
  <div class="absolute inset-0 cursor-default" onclick="toggleCommandPalette(false)"></div>
  
  <div class="relative w-full max-w-2xl bg-[#090f1d]/95 border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[70vh]">
    <!-- Search Input Header -->
    <div class="flex items-center gap-3 px-4 py-3.5 border-b border-white/10">
      <span class="material-symbols-outlined text-slate-400 text-xl select-none">search</span>
      <input type="text" id="command-palette-input" class="w-full bg-transparent text-white border-0 outline-none placeholder-slate-500 text-sm font-manrope focus:ring-0 focus:outline-none" placeholder="Search pages, actions, settings..." autocomplete="off" spellcheck="false">
      <kbd class="hidden sm:inline-flex items-center px-1.5 py-0.5 text-[9px] font-sans font-medium text-slate-500 bg-white/5 border border-white/10 rounded select-none">ESC</kbd>
    </div>
    
    <!-- Command List -->
    <div id="command-palette-list" class="flex-1 overflow-y-auto py-2 pr-1" role="listbox">
      <!-- Dynamically filled list -->
    </div>
    
    <!-- Footer -->
    <div class="flex items-center justify-between px-4 py-2 border-t border-white/5 bg-slate-950/40 text-[10px] text-slate-500 select-none">
      <div class="flex items-center gap-2">
        <span class="flex items-center gap-1"><kbd class="px-1 py-0.5 bg-white/5 border border-white/10 rounded">↑↓</kbd> Navigate</span>
        <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded">Enter</kbd> Select</span>
      </div>
      <div>
        <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 bg-white/5 border border-white/10 rounded">Esc</kbd> Close</span>
      </div>
    </div>
  </div>
</div>"""

NEW_FOOTER = """\
<footer class="bg-[#090f1d]/50 border-t border-white/5 relative z-10 mt-20">
  <div class="max-w-7xl mx-auto px-6 md:px-10 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
    <a href="../index.html" class="font-manrope text-sm text-slate-400 hover:text-[#0ea5e9] transition-colors">&larr; Back to Dalvi Consultancy</a>
    <p class="font-manrope text-sm text-slate-400">&copy; 2025 Dalvi Consultancy. Built in Pune, India.</p>
  </div>
</footer>"""

NEW_SCRIPT = """\
<script>
// -- Web Audio API UI Sound Synthesizer --------------------------------
let soundEnabled = false;
let audioCtx = null;

function playSound(type) {
  if (!soundEnabled) return;
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    if (type === 'hover') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(850, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1400, audioCtx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.01, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.04);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.04);
    } else if (type === 'click') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(520, audioCtx.currentTime);
      osc.frequency.setValueAtTime(1150, audioCtx.currentTime + 0.03);
      gain.gain.setValueAtTime(0.02, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.07);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.07);
    }
  } catch (e) {
    console.warn("Audio Context error:", e);
  }
}

// Add hover states and play sound on mouse event triggers
function setupHoverSounds() {
  const hoverables = document.querySelectorAll('a, button, input, textarea, select, .tilt-card, .magnetic-card, .faq-trigger, .contact-icon, .social-icon, .context-menu-item');
  hoverables.forEach(item => {
    if (item.dataset.hoverSoundBound) return;
    item.dataset.hoverSoundBound = "true";
    
    item.addEventListener('mouseenter', () => {
      playSound('hover');
    });
    item.addEventListener('click', () => {
      playSound('click');
    });
  });
}
setupHoverSounds();
setInterval(setupHoverSounds, 2000);

// -- Custom Context Menu ----------------------------------------------
const contextMenu = document.getElementById('custom-context-menu');
window.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  if (!contextMenu) return;
  contextMenu.style.left = `${e.clientX}px`;
  contextMenu.style.top = `${e.clientY}px`;
  contextMenu.classList.add('visible');
  playSound('hover');
});

window.addEventListener('click', (e) => {
  if (contextMenu && !contextMenu.contains(e.target)) {
    contextMenu.classList.remove('visible');
  }
});

let particlesEnabled = true;
function toggleParticles() {
  particlesEnabled = !particlesEnabled;
  if (contextMenu) contextMenu.classList.remove('visible');
}

function toggleSounds() {
  soundEnabled = !soundEnabled;
  const textEl = document.getElementById('sound-status-text');
  if (textEl) {
    textEl.textContent = soundEnabled ? 'Disable Sounds' : 'Enable Sounds';
  }
  if (contextMenu) contextMenu.classList.remove('visible');
  if (soundEnabled) {
    playSound('click');
  }
}

function copyEmail() {
  navigator.clipboard.writeText('consultancy@dalvigroup.co.in').then(() => {
    alert('Agency email copied to clipboard!');
  });
  if (contextMenu) contextMenu.classList.remove('visible');
}

const nav = document.getElementById('main-nav');
if (nav) {
  window.addEventListener('scroll', () => { nav.classList.toggle('nav-scrolled', window.scrollY > 20); });
}
const menuBtn = document.getElementById('mobile-menu-btn');
const menuClose = document.getElementById('mobile-menu-close');
const menu = document.getElementById('mobile-menu');
const toggleMenu = () => { menu.classList.toggle('open'); menu.setAttribute('aria-hidden', String(!menu.classList.contains('open'))); };
if (menuBtn) menuBtn.addEventListener('click', toggleMenu);
if (menuClose) menuClose.addEventListener('click', toggleMenu);
if (menu) menu.querySelectorAll('a').forEach(a => a.addEventListener('click', toggleMenu));

// -- Scroll progress bar indicator ------------------------------------
window.addEventListener('scroll', () => {
  const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
  const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  const scrolled = (winScroll / height) * 100;
  const progressBar = document.getElementById('scroll-progress');
  if (progressBar) {
    progressBar.style.width = scrolled + '%';
  }
});

// -- Magnetic Mouse Spotlight Glow Tracking --------------------------
document.querySelectorAll('.magnetic-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty('--mouse-x', `${x}px`);
    card.style.setProperty('--mouse-y', `${y}px`);
  });
});

// -- 3D Tilt + Card Glare Sheen Effect ---------------------------------
const tiltCards = document.querySelectorAll('.tilt-card');
tiltCards.forEach(card => {
  card.style.position = 'relative';
  card.style.overflow = 'hidden';
  
  let sheen = card.querySelector('.card-sheen');
  if (!sheen) {
    sheen = document.createElement('div');
    sheen.className = 'card-sheen';
    card.appendChild(sheen);
  }
  
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const pctX = (x / rect.width) * 100;
    const pctY = (y / rect.height) * 100;
    card.style.setProperty('--sheen-x', `${pctX}%`);
    card.style.setProperty('--sheen-y', `${pctY}%`);
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const panX = ((x - centerX) / centerX) * 8;
    const panY = ((y - centerY) / centerY) * 8;
    const rotateX = ((centerY - y) / centerY) * 8;
    const rotateY = ((x - centerX) / centerX) * 8;
    
    card.style.transform = `perspective(1000px) translate3d(${panX}px, ${panY}px, 0) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
  });
  
  card.style.transformStyle = 'preserve-3d';
  
  card.addEventListener('mouseleave', () => {
    card.style.transform = `perspective(1000px) translate3d(0px, 0px, 0) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
  });
});

// -- Scroll Reveal with Staggered Sequencing --------------------------
const revealElements = document.querySelectorAll('main > section, main > article, .tilt-card');
const revealObserver = new IntersectionObserver((entries, observer) => {
  let staggerDelay = 0;
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      el.style.transitionDelay = `${staggerDelay}ms`;
      el.classList.add('opacity-100', 'translate-y-0');
      el.classList.remove('opacity-0', 'translate-y-8');
      staggerDelay += 75;
      observer.unobserve(el);
    }
  });
  setTimeout(() => { staggerDelay = 0; }, 150);
}, { threshold: 0.08 });

revealElements.forEach(el => {
  el.classList.add('transition-all', 'duration-700', 'transform', 'opacity-0', 'translate-y-8');
  revealObserver.observe(el);
});

// -- Laser Glow Border Tracers & Background Grid Beams -----------------
function initLaserGlows() {
  const cards = document.querySelectorAll('.tilt-card, .product-card, .bento-item, .depth-card');
  cards.forEach(card => {
    if (card.querySelector('.laser-glow-border')) return;
    
    const border = document.createElement('div');
    border.className = 'laser-glow-border';
    
    if (card.classList.contains('glow-border-purple') || card.classList.contains('bg-rose-600/20')) {
      border.classList.add('laser-glow-purple-cyan');
    } else {
      border.classList.add('laser-glow-cyan-purple');
    }
    
    card.appendChild(border);
    
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const mouseX = e.clientX;
      const mouseY = e.clientY;
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const targetAngle = (180 * Math.atan2(mouseY - centerY, mouseX - centerX)) / Math.PI + 90;
      card.style.setProperty('--start', String(targetAngle));
    });
  });
}

function initGridBeams() {
  if (document.querySelector('.grid-beam-bg')) return;
  const header = document.querySelector('header') || document.querySelector('main');
  if (!header) return;
  
  const bg = document.createElement('div');
  bg.className = 'grid-beam-bg';
  bg.setAttribute('aria-hidden', 'true');
  
  const container = document.createElement('div');
  container.className = 'grid-beam-container';
  container.setAttribute('aria-hidden', 'true');
  container.innerHTML = `
    <div class="grid-beam" style="top: 60px; animation-delay: 0s; animation-duration: 6s;"></div>
    <div class="grid-beam" style="top: 180px; animation-delay: 2s; animation-duration: 8s;"></div>
    <div class="grid-beam" style="top: 300px; animation-delay: 4s; animation-duration: 7s;"></div>
    <div class="grid-beam-vertical" style="left: 120px; animation-delay: 1s; animation-duration: 9s;"></div>
    <div class="grid-beam-vertical" style="left: 480px; animation-delay: 3s; animation-duration: 10s;"></div>
    <div class="grid-beam-vertical" style="left: 840px; animation-delay: 5s; animation-duration: 11s;"></div>
  `;
  
  header.style.position = 'relative';
  header.insertBefore(bg, header.firstChild);
  header.insertBefore(container, header.firstChild);
}

initLaserGlows();
initGridBeams();
setInterval(initLaserGlows, 2000);

// ── Command Palette JS ────────────────────────────────────────────────
const commands = [
  // Navigation
  { title: "Services", category: "Navigation", url: "index.html#services", icon: "code" },
  { title: "Products", category: "Navigation", url: "index.html#products", icon: "widgets" },
  { title: "Our Work", category: "Navigation", url: "index.html#client-projects", icon: "folder_open" },
  { title: "Technologies", category: "Navigation", url: "index.html#tech-stack", icon: "psychology" },
  { title: "Contact Us", category: "Navigation", url: "index.html#contact", icon: "mail" },
  { title: "Home Page", category: "Navigation", url: "index.html", icon: "home" },
  
  // Case Studies
  { title: "Berrybash (Custom E-commerce)", category: "Case Studies", url: "projects/berrybash.html", icon: "shopping_cart" },
  { title: "Buon Cibo (Restaurant POS)", category: "Case Studies", url: "projects/buoncibo.html", icon: "restaurant" },
  { title: "RTO Buddy (Driving License Platform)", category: "Case Studies", url: "projects/rtobuddy.html", icon: "description" },
  { title: "SMPG (School Management System)", category: "Case Studies", url: "projects/smpg.html", icon: "school" },
  { title: "Dirt Shack (E-commerce Store)", category: "Case Studies", url: "projects/dirtshack.html", icon: "eco" },
  { title: "Millet Bee (D2C Brand Website)", category: "Case Studies", url: "projects/milletbee.html", icon: "spa" },
  { title: "Boundless Generosity (Non-profit)", category: "Case Studies", url: "projects/boundlessgenerosity.html", icon: "volunteer_activism" },
  { title: "Foodlebe (Food Delivery API)", category: "Case Studies", url: "projects/foodlebe.html", icon: "delivery_dining" },
  { title: "Playverse (Gaming Community)", category: "Case Studies", url: "projects/playverse.html", icon: "sports_esports" },
  { title: "VPTC (Video Production Portal)", category: "Case Studies", url: "projects/vptc.html", icon: "video_camera_back" },
  
  // Actions / Settings
  { title: "Toggle Background Particles", category: "Settings", action: "toggleParticles", icon: "filter_vintage" },
  { title: "Toggle Sound Synthesizer", category: "Settings", action: "toggleSounds", icon: "volume_up" },
  { title: "Copy Agency Email", category: "Settings", action: "copyEmail", icon: "content_copy" }
];

let commandPaletteVisible = false;
let selectedCommandIndex = 0;
let filteredCommands = [];

function resolveUrl(url) {
  const isProjectSubpage = window.location.pathname.includes('/projects/') || window.location.pathname.endsWith('.html') && !window.location.pathname.endsWith('index.html') && !window.location.pathname.includes('/dist/index.html');
  if (!isProjectSubpage) return url;
  if (url.startsWith('projects/')) {
    return url.replace('projects/', '');
  }
  if (url.startsWith('index.html')) {
    return '../' + url;
  }
  return url;
}

function toggleCommandPalette(force) {
  const palette = document.getElementById('command-palette');
  const input = document.getElementById('command-palette-input');
  if (!palette) return;
  
  if (force !== undefined) {
    commandPaletteVisible = force;
  } else {
    commandPaletteVisible = !commandPaletteVisible;
  }
  
  if (commandPaletteVisible) {
    palette.classList.add('visible');
    palette.setAttribute('aria-hidden', 'false');
    input.value = '';
    input.focus();
    renderCommands('');
    if (typeof playSound === 'function') {
      playSound('click');
    }
  } else {
    palette.classList.remove('visible');
    palette.setAttribute('aria-hidden', 'true');
    input.blur();
  }
}

function renderCommands(query) {
  const list = document.getElementById('command-palette-list');
  if (!list) return;
  list.innerHTML = '';
  
  const q = query.toLowerCase().trim();
  
  filteredCommands = commands.filter(cmd => 
    cmd.title.toLowerCase().includes(q) || 
    cmd.category.toLowerCase().includes(q)
  );
  
  if (filteredCommands.length === 0) {
    list.innerHTML = `<div class="px-4 py-8 text-center text-slate-500 text-sm">No commands found for "${query}"</div>`;
    selectedCommandIndex = 0;
    return;
  }
  
  if (selectedCommandIndex >= filteredCommands.length) {
    selectedCommandIndex = 0;
  }
  
  let currentCategory = "";
  filteredCommands.forEach((cmd, idx) => {
    if (cmd.category !== currentCategory) {
      currentCategory = cmd.category;
      const groupHeader = document.createElement('div');
      groupHeader.className = 'command-group-title';
      groupHeader.textContent = currentCategory;
      list.appendChild(groupHeader);
    }
    
    const item = document.createElement('div');
    item.className = `command-item ${idx === selectedCommandIndex ? 'selected' : ''}`;
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', idx === selectedCommandIndex ? 'true' : 'false');
    
    const iconSpan = `<span class="material-symbols-outlined text-slate-400 mr-3 text-lg">${cmd.icon || 'star'}</span>`;
    
    let rightBadge = '';
    if (cmd.category === 'Settings') {
      rightBadge = `<span class="text-[10px] text-slate-500 bg-white/5 px-2 py-0.5 rounded border border-white/5">Action</span>`;
    } else if (cmd.category === 'Case Studies') {
      rightBadge = `<span class="text-[10px] text-[#0ea5e9]/70 bg-[#0ea5e9]/5 px-2 py-0.5 rounded border border-[#0ea5e9]/10">Project</span>`;
    } else {
      rightBadge = `<span class="text-[10px] text-slate-500 select-none">&rarr;</span>`;
    }
    
    item.innerHTML = `
      <div class="flex items-center">
        ${iconSpan}
        <span class="font-manrope">${cmd.title}</span>
      </div>
      ${rightBadge}
    `;
    
    item.addEventListener('click', () => {
      selectedCommandIndex = idx;
      executeSelectedCommand();
    });
    
    item.addEventListener('mouseenter', () => {
      selectedCommandIndex = idx;
      const items = list.querySelectorAll('.command-item');
      items.forEach((el, elIdx) => {
        if (elIdx === idx) {
          el.classList.add('selected');
        } else {
          el.classList.remove('selected');
        }
      });
      if (typeof playSound === 'function') {
        playSound('hover');
      }
    });
    
    list.appendChild(item);
  });
}

function navigateCommands(direction) {
  if (filteredCommands.length === 0) return;
  
  selectedCommandIndex += direction;
  if (selectedCommandIndex < 0) {
    selectedCommandIndex = filteredCommands.length - 1;
  } else if (selectedCommandIndex >= filteredCommands.length) {
    selectedCommandIndex = 0;
  }
  
  const list = document.getElementById('command-palette-list');
  if (!list) return;
  
  const items = list.querySelectorAll('.command-item');
  items.forEach((el, idx) => {
    if (idx === selectedCommandIndex) {
      el.classList.add('selected');
      el.scrollIntoView({ block: 'nearest' });
    } else {
      el.classList.remove('selected');
    }
  });
  
  if (typeof playSound === 'function') {
    playSound('hover');
  }
}

function executeSelectedCommand() {
  if (selectedCommandIndex < 0 || selectedCommandIndex >= filteredCommands.length) return;
  const cmd = filteredCommands[selectedCommandIndex];
  
  toggleCommandPalette(false);
  
  if (typeof playSound === 'function') {
    playSound('click');
  }
  
  if (cmd.action) {
    if (cmd.action === 'toggleParticles' && typeof toggleParticles === 'function') {
      toggleParticles();
    } else if (cmd.action === 'toggleSounds' && typeof toggleSounds === 'function') {
      toggleSounds();
    } else if (cmd.action === 'copyEmail' && typeof copyEmail === 'function') {
      copyEmail();
    }
  } else if (cmd.url) {
    const targetUrl = resolveUrl(cmd.url);
    if (targetUrl.includes('#') && (window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/'))) {
      const hash = targetUrl.split('#')[1];
      const el = document.getElementById(hash);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
        window.history.pushState(null, null, `#${hash}`);
        return;
      }
    }
    window.location.href = targetUrl;
  }
}

// Bind window keydown and input events
window.addEventListener('keydown', (e) => {
  const isK = e.key === 'k' || e.key === 'K';
  if ((e.ctrlKey || e.metaKey) && isK) {
    e.preventDefault();
    toggleCommandPalette();
  }
  
  const palette = document.getElementById('command-palette');
  if (palette && palette.classList.contains('visible')) {
    if (e.key === 'Escape') {
      e.preventDefault();
      toggleCommandPalette(false);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      navigateCommands(1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      navigateCommands(-1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      executeSelectedCommand();
    }
  }
});

function initCommandPaletteEvents() {
  const cpInput = document.getElementById('command-palette-input');
  if (cpInput) {
    cpInput.addEventListener('input', (e) => {
      selectedCommandIndex = 0;
      renderCommands(e.target.value);
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCommandPaletteEvents);
} else {
  initCommandPaletteEvents();
}
</script>"""

# ---------------------------------------------------------------------------

def make_replacements():
    return [
        # -- 1. Replace Style tag containing light theme tokens --------------
        (
            "Replace style block with 3D Dark style block",
            re.compile(r'<style>.*?\-\-bg:\s*#FFFFFF;.*?</style>', re.DOTALL | re.IGNORECASE),
            NEW_HEAD_STYLE,
        ),

        # -- 2. Replace Navbar + Mobile menu up to <main ---------------------
        (
            "Replace Navbar + Mobile menu",
            re.compile(r'<nav id="main-nav".*?(?=<main)', re.DOTALL | re.IGNORECASE),
            NEW_NAVBAR + "\n",
        ),

        # -- 3. Replace <main> tag to use dark background -------------------
        (
            "Replace main tag bg-white with dark class",
            re.compile(r'<main class="pt-28 bg-white">', re.IGNORECASE),
            '<main class="pt-28 bg-[#030712] relative overflow-hidden">',
        ),

        # -- 4. Replace badge styles -----------------------------------------
        (
            "Replace badge styles with dark/neon style",
            re.compile(r'class="inline-block px-3 py-1 bg-\[#EFF6FF\] border border-\[#BFDBFE\] text-\[#0369A1\] text-xs font-manrope font-bold uppercase tracking-widest rounded-full mb-6"', re.IGNORECASE),
            'class="inline-block px-3 py-1 bg-white/2 border border-white/10 text-[#0ea5e9] text-xs font-manrope font-bold uppercase tracking-widest rounded-full mb-6"',
        ),

        # -- 5. Replace Heading text colors (#0F172A -> white) ---------------
        (
            "Replace text-[#0F172A] with text-white",
            re.compile(r'text-\[#0F172A\]', re.IGNORECASE),
            "text-white",
        ),

        # -- 6. Replace Subtitle/Paragraph text colors (#475569 -> text-slate-300)
        (
            "Replace text-[#475569] with text-slate-300",
            re.compile(r'text-\[#475569\]', re.IGNORECASE),
            "text-slate-300",
        ),

        # -- 7. Replace accent colors (#0369A1 -> #0ea5e9) -------------------
        (
            "Replace text-[#0369A1] with text-[#0ea5e9]",
            re.compile(r'text-\[#0369A1\]', re.IGNORECASE),
            "text-[#0ea5e9]",
        ),
        (
            "Replace hover:text-[#0369A1] with hover:text-[#0ea5e9]",
            re.compile(r'hover:text-\[#0369A1\]', re.IGNORECASE),
            "hover:text-[#0ea5e9]",
        ),
        (
            "Replace border-[#0369A1] with border-[#0ea5e9]/40",
            re.compile(r'border-\[#0369A1\]', re.IGNORECASE),
            "border-[#0ea5e9]/40",
        ),
        (
            "Replace hover:border-[#0369A1] with hover:border-[#0ea5e9]/60",
            re.compile(r'hover:border-\[#0369A1\]', re.IGNORECASE),
            "hover:border-[#0ea5e9]/60",
        ),
        (
            "Replace hover:bg-[#EFF6FF] with hover:bg-[#0ea5e9]/10",
            re.compile(r'hover:bg-\[#EFF6FF\]', re.IGNORECASE),
            "hover:bg-[#0ea5e9]/10",
        ),
        (
            "Replace bg-[#0369A1] with bg-gradient-to-r from-[#0ea5e9] to-[#818cf8]",
            re.compile(r'bg-\[#0369A1\]', re.IGNORECASE),
            "bg-gradient-to-r from-[#0ea5e9] to-[#818cf8]",
        ),

        # -- 8. Replace strong tags in body content to stand out -------------
        (
            "Replace strong tags text-[#0F172A] with text-white font-semibold",
            re.compile(r'<strong class="text-\[#0F172A\]">', re.IGNORECASE),
            '<strong class="text-white font-semibold">',
        ),
        (
            "Replace strong tags text-white with text-white font-semibold",
            re.compile(r'<strong class="text-white">', re.IGNORECASE),
            '<strong class="text-white font-semibold">',
        ),

        # -- 9. Replace About section container ------------------------------
        (
            "Replace about card bg-white with glassmorphic container",
            re.compile(r'class="bg-white rounded-2xl border border-\[#E2E8F0\] p-10 shadow-sm"', re.IGNORECASE),
            'class="bg-white/2 border border-white/5 backdrop-blur-md rounded-2xl p-10 shadow-lg"',
        ),

        # -- 10. Replace Feature cards (added magnetic-card!) ----------------
        (
            "Replace feature cards with dark glass/tilt/magnetic cards",
            re.compile(r'class="group p-6 rounded-2xl border border-\[#E2E8F0\] bg-white hover:border-\[#0369A1\] hover:-translate-y-1 hover:shadow-lg hover:shadow-\[#0369A1\]/5 transition-all duration-300"', re.IGNORECASE),
            'class="group p-6 rounded-2xl border border-white/5 bg-white/2 hover:border-[#0ea5e9]/40 hover:-translate-y-1 hover:shadow-lg hover:shadow-[#0ea5e9]/10 transition-all duration-300 tilt-card magnetic-card"',
        ),

        # -- 11. Replace Related project links (added magnetic-card!) --------
        (
            "Replace related project link cards with dark glass/tilt/magnetic cards",
            re.compile(r'class="p-6 rounded-2xl border border-\[#E2E8F0\] bg-white hover:border-\[#0369A1\] hover:-translate-y-1 hover:shadow-md transition-all duration-300 block"', re.IGNORECASE),
            'class="p-6 rounded-2xl border border-white/5 bg-white/2 hover:border-[#0ea5e9]/40 hover:-translate-y-1 hover:shadow-md hover:shadow-[#0ea5e9]/5 transition-all duration-300 tilt-card magnetic-card block"',
        ),

        # -- 12. Replace Icon colors -----------------------------------------
        (
            "Replace icon color classes",
            re.compile(r'class="material-symbols-outlined text-3xl text-\[#0369A1\] mb-4"', re.IGNORECASE),
            'class="material-symbols-outlined text-3xl text-[#0ea5e9] mb-4"',
        ),
        (
            "Replace general icon color classes",
            re.compile(r'class="material-symbols-outlined text-\[#0369A1\]"', re.IGNORECASE),
            'class="material-symbols-outlined text-[#0ea5e9]"',
        ),

        # -- 13. Replace CTA container ---------------------------------------
        (
            "Replace CTA container to dark gradient card",
            re.compile(r'class="bg-\[#F8FAFC\] rounded-2xl border border-\[#E2E8F0\] p-10 text-center"', re.IGNORECASE),
            'class="bg-gradient-to-br from-[#090f1d] to-[#030712] rounded-2xl border border-white/5 p-10 text-center relative overflow-hidden"',
        ),

        # -- 14. Replace CTA buttons -----------------------------------------
        (
            "Replace CTA primary button",
            re.compile(r'class="btn-primary px-8 py-4 rounded-2xl flex items-center gap-2"', re.IGNORECASE),
            'class="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[#0ea5e9] to-[#818cf8] text-[#030712] font-manrope font-extrabold rounded-lg hover:shadow-[0_0_20px_rgba(14,165,233,0.4)] hover:-translate-y-0.5 transition-all duration-200"',
        ),
        (
            "Replace CTA ghost button",
            re.compile(r'class="btn-ghost px-8 py-4 rounded-2xl"', re.IGNORECASE),
            'class="inline-flex items-center justify-center px-8 py-4 border-2 border-[#0ea5e9]/40 text-[#0ea5e9] hover:bg-[#0ea5e9]/10 font-manrope font-extrabold rounded-lg transition-all duration-200"',
        ),
        (
            "Replace inline bg-primary button in SMPG CTA",
            re.compile(r'class="inline-flex px-8 py-4 bg-primary text-white font-bold rounded-2xl hover:scale-105 transition-transform items-center gap-2"', re.IGNORECASE),
            'class="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-[#0ea5e9] to-[#818cf8] text-[#030712] font-manrope font-extrabold rounded-lg hover:shadow-[0_0_20px_rgba(14,165,233,0.4)] hover:-translate-y-0.5 transition-all duration-200"',
        ),

        # -- 15. Replace image decoration corners ----------------------------
        (
            "Replace image decoration corners color to accent",
            re.compile(r'bg-slate-200 bg-\[#CBD5E1\]', re.IGNORECASE),
            'bg-[#0ea5e9]/20',
        ),

        # -- 16. Replace Footer ----------------------------------------------
        (
            "Replace Footer with Dark footer",
            re.compile(r'<footer class="border-t border-\[#E2E8F0\] bg-white mt-20">.*?</footer>', re.DOTALL | re.IGNORECASE),
            NEW_FOOTER,
        ),

        # -- 17. Replace Script tag at the bottom ----------------------------
        (
            "Replace scroll script block with 3D Dark script",
            re.compile(r'</footer>\s*<script>.*?</script>', re.DOTALL | re.IGNORECASE),
            "</footer>\n" + NEW_SCRIPT,
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

    # Ensure <html> tag does NOT have light class or other theme triggers
    content = re.sub(r'<html([^>]*)\bclass="[^"]*light[^"]*"', r'<html\1', content)

    # Ensure styles.css is linked with relative path
    if '../styles.css' not in content:
        content = content.replace('</head>', '  <link rel="stylesheet" href="../styles.css">\n</head>', 1)
        change_log.append("  ✔ Added ../styles.css link")

    # Add scroll progress indicator right after body starts
    if 'id="scroll-progress"' not in content:
        content = content.replace('<body>', '<body>\n\n<div id="scroll-progress" aria-hidden="true"></div>\n', 1)
        change_log.append("  ✔ Injected scroll progress bar")

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
    print(f"3D Cinematic Dark propagation -> {len(html_files)} file(s) in {PROJECTS_DIR}")
    print("=" * 70)

    for filename in html_files:
        process_file(os.path.join(PROJECTS_DIR, filename), filename, replacements)

    print("\n" + "=" * 70)
    print("Done. Run `python build.py` to rebuild.")


if __name__ == "__main__":
    main()
