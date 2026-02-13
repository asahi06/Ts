"""Generate atmospheric JPEG images for the ryokan LP."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, random, os

OUT = r"C:\Users\adpm5\Desktop\bkl\images"
os.makedirs(OUT, exist_ok=True)
random.seed(42)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def gradient(w, h, colors, vertical=True):
    """Multi-stop gradient."""
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    n = len(colors) - 1
    for y in range(h) if vertical else range(w):
        t = y / (h - 1) if vertical else y / (w - 1)
        idx = min(int(t * n), n - 1)
        local_t = (t * n) - idx
        c = lerp_color(colors[idx], colors[idx + 1], local_t)
        if vertical:
            draw.line([(0, y), (w, y)], fill=c)
        else:
            draw.line([(y, 0), (y, h)], fill=c)
    return img


def add_noise(img, amount=8):
    """Subtle film-grain noise."""
    from PIL import Image as PILImage
    w, h = img.size
    pixels = img.load()
    for _ in range(w * h // 3):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        r, g, b = pixels[x, y]
        d = random.randint(-amount, amount)
        pixels[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return img


def radial_glow(img, cx, cy, radius, color, intensity=0.3):
    """Soft radial light."""
    overlay = Image.new("RGB", img.size, (0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for r in range(radius, 0, -2):
        t = 1 - (r / radius)
        alpha = int(255 * t * intensity)
        c = tuple(int(color[i] * t) for i in range(3))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius // 3))
    from PIL import ImageChops
    return ImageChops.add(img, overlay)


def vignette(img, strength=0.6):
    """Dark vignette effect."""
    w, h = img.size
    mask = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(mask)
    cx, cy = w // 2, h // 2
    max_r = math.sqrt(cx ** 2 + cy ** 2)
    for r in range(int(max_r), 0, -2):
        t = r / max_r
        val = int(255 * (1 - (t ** 1.5) * strength))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=val)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    result = img.copy()
    black = Image.new("RGB", (w, h), (0, 0, 0))
    result = Image.composite(result, black, mask)
    return result


def draw_mountain_silhouette(draw, w, h, base_y, color, segments=12, amplitude=60):
    points = [(0, h)]
    for i in range(segments + 1):
        x = int(i * w / segments)
        y = base_y - random.randint(10, amplitude) + int(20 * math.sin(i * 0.8))
        points.append((x, y))
    points.append((w, h))
    draw.polygon(points, fill=color)


def draw_soft_circle(img, cx, cy, r, color, blur=20):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (180,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(blur))
    bg = img.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay)
    return bg.convert("RGB")


# ============================================================
# HERO IMAGE — Mountain landscape at dusk
# ============================================================
def make_hero():
    w, h = 1920, 1080
    img = gradient(w, h, [
        (42, 52, 38), (58, 72, 48), (90, 110, 75),
        (140, 155, 115), (200, 195, 170), (235, 228, 215)
    ])
    draw = ImageDraw.Draw(img)
    random.seed(10)
    draw_mountain_silhouette(draw, w, h, 450, (35, 50, 35), 20, 120)
    draw_mountain_silhouette(draw, w, h, 550, (28, 42, 28), 18, 90)
    draw_mountain_silhouette(draw, w, h, 650, (22, 35, 22), 16, 60)
    # Mist layers
    img = img.filter(ImageFilter.GaussianBlur(2))
    img = radial_glow(img, w // 2, 300, 500, (180, 170, 140), 0.12)
    img = vignette(img, 0.5)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "hero.jpg"), "JPEG", quality=88)
    print("hero.jpg")


# ============================================================
# ROOM IMAGES
# ============================================================
def make_room1():
    """Tsukimi — moonlit room with outdoor bath view."""
    w, h = 800, 520
    img = gradient(w, h, [(18, 18, 42), (25, 25, 55), (35, 38, 65), (45, 50, 60)])
    draw = ImageDraw.Draw(img)
    # Moon
    img = draw_soft_circle(img, 620, 100, 40, (255, 250, 210), blur=15)
    draw = ImageDraw.Draw(img)
    # Stars
    for _ in range(40):
        x, y = random.randint(0, w), random.randint(0, h // 2)
        s = random.randint(1, 2)
        draw.ellipse([x, y, x + s, y + s], fill=(255, 255, 240, 120))
    # Mountain
    random.seed(1)
    draw_mountain_silhouette(draw, w, h, 280, (20, 28, 20), 14, 70)
    draw_mountain_silhouette(draw, w, h, 340, (15, 22, 18), 12, 50)
    # Room structure (dark)
    draw.rectangle([0, 360, w, h], fill=(30, 25, 20))
    draw.rectangle([50, 320, 350, 360], fill=(45, 38, 28))
    # Window frame
    draw.rectangle([80, 200, 320, 350], outline=(60, 50, 35), width=4)
    draw.line([(200, 200), (200, 350)], fill=(60, 50, 35), width=3)
    draw.line([(80, 275), (320, 275)], fill=(60, 50, 35), width=3)
    # Warm light from inside
    img = radial_glow(img, 200, 400, 250, (180, 140, 80), 0.08)
    # Bath hint
    draw = ImageDraw.Draw(img)
    draw.ellipse([420, 350, 680, 480], fill=(50, 70, 65))
    draw.ellipse([430, 355, 670, 470], fill=(60, 85, 80))
    img = vignette(img, 0.55)
    add_noise(img, 6)
    img.save(os.path.join(OUT, "room1.jpg"), "JPEG", quality=88)
    print("room1.jpg")


def make_room2():
    """Hanaikada — cherry blossom garden view."""
    w, h = 800, 520
    img = gradient(w, h, [(210, 195, 175), (195, 185, 165), (180, 172, 155), (165, 155, 138)])
    draw = ImageDraw.Draw(img)
    # Window with garden
    draw.rectangle([60, 60, 360, 340], fill=(160, 195, 140))
    draw.rectangle([60, 60, 360, 340], outline=(120, 105, 80), width=5)
    draw.line([(210, 60), (210, 340)], fill=(120, 105, 80), width=3)
    draw.line([(60, 200), (360, 200)], fill=(120, 105, 80), width=3)
    # Cherry blossoms through window
    for _ in range(50):
        x = random.randint(70, 350)
        y = random.randint(70, 190)
        r = random.randint(3, 10)
        pink = (235 + random.randint(-15, 10), 170 + random.randint(-20, 20), 180 + random.randint(-15, 15))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=pink)
    # Tatami floor
    draw.rectangle([0, 350, w, h], fill=(185, 175, 140))
    for i in range(0, w, 90):
        draw.line([(i, 350), (i, h)], fill=(175, 165, 130), width=1)
    # Low table
    draw.rectangle([400, 320, 650, 380], fill=(100, 80, 55))
    draw.rectangle([400, 320, 650, 328], fill=(115, 92, 62))
    # Zabuton
    draw.ellipse([420, 400, 510, 460], fill=(140, 50, 45))
    draw.ellipse([560, 400, 650, 460], fill=(140, 50, 45))
    # Tea set on table
    draw.ellipse([500, 335, 530, 365], fill=(85, 70, 50))
    draw.ellipse([540, 340, 565, 360], fill=(85, 70, 50))
    img = radial_glow(img, 210, 200, 300, (240, 220, 190), 0.1)
    img = vignette(img, 0.45)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "room2.jpg"), "JPEG", quality=88)
    print("room2.jpg")


def make_room3():
    """Yamagasumi — misty mountain modern room."""
    w, h = 800, 520
    img = gradient(w, h, [(195, 200, 185), (180, 188, 172), (170, 175, 160), (160, 158, 145)])
    draw = ImageDraw.Draw(img)
    # Large window
    draw.rectangle([40, 50, 520, 300], fill=(150, 170, 155))
    draw.rectangle([40, 50, 520, 300], outline=(110, 95, 75), width=4)
    draw.line([(280, 50), (280, 300)], fill=(110, 95, 75), width=3)
    # Misty mountains
    for layer in range(4):
        y_base = 120 + layer * 35
        opacity_color = (150 - layer * 15, 170 - layer * 12, 155 - layer * 10)
        pts = [(40, 300)]
        random.seed(30 + layer)
        for i in range(15):
            x = 40 + int(i * 480 / 14)
            y = y_base - random.randint(5, 40) + int(15 * math.sin(i * 0.6))
            pts.append((x, y))
        pts.append((520, 300))
        draw.polygon(pts, fill=opacity_color)
    # Bed area
    draw.rectangle([540, 200, 770, 380], fill=(230, 225, 215))
    draw.rectangle([540, 200, 770, 215], fill=(200, 190, 175))
    draw.rectangle([545, 220, 655, 310], fill=(220, 215, 205))
    draw.rectangle([660, 220, 765, 310], fill=(215, 210, 200))
    # Pillows
    draw.rounded_rectangle([555, 230, 620, 270], radius=8, fill=(235, 232, 225))
    draw.rounded_rectangle([685, 230, 750, 270], radius=8, fill=(235, 232, 225))
    # Floor
    draw.rectangle([0, 380, w, h], fill=(175, 168, 148))
    # Side table
    draw.rectangle([530, 300, 560, 380], fill=(90, 75, 55))
    draw.ellipse([533, 290, 557, 305], fill=(80, 65, 45))
    # Warm light
    img = radial_glow(img, 545, 300, 200, (200, 170, 120), 0.06)
    img = vignette(img, 0.45)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "room3.jpg"), "JPEG", quality=88)
    print("room3.jpg")


def make_room4():
    """Seiryu — stream view room."""
    w, h = 800, 520
    img = gradient(w, h, [(185, 195, 180), (175, 185, 172), (165, 172, 160), (155, 155, 142)])
    draw = ImageDraw.Draw(img)
    # Window
    draw.rectangle([50, 60, 500, 310], fill=(120, 165, 155))
    draw.rectangle([50, 60, 500, 310], outline=(100, 88, 68), width=4)
    draw.line([(275, 60), (275, 310)], fill=(100, 88, 68), width=3)
    # Stream/water
    for i in range(5):
        y = 220 + i * 15
        pts = []
        for j in range(20):
            x = 55 + j * 24
            yy = y + int(8 * math.sin(j * 0.7 + i * 1.2))
            pts.append((x, yy))
        for j in range(len(pts) - 1):
            c = (100 + random.randint(-10, 10), 155 + random.randint(-10, 10), 170 + random.randint(-5, 5))
            draw.line([pts[j], pts[j + 1]], fill=c, width=2)
    # Trees/foliage
    for _ in range(30):
        x = random.randint(60, 490)
        y = random.randint(70, 180)
        r = random.randint(8, 22)
        g = (60 + random.randint(-15, 20), 110 + random.randint(-20, 30), 60 + random.randint(-10, 15))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=g)
    # Room floor
    draw.rectangle([0, 340, w, h], fill=(180, 172, 145))
    for i in range(0, w, 95):
        draw.line([(i, 340), (i, h)], fill=(170, 162, 135), width=1)
    # Low writing desk
    draw.rectangle([540, 260, 750, 310], fill=(95, 78, 55))
    draw.rectangle([540, 260, 750, 268], fill=(108, 88, 62))
    # Zabuton
    draw.ellipse([600, 330, 700, 395], fill=(80, 95, 75))
    # Ikebana
    draw.rectangle([640, 230, 650, 260], fill=(100, 85, 60))
    draw.ellipse([625, 215, 665, 238], fill=(90, 75, 52))
    draw.line([(645, 218), (630, 185)], fill=(80, 120, 60), width=2)
    draw.line([(645, 220), (660, 190)], fill=(90, 130, 65), width=2)
    draw.ellipse([625, 178, 638, 192], fill=(200, 80, 80))
    img = radial_glow(img, 275, 200, 280, (170, 190, 180), 0.08)
    img = vignette(img, 0.45)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "room4.jpg"), "JPEG", quality=88)
    print("room4.jpg")


# ============================================================
# ONSEN IMAGE
# ============================================================
def make_onsen():
    w, h = 800, 600
    img = gradient(w, h, [(25, 32, 45), (35, 45, 52), (45, 58, 55), (55, 68, 58), (60, 72, 60)])
    draw = ImageDraw.Draw(img)
    # Moon
    img = draw_soft_circle(img, 620, 80, 35, (255, 250, 215), blur=12)
    draw = ImageDraw.Draw(img)
    # Stars
    random.seed(99)
    for _ in range(30):
        x, y = random.randint(0, w), random.randint(0, 200)
        draw.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 240))
    # Mountains
    random.seed(7)
    draw_mountain_silhouette(draw, w, h, 220, (30, 42, 32), 16, 80)
    draw_mountain_silhouette(draw, w, h, 280, (25, 38, 28), 14, 50)
    # Rocks
    for rx, ry, rr in [(80, 350, 60), (130, 370, 45), (650, 340, 55), (720, 360, 40), (700, 380, 50)]:
        draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(55, 58, 48))
        draw.ellipse([rx - rr + 3, ry - rr + 2, rx + rr - 2, ry + rr - 3], fill=(62, 65, 55))
    # Hot spring water
    draw.ellipse([100, 330, 680, 530], fill=(65, 95, 90))
    draw.ellipse([110, 340, 670, 520], fill=(75, 110, 105))
    draw.ellipse([120, 350, 660, 510], fill=(85, 120, 115))
    # Water reflections
    for i in range(8):
        y = 380 + i * 15
        x1 = 150 + i * 5
        x2 = 630 - i * 5
        draw.line([(x1, y), (x2, y)], fill=(95, 135, 128), width=1)
    # Steam (soft ellipses)
    steam_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam_layer)
    for sx, sy, sr in [(250, 280, 80), (400, 260, 100), (550, 285, 70), (350, 240, 60)]:
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(220, 225, 230, 25))
    steam_layer = steam_layer.filter(ImageFilter.GaussianBlur(30))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, steam_layer)
    img = img.convert("RGB")
    # Lantern
    draw = ImageDraw.Draw(img)
    draw.rectangle([65, 260, 95, 340], fill=(65, 60, 50))
    draw.rectangle([58, 250, 102, 265], fill=(80, 72, 58))
    img = radial_glow(img, 80, 300, 60, (220, 180, 100), 0.08)
    img = vignette(img, 0.55)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "onsen.jpg"), "JPEG", quality=88)
    print("onsen.jpg")


# ============================================================
# CUISINE IMAGES
# ============================================================
def make_cuisine1():
    """Sashimi plate."""
    w, h = 600, 480
    img = gradient(w, h, [(35, 28, 22), (40, 32, 25), (42, 35, 28)])
    draw = ImageDraw.Draw(img)
    # Dark plate
    draw.ellipse([80, 100, 520, 380], fill=(25, 25, 22))
    draw.ellipse([90, 108, 510, 372], fill=(32, 30, 28))
    draw.ellipse([95, 112, 505, 368], outline=(50, 45, 38), width=1)
    # Sashimi slices (salmon pink)
    for i in range(5):
        x = 180 + i * 35
        y = 195 + (i % 2) * 10
        w2, h2 = 40, 22
        draw.rounded_rectangle([x, y, x + w2, y + h2], radius=4, fill=(215, 100, 85))
        draw.line([(x + 5, y + 5), (x + w2 - 8, y + h2 - 5)], fill=(235, 160, 150), width=1)
        draw.line([(x + 15, y + 3), (x + w2 - 3, y + h2 - 8)], fill=(230, 140, 130), width=1)
    # White fish slices
    for i in range(4):
        x = 200 + i * 38
        y = 250
        draw.rounded_rectangle([x, y, x + 35, y + 18], radius=3, fill=(235, 225, 210))
        draw.line([(x + 3, y + 8), (x + 30, y + 6)], fill=(225, 215, 200), width=1)
    # Tuna slices
    for i in range(3):
        x = 220 + i * 40
        y = 290
        draw.rounded_rectangle([x, y, x + 38, y + 20], radius=4, fill=(165, 40, 45))
        draw.line([(x + 5, y + 8), (x + 32, y + 10)], fill=(185, 70, 70), width=1)
    # Wasabi
    draw.ellipse([380, 210, 405, 235], fill=(105, 160, 75))
    # Shiso leaves
    for lx, ly in [(165, 200), (170, 250)]:
        draw.polygon([(lx, ly), (lx - 15, ly + 12), (lx, ly + 20), (lx + 15, ly + 12)], fill=(50, 105, 45))
    # Daikon tsuma (shredded)
    for i in range(20):
        x = 160 + random.randint(0, 40)
        y = 320 + random.randint(-5, 15)
        draw.line([(x, y), (x + random.randint(8, 20), y + random.randint(-3, 3))], fill=(240, 235, 215), width=1)
    # Soy sauce dish
    draw.ellipse([420, 310, 480, 360], fill=(45, 38, 30))
    draw.ellipse([425, 314, 475, 356], fill=(30, 20, 12))
    img = radial_glow(img, 300, 240, 200, (180, 150, 100), 0.06)
    img = vignette(img, 0.6)
    add_noise(img, 6)
    img.save(os.path.join(OUT, "cuisine1.jpg"), "JPEG", quality=90)
    print("cuisine1.jpg")


def make_cuisine2():
    """Grilled fish on square plate."""
    w, h = 600, 480
    img = gradient(w, h, [(38, 30, 24), (42, 34, 28), (45, 38, 30)])
    draw = ImageDraw.Draw(img)
    # Square plate
    draw.rounded_rectangle([80, 80, 520, 400], radius=8, fill=(210, 200, 180))
    draw.rounded_rectangle([88, 88, 512, 392], radius=6, fill=(225, 218, 200))
    draw.rounded_rectangle([92, 92, 508, 388], radius=5, outline=(200, 192, 175), width=1)
    # Fish body
    fish_cx, fish_cy = 300, 220
    draw.ellipse([150, 170, 450, 280], fill=(195, 160, 100))
    draw.ellipse([155, 175, 445, 275], fill=(205, 170, 108))
    # Grill marks
    for gx in range(180, 430, 40):
        draw.line([(gx, 180), (gx + 15, 270)], fill=(165, 130, 75), width=3)
    # Fish tail
    draw.polygon([(440, 200), (490, 180), (480, 225), (490, 265), (440, 245)], fill=(185, 150, 95))
    # Eye
    draw.ellipse([175, 210, 195, 230], fill=(40, 35, 25))
    draw.ellipse([180, 215, 188, 223], fill=(60, 55, 45))
    # Lemon half
    draw.ellipse([150, 310, 200, 360], fill=(230, 215, 70))
    draw.ellipse([155, 315, 195, 355], fill=(240, 230, 90))
    for angle in range(0, 360, 45):
        x2 = 175 + int(15 * math.cos(math.radians(angle)))
        y2 = 335 + int(15 * math.sin(math.radians(angle)))
        draw.line([(175, 335), (x2, y2)], fill=(220, 200, 60), width=1)
    # Daikon oroshi
    draw.ellipse([400, 310, 460, 355], fill=(240, 235, 225))
    draw.ellipse([420, 318, 432, 330], fill=(200, 50, 40))
    # Green garnish
    for _ in range(8):
        gx = random.randint(220, 370)
        gy = random.randint(300, 360)
        draw.polygon([(gx, gy), (gx - 6, gy + 14), (gx + 6, gy + 14)], fill=(60, 110, 50))
    img = radial_glow(img, 300, 240, 220, (190, 160, 110), 0.06)
    img = vignette(img, 0.55)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "cuisine2.jpg"), "JPEG", quality=90)
    print("cuisine2.jpg")


def make_cuisine3():
    """Simmered dish in ceramic bowl."""
    w, h = 600, 480
    img = gradient(w, h, [(32, 26, 22), (38, 32, 26), (40, 35, 28)])
    draw = ImageDraw.Draw(img)
    # Bowl
    draw.ellipse([100, 340, 500, 440], fill=(48, 40, 32))
    draw.rounded_rectangle([120, 180, 480, 380], radius=60, fill=(95, 82, 62))
    draw.ellipse([110, 160, 490, 280], fill=(105, 90, 68))
    draw.ellipse([120, 168, 480, 275], fill=(75, 62, 48))
    # Broth
    draw.ellipse([130, 175, 470, 270], fill=(175, 140, 85, 80))
    # Tofu block
    draw.rounded_rectangle([220, 190, 310, 245], radius=5, fill=(235, 228, 210))
    draw.rounded_rectangle([222, 192, 308, 243], radius=4, fill=(242, 238, 225))
    # Daikon/turnip
    draw.ellipse([160, 200, 220, 250], fill=(210, 180, 120))
    draw.ellipse([163, 203, 217, 247], fill=(220, 190, 130))
    # Carrot
    draw.ellipse([330, 210, 370, 245], fill=(210, 110, 50))
    draw.ellipse([333, 213, 367, 242], fill=(220, 120, 58))
    # Shiitake mushroom
    draw.ellipse([260, 200, 310, 230], fill=(80, 55, 30))
    draw.line([(275, 210), (275, 225)], fill=(65, 42, 20), width=1)
    draw.line([(285, 208), (285, 225)], fill=(65, 42, 20), width=1)
    draw.line([(295, 210), (295, 225)], fill=(65, 42, 20), width=1)
    # Green vegetable
    draw.ellipse([370, 195, 420, 230], fill=(70, 120, 50))
    draw.ellipse([375, 198, 415, 226], fill=(80, 135, 58))
    # Yuzu peel
    draw.arc([340, 185, 365, 205], 0, 180, fill=(200, 180, 40), width=3)
    # Steam
    steam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for sx, sy, sr in [(230, 140, 50), (300, 120, 70), (370, 135, 55)]:
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(230, 230, 235, 18))
    steam = steam.filter(ImageFilter.GaussianBlur(20))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, steam)
    img = img.convert("RGB")
    # Lid to the side
    draw = ImageDraw.Draw(img)
    draw.ellipse([440, 310, 540, 370], fill=(105, 90, 68))
    draw.ellipse([445, 314, 535, 365], fill=(115, 100, 76))
    draw.ellipse([478, 300, 502, 318], fill=(95, 80, 60))
    img = radial_glow(img, 300, 220, 200, (180, 150, 100), 0.06)
    img = vignette(img, 0.6)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "cuisine3.jpg"), "JPEG", quality=90)
    print("cuisine3.jpg")


def make_cuisine4():
    """Wagyu shabu-shabu hot pot."""
    w, h = 600, 480
    img = gradient(w, h, [(30, 24, 20), (36, 30, 25), (40, 34, 28)])
    draw = ImageDraw.Draw(img)
    # Hot pot (nabe)
    draw.ellipse([80, 340, 520, 430], fill=(25, 20, 16))
    draw.rounded_rectangle([90, 170, 510, 380], radius=50, fill=(60, 55, 50))
    draw.ellipse([80, 150, 520, 270], fill=(72, 65, 58))
    draw.ellipse([90, 158, 510, 265], fill=(48, 42, 38))
    # Broth
    draw.ellipse([100, 165, 500, 260], fill=(170, 130, 75))
    draw.ellipse([105, 168, 495, 256], fill=(155, 118, 68))
    # Bubbles
    for _ in range(12):
        bx = random.randint(140, 460)
        by = random.randint(175, 245)
        br = random.randint(3, 8)
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(180, 145, 85))
        draw.ellipse([bx - br + 1, by - br + 1, bx + br - 1, by + br - 1], fill=(165, 128, 72))
    # Vegetables in pot
    draw.ellipse([150, 190, 200, 220], fill=(230, 225, 200))  # tofu
    draw.ellipse([350, 185, 400, 215], fill=(65, 115, 48))  # green
    draw.rounded_rectangle([250, 195, 290, 230], radius=4, fill=(220, 210, 190))  # enoki
    draw.ellipse([420, 195, 460, 225], fill=(75, 50, 28))  # shiitake
    # Plate with wagyu slices above
    draw.ellipse([150, 45, 450, 155], fill=(230, 225, 215))
    draw.ellipse([155, 48, 445, 152], fill=(240, 238, 230))
    # Marbled beef slices
    for i in range(4):
        sx = 190 + i * 50
        sy = 65 + (i % 2) * 8
        draw.rounded_rectangle([sx, sy, sx + 55, sy + 30], radius=4, fill=(190, 60, 55))
        # Marbling
        for _ in range(4):
            mx = sx + random.randint(5, 48)
            my = sy + random.randint(3, 25)
            draw.line([(mx, my), (mx + random.randint(5, 15), my + random.randint(-3, 3))],
                      fill=(240, 200, 200), width=2)
    # Handles
    draw.rounded_rectangle([40, 240, 85, 265], radius=5, fill=(80, 72, 60))
    draw.rounded_rectangle([515, 240, 560, 265], radius=5, fill=(80, 72, 60))
    # Steam
    steam = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for sx, sy, sr in [(220, 120, 60), (300, 100, 80), (380, 115, 65)]:
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(220, 220, 225, 15))
    steam = steam.filter(ImageFilter.GaussianBlur(25))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, steam)
    img = img.convert("RGB")
    # Blue flame hint under pot
    draw = ImageDraw.Draw(img)
    for fx in range(220, 400, 20):
        fy = 415
        draw.polygon([(fx, fy + 10), (fx + 5, fy - 5), (fx + 10, fy + 10)], fill=(60, 90, 180))
    img = radial_glow(img, 300, 220, 220, (170, 140, 90), 0.06)
    img = vignette(img, 0.6)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "cuisine4.jpg"), "JPEG", quality=90)
    print("cuisine4.jpg")


# ============================================================
# CUISINE EXTRA: Breakfast, Dessert, Sake, Appetizer
# ============================================================
def make_cuisine5():
    """Japanese breakfast set."""
    w, h = 600, 480
    img = gradient(w, h, [(55, 48, 38), (60, 52, 42), (65, 55, 45)])
    draw = ImageDraw.Draw(img)
    # Wooden tray
    draw.rounded_rectangle([40, 60, 560, 420], radius=6, fill=(120, 95, 62))
    draw.rounded_rectangle([45, 65, 555, 415], radius=5, fill=(135, 108, 70))
    # Rice in donabe (clay pot)
    draw.ellipse([60, 250, 220, 380], fill=(90, 78, 55))
    draw.ellipse([65, 245, 215, 350], fill=(100, 85, 60))
    draw.ellipse([75, 255, 205, 340], fill=(240, 238, 230))
    # Rice grains suggestion
    for _ in range(15):
        rx, ry = random.randint(90, 190), random.randint(265, 325)
        draw.ellipse([rx, ry, rx + 4, ry + 3], fill=(248, 245, 238))
    # Miso soup bowl
    draw.ellipse([250, 270, 380, 370], fill=(70, 25, 20))
    draw.ellipse([255, 268, 375, 345], fill=(80, 30, 25))
    draw.ellipse([260, 275, 370, 340], fill=(160, 120, 60))
    # Tofu in miso
    draw.rounded_rectangle([290, 290, 320, 310], radius=2, fill=(235, 228, 210))
    # Grilled fish small plate
    draw.ellipse([380, 240, 530, 340], fill=(200, 192, 175))
    draw.ellipse([385, 244, 525, 336], fill=(215, 208, 192))
    draw.ellipse([410, 265, 500, 310], fill=(195, 155, 95))
    # Small dishes top row
    for i, color in enumerate([(180, 175, 160), (170, 165, 152), (185, 180, 168)]):
        cx = 130 + i * 140
        draw.ellipse([cx - 50, 100, cx + 50, 190], fill=color)
        draw.ellipse([cx - 45, 105, cx + 45, 185], fill=tuple(c + 12 for c in color))
    # Egg in first dish
    draw.ellipse([90, 130, 130, 160], fill=(220, 190, 60))
    # Pickles in second dish
    for px in range(240, 310, 12):
        draw.rounded_rectangle([px, 135, px + 10, 155], radius=3, fill=(180, 100, 50))
    # Green in third dish
    draw.ellipse([360, 130, 405, 165], fill=(60, 110, 50))
    # Chopsticks
    draw.line([(50, 430), (200, 400)], fill=(160, 130, 85), width=3)
    draw.line([(55, 435), (205, 405)], fill=(150, 120, 78), width=3)
    img = radial_glow(img, 300, 250, 250, (200, 170, 120), 0.06)
    img = vignette(img, 0.5)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "cuisine5.jpg"), "JPEG", quality=90)
    print("cuisine5.jpg")


def make_cuisine6():
    """Japanese sake and cups."""
    w, h = 600, 480
    img = gradient(w, h, [(28, 24, 20), (32, 28, 24), (38, 34, 28)])
    draw = ImageDraw.Draw(img)
    # Sake bottle (tokkuri)
    draw.polygon([(270, 120), (250, 180), (240, 350), (260, 380), (340, 380), (360, 350), (350, 180), (330, 120)],
                 fill=(55, 50, 80))
    draw.ellipse([265, 108, 335, 135], fill=(55, 50, 80))
    draw.ellipse([270, 112, 330, 132], fill=(65, 58, 88))
    # Sake level hint
    draw.rounded_rectangle([248, 250, 352, 370], radius=10, fill=(60, 55, 85))
    # Ochoko cups
    for cx, cy in [(150, 350), (450, 350)]:
        draw.polygon([(cx - 25, cy), (cx - 20, cy - 35), (cx + 20, cy - 35), (cx + 25, cy)], fill=(200, 195, 185))
        draw.ellipse([cx - 20, cy - 42, cx + 20, cy - 28], fill=(210, 205, 195))
        draw.ellipse([cx - 17, cy - 39, cx + 17, cy - 31], fill=(220, 215, 205))
        # Sake in cup
        draw.ellipse([cx - 15, cy - 38, cx + 15, cy - 32], fill=(240, 238, 230))
    # Wooden tray/board
    draw.rounded_rectangle([100, 370, 500, 440], radius=4, fill=(100, 80, 52))
    # Small appetizer
    draw.ellipse([400, 200, 520, 300], fill=(60, 55, 45))
    draw.ellipse([405, 205, 515, 295], fill=(50, 45, 38))
    draw.rounded_rectangle([430, 225, 470, 260], radius=4, fill=(190, 90, 70))
    draw.polygon([(440, 265), (435, 280), (445, 280)], fill=(55, 100, 45))
    img = radial_glow(img, 300, 280, 200, (160, 140, 100), 0.07)
    img = vignette(img, 0.6)
    add_noise(img, 6)
    img.save(os.path.join(OUT, "cuisine6.jpg"), "JPEG", quality=90)
    print("cuisine6.jpg")


def make_cuisine7():
    """Dessert — matcha and wagashi."""
    w, h = 600, 480
    img = gradient(w, h, [(42, 38, 32), (48, 42, 35), (52, 46, 38)])
    draw = ImageDraw.Draw(img)
    # Matcha bowl (chawan)
    draw.ellipse([80, 280, 300, 420], fill=(65, 80, 55))
    draw.ellipse([85, 260, 295, 350], fill=(75, 92, 62))
    draw.ellipse([92, 268, 288, 345], fill=(58, 72, 48))
    # Matcha tea
    draw.ellipse([100, 275, 280, 340], fill=(90, 130, 60))
    draw.ellipse([105, 278, 275, 335], fill=(100, 145, 68))
    # Foam dots
    for _ in range(15):
        fx, fy = random.randint(120, 260), random.randint(285, 325)
        draw.ellipse([fx, fy, fx + 3, fy + 3], fill=(140, 180, 100))
    # Wagashi plate
    draw.ellipse([340, 200, 540, 350], fill=(190, 185, 175))
    draw.ellipse([345, 205, 535, 345], fill=(205, 200, 190))
    # Wagashi (Japanese sweet)
    draw.ellipse([395, 240, 475, 305], fill=(220, 140, 160))
    draw.ellipse([400, 245, 470, 300], fill=(230, 155, 175))
    # Leaf decoration
    draw.polygon([(425, 248), (410, 235), (435, 230), (450, 238)], fill=(70, 120, 55))
    # Second wagashi
    draw.rounded_rectangle([410, 305, 460, 335], radius=8, fill=(200, 180, 100))
    draw.rounded_rectangle([413, 308, 457, 332], radius=6, fill=(215, 195, 110))
    # Bamboo pick
    draw.line([(440, 255), (440, 310)], fill=(180, 160, 100), width=2)
    img = radial_glow(img, 300, 300, 200, (160, 150, 100), 0.06)
    img = vignette(img, 0.55)
    add_noise(img, 5)
    img.save(os.path.join(OUT, "cuisine7.jpg"), "JPEG", quality=90)
    print("cuisine7.jpg")


def make_cuisine8():
    """Appetizer / Sakizuke."""
    w, h = 600, 480
    img = gradient(w, h, [(30, 25, 22), (35, 30, 25), (40, 35, 28)])
    draw = ImageDraw.Draw(img)
    # Elegant small plate
    draw.rounded_rectangle([120, 120, 480, 380], radius=12, fill=(42, 40, 55))
    draw.rounded_rectangle([125, 125, 475, 375], radius=10, fill=(50, 48, 62))
    draw.rounded_rectangle([130, 130, 470, 370], radius=8, outline=(65, 60, 75), width=1)
    # Artistic food arrangement
    # Main piece (fish/meat)
    draw.rounded_rectangle([200, 180, 320, 240], radius=6, fill=(200, 130, 90))
    draw.rounded_rectangle([205, 185, 315, 235], radius=4, fill=(210, 140, 100))
    # Sauce drizzle
    for i in range(10):
        sx = 180 + i * 15
        sy = 260 + int(8 * math.sin(i * 0.8))
        draw.ellipse([sx, sy, sx + 8, sy + 3], fill=(80, 40, 20))
    # Microgreens
    for _ in range(12):
        gx = random.randint(250, 380)
        gy = random.randint(250, 310)
        draw.line([(gx, gy), (gx + random.randint(-8, 8), gy - random.randint(10, 25))],
                  fill=(60, 120, 50), width=1)
        draw.ellipse([gx - 2, gy - 25, gx + 4, gy - 20], fill=(70, 135, 55))
    # Edible flower
    for angle in range(0, 360, 60):
        px = 360 + int(12 * math.cos(math.radians(angle)))
        py = 200 + int(12 * math.sin(math.radians(angle)))
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(180, 80, 120))
    draw.ellipse([355, 195, 365, 205], fill=(230, 200, 60))
    # Gold leaf accent
    draw.polygon([(220, 200), (225, 192), (240, 195), (235, 205)], fill=(200, 175, 80))
    img = radial_glow(img, 300, 250, 200, (160, 140, 100), 0.06)
    img = vignette(img, 0.6)
    add_noise(img, 6)
    img.save(os.path.join(OUT, "cuisine8.jpg"), "JPEG", quality=90)
    print("cuisine8.jpg")


# ============================================================
if __name__ == "__main__":
    print("Generating images...")
    make_hero()
    make_room1()
    make_room2()
    make_room3()
    make_room4()
    make_onsen()
    make_cuisine1()
    make_cuisine2()
    make_cuisine3()
    make_cuisine4()
    make_cuisine5()
    make_cuisine6()
    make_cuisine7()
    make_cuisine8()
    print("All done!")
