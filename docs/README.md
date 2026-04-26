# Poker Chips Reps Counter — PWA

A standalone, installable web app for counting reps with poker-chip-styled buttons. Tap chips (+1, +3, +5, +10) to log reps; track rounds, totals, and history. Works fully offline.

## Features

- Manual rep counter with 4 chip denominations
- Round tracking with full history
- Undo / reset controls with haptic feedback
- Persistent state via `localStorage`
- Installable on iOS, Android, and desktop
- 100% offline after first load

## Live Demo

https://prokashevr.github.io/exercise_counter/

## Development

Pure static site — no build step.

```bash
# Serve locally from repo root
cd docs
python3 -m http.server 8000
# Open http://localhost:8000
```

For service-worker testing, use `localhost` (HTTPS not required) or deploy to Pages.

## Project Structure

```
docs/
├── index.html              # App shell
├── styles.css              # Extracted styles
├── app.js                  # Counter logic + SW registration
├── sw.js                   # Service worker (cache-first, same-origin)
├── manifest.webmanifest    # PWA manifest
├── generate_icons.py       # Regenerates icons via OpenCV
└── icons/
    ├── icon-192.png        # Standard
    ├── icon-512.png        # Standard
    ├── icon-maskable.png   # Maskable (Android adaptive)
    └── apple-touch-icon.png
```

All paths inside the app are relative (`./`), so it runs correctly under any subpath — including `https://prokashevr.github.io/exercise_counter/`.

To regenerate icons after editing `generate_icons.py`:

```bash
python3 docs/generate_icons.py
```

(Requires `numpy` and `opencv-python`.)

## Deployment (GitHub Pages)

1. Push the `docs/` folder to `master`.
2. Repo → **Settings → Pages**.
3. **Source:** Deploy from a branch.
4. **Branch:** `master`, **Folder:** `/docs`.
5. App goes live at `https://<user>.github.io/exercise_counter/`.

For a custom domain or build pipeline, add a workflow at `.github/workflows/deploy-pwa.yml`.

## PWA Checklist

- [x] `manifest.webmanifest` linked in `<head>`
- [x] Service worker registered, caches shell on install
- [x] Icons: 192, 512, maskable, apple-touch
- [x] `theme-color` and `apple-touch-icon` meta tags
- [x] iOS standalone meta tags
- [ ] HTTPS — provided by GitHub Pages on deploy
- [ ] Lighthouse PWA audit ≥ 90 — verify after deploy

## License

Same as parent repo.
