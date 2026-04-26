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

https://<your-username>.github.io/exercise_counter/

## Development

Pure static site — no build step.

```bash
# Serve locally
cd pwa
python3 -m http.server 8000
# Open http://localhost:8000
```

For service-worker testing, use `localhost` (HTTPS not required) or deploy to Pages.

## Project Structure

```
pwa/
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

To regenerate icons after editing `generate_icons.py`:

```bash
python3 pwa/generate_icons.py
```

(Requires `numpy` and `opencv-python`.)

## Deployment (GitHub Pages)

1. Push the `pwa/` folder to `master`.
2. Repo → Settings → Pages → Source: **Deploy from a branch**.
3. Branch: `master`, Folder: `/pwa`.
4. App goes live at `https://<user>.github.io/<repo>/`.

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
