import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_parchment_base(width, height, base_color=(235, 225, 200)):
    img = Image.new("RGBA", (width, height), base_color + (255,))
    draw = ImageDraw.Draw(img)

    # Add subtle aged noise and stains
    for _ in range(12000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        shade = random.randint(-18, 18)
        c = (
            max(0, min(255, base_color[0] + shade)),
            max(0, min(255, base_color[1] + shade)),
            max(0, min(255, base_color[2] + shade)),
            random.randint(40, 120)
        )
        draw.point((x, y), fill=c)

    # Aged vignette around edges
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for i in range(60):
        dist = i * 2.5
        alpha = int((1.0 - (i / 60.0)) * 65)
        v_draw.rectangle([dist, dist, width - dist, height - dist], outline=(140, 110, 75, alpha), width=3)

    img = Image.alpha_composite(img, vignette)
    return img

def generate_evacuation_notice_texture(out_path):
    w, h = 1024, 1024
    img = create_parchment_base(w, h, (240, 230, 210))
    draw = ImageDraw.Draw(img)

    # Header border
    draw.rectangle([60, 60, w - 60, h - 60], outline=(80, 50, 30, 200), width=6)
    draw.rectangle([70, 70, w - 70, h - 70], outline=(80, 50, 30, 120), width=2)

    # Top USFS Shield Badge (Green shield icon)
    shield_pts = [
        (w//2 - 60, 100),
        (w//2 + 60, 100),
        (w//2 + 50, 180),
        (w//2, 220),
        (w//2 - 50, 180)
    ]
    draw.polygon(shield_pts, fill=(35, 75, 45, 230), outline=(20, 45, 25, 255))
    draw.text((w//2 - 32, 135), "U S", fill=(240, 235, 210, 255))
    draw.text((w//2 - 12, 165), "FS", fill=(240, 235, 210, 255))

    # Department and Region
    draw.text((w//2 - 290, 245), "UNITED STATES DEPARTMENT OF AGRICULTURE", fill=(40, 35, 30, 240))
    draw.text((w//2 - 250, 275), "FOREST SERVICE — CASCADE NATIONAL DISTRICT", fill=(50, 45, 35, 230))
    draw.line([(120, 310), (w - 120, 310)], fill=(80, 50, 30, 200), width=3)

    # Bold Red Emergency Header
    draw.rectangle([110, 330, w - 110, 400], fill=(165, 30, 25, 240))
    draw.text((w//2 - 280, 345), "EMERGENCY EVACUATION ORDER", fill=(255, 245, 235, 255))

    # Notice Metadata
    draw.text((120, 420), "STATION: #04 (BLACK PINE RIDGE)", fill=(50, 40, 30, 230))
    draw.text((w - 380, 420), "EFFECTIVE: IMMEDIATELY", fill=(160, 30, 25, 240))
    draw.line([(120, 450), (w - 120, 450)], fill=(120, 90, 70, 150), width=2)

    # Body Text (Typewriter Style layout)
    lines = [
        "DISTRICT CLOSED INDEFINITELY BY ORDER OF THE REGIONAL FORESTER.",
        "",
        "All USFS research personnel, game wardens, and backcountry campers are ordered",
        "to fall back to the Highway 9 staging checkpoint without delay.",
        "",
        "HAZARD WARNING — CODE ORANGE:",
        "- Multiple catastrophic animal mutilations documented along the drainage creek.",
        "- Adult bull elk snapped clean at the cervical vertebrae; deep claws in pine bark.",
        "- Large bipedal apex stalker tracked in perimeter timber after 19:00 hours.",
        "- Severe structural claw gouges observed on the ranger station porch and sill.",
        "",
        "DO NOT ENTER THE PINES AFTER DUSK UNDER ANY CIRCUMSTANCES.",
        "Keep road flares lit and armed. If confronted, do not sprint.",
    ]

    cur_y = 475
    for line in lines:
        if "HAZARD WARNING" in line or "DO NOT ENTER" in line:
            draw.text((120, cur_y), line, fill=(165, 25, 20, 255))
        else:
            draw.text((120, cur_y), line, fill=(35, 30, 25, 235))
        cur_y += 30

    # Official Angled Red Stamp: "EVACUATED / ACCESS PROHIBITED"
    stamp_img = Image.new("RGBA", (450, 120), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stamp_img)
    s_draw.rectangle([10, 10, 440, 110], outline=(190, 30, 25, 220), width=6)
    s_draw.rectangle([16, 16, 434, 104], outline=(190, 30, 25, 140), width=2)
    s_draw.text((45, 30), "EVACUATED", fill=(190, 30, 25, 230))
    s_draw.text((55, 65), "DISTRICT CLOSED", fill=(190, 30, 25, 210))
    stamp_rotated = stamp_img.rotate(14, expand=True)

    img.paste(stamp_rotated, (w - 480, h - 250), stamp_rotated)

    # Signature block
    draw.text((120, h - 130), "APPROVED: Warden T. MacReady, District Supervisor", fill=(45, 40, 35, 230))
    draw.line([(120, h - 140), (450, h - 140)], fill=(70, 55, 40, 200), width=1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"[Texture] Generated Evacuation Notice PBR Texture -> {out_path}")

def generate_field_journal_texture(out_path):
    w, h = 1024, 1024
    img = create_parchment_base(w, h, (230, 220, 195))
    draw = ImageDraw.Draw(img)

    # Center book spine fold
    draw.line([(w//2, 40), (w//2, h - 40)], fill=(120, 90, 60, 180), width=8)
    draw.line([(w//2 - 6, 40), (w//2 - 6, h - 40)], fill=(90, 70, 45, 120), width=3)
    draw.line([(w//2 + 6, 40), (w//2 + 6, h - 40)], fill=(90, 70, 45, 120), width=3)

    # Notebook ruled faint lines
    for ly in range(120, h - 80, 38):
        draw.line([(60, ly), (w//2 - 30, ly)], fill=(160, 180, 200, 60), width=1)
        draw.line([(w//2 + 30, ly), (w - 60, ly)], fill=(160, 180, 200, 60), width=1)

    # Left Page: Hand-sketched 18.5" Footprint
    draw.text((80, 80), "SPECIMEN #14 — CREEK BED IMPRINT", fill=(60, 45, 30, 230))
    # Footprint sketch outline
    foot_pts = [
        (160, 320), (220, 260), (280, 270), (330, 340), (340, 480),
        (310, 600), (260, 700), (220, 710), (180, 690), (150, 580),
        (140, 440), (145, 360)
    ]
    draw.polygon(foot_pts, fill=(160, 140, 110, 120), outline=(80, 60, 40, 220))
    # 5 Toes
    for idx, (tx, ty, tr) in enumerate([(155, 230, 24), (200, 210, 26), (245, 205, 28), (290, 215, 30), (335, 235, 34)]):
        draw.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=(160, 140, 110, 140), outline=(80, 60, 40, 220))
    draw.text((80, 750), "L: 18.5 in  |  W: 7.4 in", fill=(70, 50, 30, 240))
    draw.text((80, 790), "Pressure ridges match 800+ lb biped.", fill=(90, 35, 30, 240))

    # Right Page: Handwritten Field Notes
    right_notes = [
        "OCTOBER 28:",
        "Found bull elk snapped clean at spine.",
        "Claw gouges 7.8 inches across flanks.",
        "Internal organs missing.",
        "",
        "OCTOBER 29:",
        "Tracks in damp sand near creek.",
        "Stride length exceeds 5.2 feet.",
        "Distinct sulfur/rotting musk in air.",
        "",
        "OCTOBER 31 — 22:45:",
        "HEAVY BREATHING AT NORTH WINDOW.",
        "Eyes caught in lantern beam: deep amber.",
        "Height above ground: nearly 9 feet.",
        "Fired 3 rounds from .30-06. It didn't flinch.",
        "Radioed dispatcher. Leaving station now."
    ]
    ry = 90
    for rline in right_notes:
        if "OCTOBER 31" in rline or "HEAVY BREATHING" in rline:
            draw.text((w//2 + 40, ry), rline, fill=(160, 30, 25, 255))
        else:
            draw.text((w//2 + 40, ry), rline, fill=(40, 35, 45, 235))
        ry += 42

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"[Texture] Generated Field Journal PBR Texture -> {out_path}")

def generate_topomap_texture(out_path):
    w, h = 1024, 1024
    img = create_parchment_base(w, h, (238, 232, 214))
    draw = ImageDraw.Draw(img)

    # Topo Header
    draw.text((80, 50), "USGS 7.5 MINUTE QUADRANGLE — THE BLACK PINES DISTRICT", fill=(50, 45, 40, 240))
    draw.line([(80, 80), (w - 80, 80)], fill=(80, 60, 40, 200), width=2)

    # Topographic elevation contour lines (Brown undulating rings)
    for r in range(80, 480, 35):
        box = [w//2 - r, h//2 - r * 0.8, w//2 + r, h//2 + r * 0.8]
        draw.arc(box, start=0, end=360, fill=(160, 115, 75, 140), width=2)

    # Winding Creek Line (Blue)
    creek_pts = [
        (120, 100), (220, 260), (310, 420), (450, 560), (620, 680), (780, 820), (920, 960)
    ]
    for i in range(len(creek_pts) - 1):
        draw.line([creek_pts[i], creek_pts[i+1]], fill=(60, 110, 160, 200), width=4)
    draw.text((320, 390), "Deadwood Creek", fill=(40, 90, 140, 220))

    # Red grease-pencil circles & markings
    # Station 04
    draw.ellipse([460, 580, 560, 680], outline=(200, 30, 25, 240), width=5)
    draw.text((430, 695), "RANGER STATION #04", fill=(190, 25, 20, 255))
    draw.text((455, 725), "[LAST CONTACT]", fill=(190, 25, 20, 255))

    # Carcass Kill Site
    draw.ellipse([210, 240, 310, 340], outline=(200, 30, 25, 240), width=5)
    draw.text((180, 355), "CARCASS KILL SITE", fill=(190, 25, 20, 255))

    # Trail track
    draw.line([(480, 600), (280, 320)], fill=(190, 30, 25, 180), width=3)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"[Texture] Generated Topo Map PBR Texture -> {out_path}")

if __name__ == "__main__":
    tex_dir = "/home/m3tal/apps/the-black-pines/assets/textures"
    generate_evacuation_notice_texture(os.path.join(tex_dir, "prop_doc_evacuation_notice.png"))
    generate_field_journal_texture(os.path.join(tex_dir, "prop_doc_field_journal.png"))
    generate_topomap_texture(os.path.join(tex_dir, "prop_doc_topomap.png"))
