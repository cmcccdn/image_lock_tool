"""Generate the application icon: a padlock locking an image.

Run:  python -m image_lock.gui.icon_gen   # writes resources/icon.png + .ico
"""
import os
from PIL import Image, ImageDraw


def make_icon(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ---- image card (back) ----
    pad = int(size * 0.10)
    card_l = pad
    card_t = int(size * 0.18)
    card_r = size - pad
    card_b = size - pad
    # frame
    d.rounded_rectangle([card_l, card_t, card_r, card_b],
                        radius=int(size * 0.04),
                        fill=(245, 245, 250, 255),
                        outline=(70, 90, 130, 255),
                        width=max(2, size // 60))
    # sky
    inner = int(size * 0.02)
    sky_l = card_l + inner
    sky_t = card_t + inner
    sky_r = card_r - inner
    sky_b = card_b - inner
    d.rectangle([sky_l, sky_t, sky_r, sky_b], fill=(160, 210, 240, 255))
    # mountains
    mid_y = sky_t + (sky_b - sky_t) * 0.55
    d.polygon([
        (sky_l, sky_b),
        (sky_l + (sky_r - sky_l) * 0.30, mid_y),
        (sky_l + (sky_r - sky_l) * 0.55, sky_b - (sky_b - sky_t) * 0.10),
        (sky_l + (sky_r - sky_l) * 0.75, mid_y - (sky_b - sky_t) * 0.05),
        (sky_r, sky_b),
    ], fill=(90, 150, 90, 255))
    # sun
    sun_r = int((sky_r - sky_l) * 0.10)
    sun_cx = sky_l + int((sky_r - sky_l) * 0.78)
    sun_cy = sky_t + int((sky_b - sky_t) * 0.22)
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r,
               sun_cx + sun_r, sun_cy + sun_r],
              fill=(255, 210, 80, 255))

    # ---- padlock (front, slightly off-centre) ----
    lock_w = int(size * 0.55)
    lock_h = int(size * 0.42)
    lock_l = (size - lock_w) // 2
    lock_t = int(size * 0.42)
    lock_r = lock_l + lock_w
    lock_b = lock_t + lock_h
    # shadow
    sh = max(2, size // 80)
    d.rounded_rectangle([lock_l + sh, lock_t + sh, lock_r + sh, lock_b + sh],
                        radius=int(size * 0.06),
                        fill=(0, 0, 0, 90))
    # body
    d.rounded_rectangle([lock_l, lock_t, lock_r, lock_b],
                        radius=int(size * 0.06),
                        fill=(255, 180, 40, 255),
                        outline=(150, 90, 10, 255),
                        width=max(2, size // 70))
    # shackle
    sh_w = int(lock_w * 0.55)
    sh_l = lock_l + (lock_w - sh_w) // 2
    sh_top = lock_t - int(lock_h * 0.55)
    sh_bot = lock_t + int(lock_h * 0.18)
    sh_thick = max(4, size // 28)
    d.arc([sh_l, sh_top, sh_l + sh_w, sh_bot],
          start=180, end=360,
          fill=(120, 130, 145, 255), width=sh_thick)
    # straight legs
    d.rectangle([sh_l, (sh_top + sh_bot) // 2,
                 sh_l + sh_thick, lock_t + int(lock_h * 0.05)],
                fill=(120, 130, 145, 255))
    d.rectangle([sh_l + sh_w - sh_thick, (sh_top + sh_bot) // 2,
                 sh_l + sh_w, lock_t + int(lock_h * 0.05)],
                fill=(120, 130, 145, 255))
    # keyhole
    kh_cx = (lock_l + lock_r) // 2
    kh_cy = lock_t + int(lock_h * 0.45)
    kh_r = max(4, size // 30)
    d.ellipse([kh_cx - kh_r, kh_cy - kh_r, kh_cx + kh_r, kh_cy + kh_r],
              fill=(60, 40, 10, 255))
    d.rectangle([kh_cx - kh_r // 2, kh_cy,
                 kh_cx + kh_r // 2, kh_cy + int(kh_r * 2.2)],
                fill=(60, 40, 10, 255))

    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    res_dir = os.path.normpath(os.path.join(here, "..", "..", "resources"))
    os.makedirs(res_dir, exist_ok=True)

    big = make_icon(256)
    png_path = os.path.join(res_dir, "icon.png")
    ico_path = os.path.join(res_dir, "icon.ico")
    big.save(png_path, "PNG")
    big.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48),
                              (64, 64), (128, 128), (256, 256)])
    print("wrote", png_path)
    print("wrote", ico_path)


if __name__ == "__main__":
    main()
