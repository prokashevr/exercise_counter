"""Generate PWA icons (poker-chip style) using OpenCV.

Run from project root:
    python docs/generate_icons.py
"""
import os
import math
import numpy as np
import cv2

OUT_DIR = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT_DIR, exist_ok=True)

BG = (20, 13, 10)         # BGR for #0a0d14 (used only for maskable padding)
BASE = (28, 28, 185)      # BGR for #b91c1c (red base)
FACE = (38, 38, 220)      # BGR for #dc2626 (red face)
DASH = (242, 242, 254)    # BGR for #fef2f2 (off-white)
SHADOW = (0, 0, 0)


def draw_chip(size: int, fill_ratio: float = 0.92, bg=None) -> np.ndarray:
    """Draw a poker-chip icon. fill_ratio sets chip diameter vs canvas."""
    img = np.zeros((size, size, 4), dtype=np.uint8)
    if bg is not None:
        img[:] = (*bg, 255)

    cx, cy = size / 2, size / 2
    r_outer = int((size / 2) * fill_ratio)

    # Build alpha mask layer for the chip body, then composite
    chip = np.zeros((size, size, 4), dtype=np.uint8)

    # Outer base circle (red)
    cv2.circle(chip, (int(cx), int(cy)), r_outer, (*BASE, 255), -1, lineType=cv2.LINE_AA)

    # 8 white dashes around the rim (each ~24deg wide, centered every 45deg)
    rim_inner = int(r_outer * 0.78)
    for i in range(8):
        center_deg = i * 45
        start = center_deg - 12
        end = center_deg + 12
        # Draw a white pie slice, then mask it to a ring by drawing the face later.
        # Use ellipse with thickness=-1 + clipping via face circle below.
        cv2.ellipse(
            chip,
            (int(cx), int(cy)),
            (r_outer, r_outer),
            0, start, end,
            (*DASH, 255),
            thickness=-1,
            lineType=cv2.LINE_AA,
        )

    # Face (inner solid circle) — covers dash inner ends
    r_face = int(r_outer * 0.58)
    cv2.circle(chip, (int(cx), int(cy)), r_face, (*FACE, 255), -1, lineType=cv2.LINE_AA)

    # Decorative dashed inner ring on the face
    r_ring = int(r_face * 0.82)
    n_segs = 24
    for i in range(n_segs):
        if i % 2 == 0:
            continue
        a0 = (i / n_segs) * 360
        a1 = ((i + 1) / n_segs) * 360
        cv2.ellipse(
            chip,
            (int(cx), int(cy)),
            (r_ring, r_ring),
            0, a0, a1,
            (*DASH, 220),
            thickness=max(2, size // 90),
            lineType=cv2.LINE_AA,
        )

    # Center text "R"
    font = cv2.FONT_HERSHEY_DUPLEX
    text = "R"
    scale = size / 180.0
    thickness = max(2, int(size / 60))
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    tx = int(cx - tw / 2)
    ty = int(cy + th / 2)
    # Text shadow
    cv2.putText(chip, text, (tx + max(1, size // 200), ty + max(1, size // 200)),
                font, scale, (0, 0, 0, 180), thickness + 1, cv2.LINE_AA)
    cv2.putText(chip, text, (tx, ty), font, scale, (255, 255, 255, 255),
                thickness, cv2.LINE_AA)

    # Soft top highlight (gloss)
    gloss = np.zeros((size, size, 4), dtype=np.uint8)
    cv2.ellipse(
        gloss,
        (int(cx - size * 0.05), int(cy - size * 0.18)),
        (int(r_outer * 0.55), int(r_outer * 0.30)),
        0, 0, 360,
        (255, 255, 255, 60),
        thickness=-1,
        lineType=cv2.LINE_AA,
    )
    chip = _alpha_over(chip, gloss)

    # Composite chip onto background
    return _alpha_over(img, chip)


def _alpha_over(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    """Alpha-composite top over base (both BGRA)."""
    a_top = top[..., 3:4].astype(np.float32) / 255.0
    a_base = base[..., 3:4].astype(np.float32) / 255.0
    out_a = a_top + a_base * (1 - a_top)
    out_rgb = (
        top[..., :3].astype(np.float32) * a_top +
        base[..., :3].astype(np.float32) * a_base * (1 - a_top)
    )
    out_a_safe = np.where(out_a > 0, out_a, 1)
    out_rgb = out_rgb / out_a_safe
    out = np.zeros_like(base)
    out[..., :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
    out[..., 3:4] = np.clip(out_a * 255, 0, 255).astype(np.uint8)
    return out


def save_png(img: np.ndarray, path: str):
    cv2.imwrite(path, img)
    print(f"  wrote {path} ({img.shape[1]}x{img.shape[0]})")


def main():
    print("Generating PWA icons...")

    # Standard icons (transparent background, chip nearly full-bleed)
    save_png(draw_chip(192, fill_ratio=0.96), os.path.join(OUT_DIR, "icon-192.png"))
    save_png(draw_chip(512, fill_ratio=0.96), os.path.join(OUT_DIR, "icon-512.png"))

    # Maskable icon: chip at ~70% so safe zone fits within ~80% inner area
    save_png(
        draw_chip(512, fill_ratio=0.70, bg=BG),
        os.path.join(OUT_DIR, "icon-maskable.png"),
    )

    # Apple touch icon (180x180, opaque background)
    save_png(
        draw_chip(180, fill_ratio=0.94, bg=BG),
        os.path.join(OUT_DIR, "apple-touch-icon.png"),
    )

    print("Done.")


if __name__ == "__main__":
    main()
