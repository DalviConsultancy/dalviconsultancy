# The Antigravity Architect: System Directives

## 1. The 3-Layer Mandate
All operations must strictly adhere to the following architectural stratification:

### L1: Directives (Strategy)
- **Role:** High-level decision making, system constraints, and architectural patterns.
- **Location:** `AGENTS.md`, `task.md`, `implementation_plan.md`
- **Output:** Clear, bounded instructions for L2.

### L2: Orchestration (Tactics)
- **Role:** Connecting components, managing workflow state, and bridging Strategy with Execution.
- **Location:** `scripts/`, `build.py`
- **Output:** Deterministic command sequences.

### L3: Execution (Physics)
- **Role:** The metal. Running code, moving bytes, compiling assets.
- **Location:** `src/`, `live/`, `assets/`
- **Constraint:** Must be automatable. If it requires a mouse, it's wrong.

---

## 2. Engineering & Design Standards

### Engineering
- **Functional Purity:** Side effects should be isolated.
- **Single Source of Truth:** Data must live in *one* place. Reference it, don't duplicate it.
- **Security:** Sanitize all inputs. Assume hostile environment.
- **Idempotency:** Scripts must run safely multiple times without changing the result after the first success.

### UX/UI
- **Ruthless Minimalism:** Remove everything that doesn't support the user's primary goal.
- **Feedback:** Every interaction (hover, click, focus) must provide immediate, perceptible feedback.
- **Performance:** < 100ms Time-to-Interactive. Use `live/` for production.

---

## 3. Directory & Production Standards

| Directory | Purpose | Constraint |
|:---|:---|:---|
| `/src` | Source Code | Raw, unoptimized human-readable code. |
| `/live` | Production | **MANDATORY**. Minified, optimized, SEO-ready. |
| `/assets` | Media | Source media files. |
| `/directives` | SOPs | Strategic documentation. |
| `/execution` | Scripts | Python/Node scripts for automation. |

**FFmpeg Standard:**
All media must be processed via FFmpeg.
- **Images:** WebP format, stripped metadata.
- **Video:** H.264/AAC or WebM, optimized bitrate.

---

## 4. Workflows & Automation
- **Deployment:** `python build.py` -> Push to GitHub -> Cloudflare Pages (Output: `live/`).
- **SEO:** handled by `build.py` (sitemap, robots, llms.txt).
- **CSS:** `npm run dev` (Tailwind JIT).

*Code Over Conversation.*