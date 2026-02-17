# Deployment & Local Development Guide

## Prerequisites
- **Node.js** (for Tailwind CSS)
- **Python 3.x** (for build script)

## Local Development
To work on the site locally:

1.  **Install Dependencies** (First time only):
    ```bash
    npm install
    ```

2.  **Start CSS Watcher** (In a separate terminal):
    ```bash
    npm run dev
    ```
    *This watches `src/input.css` and updates `styles.css` automatically.*

3.  **Preview Site**:
    ```bash
    npx serve .
    ```

## Building for Production
Before pushing to GitHub, you **MUST** run the build script. This generates the optimized `live/` folder.

1.  **Run Build**:
    ```bash
    npm run build
    ```
    *(Or run `python build.py` directly if you don't need to rebuild CSS)*

    **What this does:**
    - Minifies HTML, CSS, and JS.
    - Generates `sitemap.xml` and `robots.txt`.
    - Generates `llms.txt` for AI crawlers.
    - Outputs everything to the `live/` directory.

2.  **Verify**:
    Check the `live/` folder to ensure all files are present and minified.

## Deployment (Cloudflare Pages)
The site is hosted on Cloudflare Pages, connected to the GitHub repository.

**Configuration:**
- **Build Command:** `(Leave Empty)`
    *   *Reason:* We commit the built assets in `live/` directly to GitHub, so Cloudflare doesn't need to build anything.
- **Build Output Directory:** `live`
    *   *Reason:* This serves the optimized files from the `live` folder.

## Workflow Summary
1.  Make changes.
2.  Run `npm run build`.
3.  Commit and Push:
    ```bash
    git add .
    git commit -m "update: description of changes"
    git push
    ```
