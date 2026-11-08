#!/usr/bin/env python3
"""
High-Resolution Document & Paper Texture Generator for The Black Pines.
Creates authentic period assets with paper fiber aging, coffee rings,
folding creases, official government seals, typewriter text, and red ink rubber stamps:
1. usfs_evacuation_notice.png (1024x1024) - U.S. Forest Service Evacuation Order
2. warden_field_journal.png (1024x1024) - Warden's handwritten field logbook
3. black_pines_topomap.png (1024x1024) - Topographical survey map with grease pencil marks
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs("assets/textures/documents", exist_ok=True)

def get_font(font_names, size):
    for fn in font_names:
        if os.path.exists(fn):
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                pass
    return ImageFont.load_default()

FONT_SERIF = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
]
FONT_SERIF_BOLD = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
]
FONT_SANS_BOLD = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
]
FONT_MONO = [
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
]

def add_paper_grain(draw, width, height, base_color):
    # Add fibrous paper grain & subtle mottled discoloration
    random.seed(42)
    for _ in range(12000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        # Varying specks
        shade = random.randint(-18, 12)
        r = max(0, min(255, base_color[0] + shade))
        g = max(0, min(255, base_color[1] + shade))
        b = max(0, min(255, base_color[2] + shade))
        draw.point((x, y), fill=(r, g, b, 255))

def add_coffee_stain(draw, cx, cy, radius):
    # Concentric irregular coffee ring with edge drying
    for angle_deg in range(360):
        rad = math.radians(angle_deg)
        r_wobble = radius + math.sin(rad * 5.0) * 4.0 + math.cos(rad * 3.0) * 3.0
        # Ring rim
        px = int(cx + math.cos(rad) * r_wobble)
        py = int(cy + math.sin(rad) * r_wobble)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(130, 95, 60, 45))
        # Inner wash
        inner_r = r_wobble * 0.7
        ipx = int(cx + math.cos(rad) * inner_r)
        ipy = int(cy + math.sin(rad) * inner_r)
        draw.point((ipx, ipy), fill=(160, 125, 90, 20))

def add_folds(draw, width, height):
    # Horizontal fold line across middle
    mid_y = height // 2
    for x in range(width):
        draw.line([(x, mid_y - 1), (x, mid_y)], fill=(120, 105, 85, 45))
        draw.line([(x, mid_y + 1), (x, mid_y + 2)], fill=(245, 235, 215, 55))
    # Vertical fold line
    mid_x = width // 2
    for y in range(height):
        draw.line([(mid_x - 1, y), (mid_x, y)], fill=(120, 105, 85, 40))
        draw.line([(mid_x + 1, y), (mid_x + 2, y)], fill=(245, 235, 215, 50))

# -----------------------------------------------------------------------------
# 1. USFS Evacuation Notice
# -----------------------------------------------------------------------------
def generate_evacuation_notice():
    w, h = 1024, 1024
    img = Image.new("RGBA", (w, h), (226, 212, 186, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Paper grain and vignette
    add_paper_grain(draw, w, h, (226, 212, 186))
    
    # Border aging / burned vignette
    for b in range(35):
        alpha = int(45 * (1.0 - b / 35.0))
        draw.rectangle([b, b, w - b, h - b], outline=(110, 85, 55, alpha), width=1)

    add_folds(draw, w, h)
    add_coffee_stain(draw, 820, 240, 85)

    # USDA Forest Service Emblem / Header Box
    f_header = get_font(FONT_SANS_BOLD, 22)
    f_sub = get_font(FONT_SERIF, 17)
    f_order = get_font(FONT_SANS_BOLD, 38)
    f_body = get_font(FONT_MONO, 19)
    f_body_bold = get_font(FONT_MONO, 21)
    f_stamp = get_font(FONT_SANS_BOLD, 42)

    # Header Shield & Text
    draw.rectangle([110, 60, 914, 135], outline=(60, 48, 36, 220), width=3)
    draw.rectangle([114, 64, 910, 131], outline=(60, 48, 36, 140), width=1)
    draw.text((512, 82), "UNITED STATES DEPARTMENT OF AGRICULTURE", fill=(45, 35, 25, 255), font=f_header, anchor="mm")
    draw.text((512, 110), "FOREST SERVICE  •  PACIFIC NORTHWEST REGION 6", fill=(65, 55, 40, 255), font=f_sub, anchor="mm")

    # Red Emergency Banner
    draw.rectangle([110, 160, 914, 235], fill=(168, 38, 30, 235), outline=(110, 20, 15, 255), width=3)
    draw.text((512, 197), "- EMERGENCY EVACUATION ORDER -", fill=(245, 235, 225, 255), font=f_order, anchor="mm")

    # Sub-metadata
    draw.text((120, 260), "LOCATION: BLACK PINES DISTRICT — RANGER SECTOR #04", fill=(50, 40, 30, 255), font=f_body_bold)
    draw.text((120, 290), "DIRECTIVE NO: USFS-ORD-86-0941        DATE: OCTOBER 29", fill=(50, 40, 30, 255), font=f_body)
    draw.line([(120, 325), (904, 325)], fill=(80, 65, 50, 200), width=2)

    # Body Paragraphs in Typewriter font
    body_lines = [
        "ALL FORESTRY PERSONNEL, RESEARCH WARDENS, AND FIELD CONTRACTORS",
        "ARE ORDERED TO IMMEDIATELY EVACUATE SECTOR 4 OUTPOSTS.",
        "",
        "EFFECTIVE AT 1800 HOURS, DUSK PROTOCOL IS MANDATORY:",
        "  1. DO NOT REMAIN IN THE BLACK PINES PAST SUNSET UNDER ANY",
        "     CIRCUMSTANCE. ALL MOTORIZED TRAILS ARE CLOSED AT MILE 9.",
        "  2. EXTENSIVE LARGE PREDATOR CARCASS MUTILATION HAS BEEN",
        "     CONFIRMED ACROSS THE EASTERN RIDGE CLEARED LOGGING CORRIDOR.",
        "  3. MULTIPLE AGGRESSIVE NOCTURNAL PROWLING ENCOUNTERS RECORDED.",
        "     SEVERAL STRIDE PATTERNS EXCEED NORMAL BIOLOGICAL CLASSIFICATION.",
        "  4. ALL SEARCH & RESCUE OPERATIONS ARE SUSPENDED UNTIL ARMED",
        "     STATE FISH & GAME REINFORCEMENTS ARRIVE FROM HIGHWAY 9.",
        "",
        "SECURE ALL EMERGENCY BROADCAST FREQUENCIES (CHANNEL 4 - 146.520 MHz).",
        "IF ISOLATED AFTER DARK: BARRICADE STATION, MAINTAIN FLASHLIGHT BATTERIES,",
        "AND DO NOT VENTURE INTO THE TREE LINE FOR UNIDENTIFIED VOCALIZATIONS."
    ]

    cur_y = 350
    for line in body_lines:
        draw.text((125, cur_y), line, fill=(40, 32, 24, 250), font=f_body)
        cur_y += 28

    # Signatures
    draw.line([(125, 840), (450, 840)], fill=(70, 55, 40, 220), width=1)
    draw.text((130, 850), "T. Hargrove, District Chief Warden", fill=(55, 45, 35, 255), font=f_sub)

    draw.line([(550, 840), (875, 840)], fill=(70, 55, 40, 220), width=1)
    draw.text((555, 850), "State Wildlife Forensic Bureau", fill=(55, 45, 35, 255), font=f_sub)

    # Angled Red Rubber Stamp: "DISTRICT RESTRICTED / LEVEL 4 HAZARD"
    stamp_img = Image.new("RGBA", (450, 180), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stamp_img)
    s_draw.rectangle([10, 10, 440, 170], outline=(180, 28, 24, 210), width=6)
    s_draw.rectangle([18, 18, 432, 162], outline=(180, 28, 24, 150), width=2)
    s_draw.text((225, 55), "RESTRICTED", fill=(185, 25, 20, 220), font=f_stamp, anchor="mm")
    s_draw.text((225, 115), "LEVEL 4 HAZARD", fill=(185, 25, 20, 220), font=get_font(FONT_SANS_BOLD, 30), anchor="mm")
    
    # Add stamp grit
    for _ in range(800):
        sx = random.randint(0, 449)
        sy = random.randint(0, 179)
        stamp_img.putpixel((sx, sy), (0, 0, 0, 0))
        
    stamp_rot = stamp_img.rotate(14.5, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(stamp_rot, (470, 620))

    img.save("assets/textures/documents/usfs_evacuation_notice.png")
    print("Saved assets/textures/documents/usfs_evacuation_notice.png")

# -----------------------------------------------------------------------------
# 2. Warden's Field Journal
# -----------------------------------------------------------------------------
def generate_field_journal():
    w, h = 1024, 1024
    # Open 2-page leather book
    img = Image.new("RGBA", (w, h), (45, 30, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Leather cover border
    for y in range(h):
        for x in range(w):
            if x < 40 or x > w - 40 or y < 40 or y > h - 40:
                draw.point((x, y), fill=(38 + (x % 5), 24 + (y % 4), 16, 255))

    # Pages background
    page_w = 440
    page_h = 920
    p1_rect = [60, 52, 500, 972]
    p2_rect = [524, 52, 964, 972]

    draw.rectangle(p1_rect, fill=(238, 228, 206, 255))
    draw.rectangle(p2_rect, fill=(235, 224, 200, 255))

    # Spine shadow in middle
    for dx in range(-15, 16):
        alpha = int(90 * (1.0 - abs(dx) / 16.0))
        draw.line([(512 + dx, 52), (512 + dx, 972)], fill=(40, 28, 18, alpha))

    # Ruled lines on left page
    for ly in range(120, 930, 32):
        draw.line([(85, ly), (480, ly)], fill=(185, 195, 210, 140), width=1)
    draw.line([(120, 75), (120, 950)], fill=(225, 170, 170, 180), width=1)

    f_title = get_font(FONT_SERIF_BOLD, 22)
    f_hand = get_font(FONT_SERIF, 17)
    f_hand_sm = get_font(FONT_SERIF, 14)

    # Left Page Text (Handwritten Journal)
    draw.text((135, 85), "SECTOR 4 LOG — OCT 26 - 31", fill=(60, 42, 28, 255), font=f_title)

    entries = [
        ("Oct 26:", "Heavy freezing rain. Dogs refused to step"),
        ("", "past the woodpile. Deep timber thumping"),
        ("", "heard near Ridge 2 at 0200 hrs."),
        ("Oct 28:", "Found full bull elk snapped clean at"),
        ("", "the mid-spine. No powder burns. Claw gouges"),
        ("", "measured 7.8 inches across the flanks."),
        ("Oct 29:", "Imprints found in muddy trail bed:"),
        ("", "18.5 inches long, 7.2 wide. Deep heel sink"),
        ("", "indicates weight easily topping 800 lbs."),
        ("Oct 31:", "Power line to outpost was torn down from"),
        ("", "a 12-foot crossarm. It wasn't a fallen tree."),
        ("", "Something was looking in through the north"),
        ("", "eave window tonight. Heavy breath on the glass.")
    ]

    ey = 126
    for tag, text in entries:
        if tag:
            draw.text((85, ey), tag, fill=(130, 35, 25, 255), font=f_hand)
        draw.text((135, ey), text, fill=(45, 38, 32, 240), font=f_hand)
        ey += 32

    # Right Page: Rough anatomical field sketch of track and clawed tree
    draw.text((550, 85), "FIELD EVIDENCE SKETCHES", fill=(60, 42, 28, 255), font=f_title)
    
    # Clawed bark diagram
    draw.rectangle([560, 140, 920, 440], outline=(140, 120, 95, 180), width=1)
    draw.text((575, 155), "FIG 1: Resin seep & 4-finger bark tear", fill=(70, 55, 40, 255), font=f_hand_sm)
    # 4 curved claw gouges sketched
    for ci in range(4):
        cx = 660 + ci * 38
        draw.line([(cx, 210), (cx + 8, 300), (cx - 4, 380)], fill=(90, 45, 30, 220), width=4)
        draw.line([(cx - 1, 212), (cx + 7, 302)], fill=(50, 25, 15, 255), width=2)

    # Footprint sketch
    draw.rectangle([560, 480, 920, 920], outline=(140, 120, 95, 180), width=1)
    draw.text((575, 495), "FIG 2: Cast of left plantigrade track", fill=(70, 55, 40, 255), font=f_hand_sm)
    
    # Footprint outline shape
    fx, fy = 730, 720
    draw.ellipse([fx - 65, fy - 140, fx + 65, fy + 120], outline=(80, 60, 45, 220), width=3) # Main sole
    draw.ellipse([fx - 50, fy + 60, fx + 50, fy + 160], outline=(80, 60, 45, 220), width=3) # Heel
    # 5 broad toes
    for ti in range(5):
        tx = fx - 50 + ti * 25
        ty = fy - 165 - abs(ti - 2) * 5
        draw.ellipse([tx - 11, ty - 16, tx + 11, ty + 16], fill=(110, 85, 65, 160), outline=(70, 50, 35, 240), width=2)

    draw.text((580, 875), "Scale: 18.5\" x 7.2\" (Est. 850 lbs)", fill=(120, 35, 25, 255), font=f_hand_sm)

    img.save("assets/textures/documents/warden_field_journal.png")
    print("Saved assets/textures/documents/warden_field_journal.png")

# -----------------------------------------------------------------------------
# 3. Black Pines Topographic Survey Map
# -----------------------------------------------------------------------------
def generate_topographic_map():
    w, h = 1024, 1024
    img = Image.new("RGBA", (w, h), (232, 225, 204, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    add_paper_grain(draw, w, h, (232, 225, 204))
    add_folds(draw, w, h)

    # Grid lines (UTM coordinate grid)
    for x in range(80, w - 80, 110):
        draw.line([(x, 80), (x, h - 80)], fill=(160, 175, 160, 90), width=1)
    for y in range(80, h - 80, 110):
        draw.line([(80, y), (w - 80, y)], fill=(160, 175, 160, 90), width=1)

    # Contour lines (elevation curves)
    random.seed(101)
    for elevation in range(120, 880, 45):
        pts = []
        for x in range(80, w - 80, 40):
            wobble = math.sin(x * 0.015 + elevation * 0.02) * 50.0 + math.cos(x * 0.03) * 25.0
            pts.append((x, elevation + wobble))
        for p in range(len(pts) - 1):
            is_index = (elevation % 90 == 0)
            col = (145, 105, 75, 200 if is_index else 110)
            draw.line([pts[p], pts[p+1]], fill=col, width=2 if is_index else 1)

    # River / Creek (meandering blue line)
    river_pts = []
    for y in range(80, h - 80, 20):
        rx = 480 + math.sin(y * 0.012) * 120.0 + math.cos(y * 0.035) * 35.0
        river_pts.append((rx, y))
    for p in range(len(river_pts) - 1):
        draw.line([river_pts[p], river_pts[p+1]], fill=(65, 115, 160, 220), width=4)

    # Legend & Title
    f_map_title = get_font(FONT_SANS_BOLD, 26)
    f_map_sm = get_font(FONT_SERIF, 15)
    f_pencil = get_font(FONT_SANS_BOLD, 20)

    draw.rectangle([90, 90, 520, 180], fill=(245, 240, 225, 230), outline=(80, 70, 60, 220), width=2)
    draw.text((105, 105), "THE BLACK PINES SURVEY DISTRICT", fill=(40, 35, 30, 255), font=f_map_title)
    draw.text((105, 140), "QUADRANGLE 1:24,000 • CASCADE FORESTRY DIVISION", fill=(60, 50, 40, 255), font=f_map_sm)

    # Red grease-pencil marked points of interest
    # Ranger Station #4
    sx, sy = 512, 620
    draw.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], outline=(205, 35, 25, 240), width=4)
    draw.text((sx + 24, sy - 12), "STATION 04 (LAST CONTACT)", fill=(195, 25, 20, 255), font=f_pencil)

    # Trail of sightings / danger zone
    draw.line([(sx, sy), (sx - 120, sy - 90), (sx - 210, sy - 160)], fill=(205, 35, 25, 200), width=3)
    draw.text((sx - 260, sy - 190), "CARCASS KILL SITE", fill=(195, 25, 20, 255), font=f_pencil)

    # Egress road
    draw.text((680, 890), "HIGHWAY 9 EVAC ROUTE -->", fill=(30, 80, 30, 255), font=f_pencil)

    img.save("assets/textures/documents/black_pines_topomap.png")
    print("Saved assets/textures/documents/black_pines_topomap.png")

if __name__ == "__main__":
    generate_evacuation_notice()
    generate_field_journal()
    generate_topographic_map()
    print("All documents generated successfully.")
