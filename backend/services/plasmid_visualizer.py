"""
Plasmid map visualization — clean, modern circular construct maps.

Generates SVG-based circular plasmid maps with real bp positions,
gene annotations, promoters, terminators, and regulatory elements.
Designed for both web display and Product Hunt screenshots.
"""

import io
import base64
import math


# Modern color palette — accessible, distinct, looks good on white
FEATURE_STYLES = {
    "gene": {
        "colors": [
            "#3B82F6",  # blue
            "#10B981",  # emerald
            "#F59E0B",  # amber
            "#8B5CF6",  # violet
            "#EF4444",  # red
            "#06B6D4",  # cyan
            "#EC4899",  # pink
            "#84CC16",  # lime
            "#F97316",  # orange
            "#6366F1",  # indigo
        ],
        "track": "outer",
        "width": 18,
        "label_weight": "600",
    },
    "promoter": {
        "color": "#22C55E",
        "track": "inner",
        "width": 8,
        "label_weight": "500",
    },
    "terminator": {
        "color": "#EF4444",
        "track": "inner",
        "width": 8,
        "label_weight": "500",
    },
    "kill_switch": {
        "color": "#DC2626",
        "track": "middle",
        "width": 14,
        "label_weight": "600",
    },
    "marker": {
        "color": "#F59E0B",
        "track": "middle",
        "width": 14,
        "label_weight": "600",
    },
    "ori": {
        "color": "#9CA3AF",
        "track": "middle",
        "width": 14,
        "label_weight": "600",
    },
}


def generate_plasmid_map(
    genes: list[dict],
    promoters: list[str],
    terminators: list[str],
    ori: dict,
    marker: dict,
    kill_switch: dict,
    total_length: int,
    design_name: str = "pProgenx",
) -> dict:
    """
    Generate a plasmid map with real bp positions.
    Returns both a base64 SVG and structured feature data.
    """
    if total_length < 500:
        total_length = 5000

    # Build feature list with real bp positions
    features = []
    feature_data = []
    current_pos = 100  # start after promoter region

    # Promoter region
    for i, prom in enumerate(promoters or []):
        prom_start = 20 + i * 60
        prom_end = prom_start + 50
        features.append({
            "start": prom_start, "end": prom_end,
            "label": prom, "type": "promoter", "strand": 1,
        })

    # Genes with realistic spacing
    gene_spacing = 30  # bp between genes for RBS
    for i, gene in enumerate(genes or []):
        gene_name = gene.get("name", f"gene_{i}")
        gene_size = gene.get("size_bp", 900)
        gene_start = current_pos
        gene_end = current_pos + gene_size

        if gene_end > total_length - 1000:
            total_length = gene_end + 2000

        features.append({
            "start": gene_start, "end": gene_end,
            "label": gene_name, "type": "gene",
            "color_index": i, "strand": 1,
        })
        feature_data.append({
            "name": gene_name,
            "start": gene_start,
            "end": gene_end,
            "size_bp": gene_size,
            "function": gene.get("function", ""),
            "source": gene.get("source_organism", ""),
        })
        current_pos = gene_end + gene_spacing

    # Terminator
    for i, term in enumerate(terminators or []):
        term_start = current_pos + i * 40
        term_end = term_start + 30
        features.append({
            "start": term_start, "end": term_end,
            "label": term, "type": "terminator", "strand": 0,
        })

    current_pos += 100

    # Kill switch
    if kill_switch:
        ks_size = kill_switch.get("size_bp", 600)
        features.append({
            "start": current_pos, "end": current_pos + ks_size,
            "label": kill_switch.get("name", "kill switch").split("/")[0].split("(")[0].strip(),
            "type": "kill_switch", "strand": -1,
        })
        current_pos += ks_size + 50

    # Selection marker
    if marker:
        marker_size = marker.get("size_bp", 795)
        features.append({
            "start": current_pos, "end": current_pos + marker_size,
            "label": marker.get("gene", "marker"),
            "type": "marker", "strand": -1,
        })
        current_pos += marker_size + 50

    # Origin of replication
    if ori:
        ori_size = ori.get("size_bp", 900)
        features.append({
            "start": current_pos, "end": current_pos + ori_size,
            "label": ori.get("name", "ori"),
            "type": "ori", "strand": 0,
        })
        current_pos += ori_size

    total_length = max(total_length, current_pos + 100)

    # Generate SVG
    svg_b64 = _render_svg(features, total_length, design_name)

    return {
        "png_base64": svg_b64,  # key kept as png_base64 for frontend compat
        "features": features,
        "feature_data": feature_data,
        "total_length_bp": total_length,
        "design_name": design_name,
    }


def _get_feature_color(feature: dict) -> str:
    """Get the color for a feature based on its type and index."""
    ftype = feature.get("type", "gene")
    style = FEATURE_STYLES.get(ftype, FEATURE_STYLES["gene"])

    if ftype == "gene":
        idx = feature.get("color_index", 0)
        colors = style["colors"]
        return colors[idx % len(colors)]
    return style.get("color", "#9CA3AF")


def _get_feature_track_radius(feature: dict, base_r: float) -> float:
    """Get the radius for a feature based on its track."""
    ftype = feature.get("type", "gene")
    style = FEATURE_STYLES.get(ftype, FEATURE_STYLES["gene"])
    track = style.get("track", "outer")

    if track == "outer":
        return base_r + 2
    elif track == "inner":
        return base_r - 14
    else:  # middle
        return base_r - 6


def _get_feature_width(feature: dict) -> int:
    """Get stroke width for a feature."""
    ftype = feature.get("type", "gene")
    style = FEATURE_STYLES.get(ftype, FEATURE_STYLES["gene"])
    return style.get("width", 12)


def _angle_for_bp(bp: int, total: int) -> float:
    """Convert base pair position to angle in degrees (0 = top)."""
    return (bp / total) * 360


def _polar_to_xy(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    """Convert polar coordinates to SVG x,y. Angle 0 = top (12 o'clock)."""
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def _arc_path(cx: float, cy: float, r: float, start_deg: float, end_deg: float) -> str:
    """Generate SVG arc path data."""
    x1, y1 = _polar_to_xy(cx, cy, r, start_deg)
    x2, y2 = _polar_to_xy(cx, cy, r, end_deg)
    span = end_deg - start_deg
    large = 1 if span > 180 else 0
    return f"M {x1:.1f} {y1:.1f} A {r:.1f} {r:.1f} 0 {large} 1 {x2:.1f} {y2:.1f}"


def _render_svg(features: list[dict], total_length: int, title: str) -> str:
    """Render a clean, modern circular plasmid map as SVG."""
    # Canvas dimensions
    w, h = 520, 580
    cx, cy = w / 2, 260
    base_r = 150

    svg = []
    font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
               f'width="{w}" height="{h}" font-family="{font_family}">')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FAFAFA" rx="12"/>')

    # Title
    svg.append(f'<text x="{cx}" y="32" text-anchor="middle" font-size="16" '
               f'font-weight="700" fill="#111827">{_escape(title)}</text>')
    svg.append(f'<text x="{cx}" y="52" text-anchor="middle" font-size="12" '
               f'fill="#6B7280">{total_length:,} bp</text>')

    # Backbone circle (thin, subtle)
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{base_r}" '
               f'fill="none" stroke="#E5E7EB" stroke-width="2"/>')

    # Separate features by type for layered rendering
    genes = [f for f in features if f["type"] == "gene"]
    infrastructure = [f for f in features if f["type"] in ("ori", "marker", "kill_switch")]
    regulatory = [f for f in features if f["type"] in ("promoter", "terminator")]

    # Render infrastructure first (bottom layer)
    for f in infrastructure:
        _draw_arc_feature(svg, f, cx, cy, base_r, total_length)

    # Render regulatory elements
    for f in regulatory:
        _draw_arc_feature(svg, f, cx, cy, base_r, total_length)

    # Render genes on top
    for f in genes:
        _draw_arc_feature(svg, f, cx, cy, base_r, total_length)

    # Labels (placed after all arcs to be on top)
    label_positions = []
    for f in features:
        _draw_label(svg, f, cx, cy, base_r, total_length, label_positions)

    # Center info
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="45" fill="white" stroke="#F3F4F6" stroke-width="1"/>')
    svg.append(f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-size="10" '
               f'font-weight="600" fill="#374151">Circular</text>')
    svg.append(f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="9" '
               f'fill="#9CA3AF">construct</text>')

    # Legend
    _draw_legend(svg, features, w, h)

    svg.append('</svg>')
    svg_str = "\n".join(svg)
    return base64.b64encode(svg_str.encode()).decode()


def _draw_arc_feature(svg: list, feature: dict, cx: float, cy: float,
                      base_r: float, total_length: int):
    """Draw a feature as an arc on the circular map."""
    start_deg = _angle_for_bp(feature["start"], total_length)
    end_deg = _angle_for_bp(feature["end"], total_length)
    color = _get_feature_color(feature)
    r = _get_feature_track_radius(feature, base_r)
    width = _get_feature_width(feature)

    # Draw arc
    path = _arc_path(cx, cy, r, start_deg, end_deg)
    opacity = "0.9" if feature["type"] == "gene" else "0.75"
    svg.append(
        f'<path d="{path}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round" opacity="{opacity}">'
        f'<title>{_escape(feature["label"])}: {feature["start"]:,}-{feature["end"]:,} bp</title>'
        f'</path>'
    )

    # Direction arrow for genes
    if feature["type"] == "gene" and (end_deg - start_deg) > 8:
        arrow_deg = end_deg - 2
        ax, ay = _polar_to_xy(cx, cy, r, arrow_deg)
        # Small arrowhead
        a1x, a1y = _polar_to_xy(cx, cy, r - 6, arrow_deg - 4)
        a2x, a2y = _polar_to_xy(cx, cy, r + 6, arrow_deg - 4)
        svg.append(
            f'<polygon points="{ax:.1f},{ay:.1f} {a1x:.1f},{a1y:.1f} {a2x:.1f},{a2y:.1f}" '
            f'fill="{color}" opacity="0.9"/>'
        )


def _draw_label(svg: list, feature: dict, cx: float, cy: float,
                base_r: float, total_length: int, existing: list):
    """Draw a label for a feature with smart positioning."""
    start_deg = _angle_for_bp(feature["start"], total_length)
    end_deg = _angle_for_bp(feature["end"], total_length)
    mid_deg = (start_deg + end_deg) / 2

    # Skip labels for very small features (< 3 degrees)
    if (end_deg - start_deg) < 3 and feature["type"] != "gene":
        return

    # Label placement radius
    ftype = feature["type"]
    if ftype == "gene":
        label_r = base_r + 35
    elif ftype in ("ori", "marker", "kill_switch"):
        label_r = base_r + 28
    else:
        label_r = base_r + 25

    # Adjust label position to avoid overlaps
    for ex_deg, ex_r in existing:
        if abs(mid_deg - ex_deg) < 15 and abs(label_r - ex_r) < 20:
            label_r += 18

    existing.append((mid_deg, label_r))

    lx, ly = _polar_to_xy(cx, cy, label_r, mid_deg)

    # Text anchor based on position
    if 45 < mid_deg < 135:
        anchor = "start"
    elif 225 < mid_deg < 315:
        anchor = "end"
    elif mid_deg >= 135 and mid_deg <= 225:
        anchor = "end"
    else:
        anchor = "start"

    color = _get_feature_color(feature)
    style = FEATURE_STYLES.get(ftype, FEATURE_STYLES["gene"])
    weight = style.get("label_weight", "500")
    size = "10" if ftype == "gene" else "9"

    # Draw connector line
    conn_r = _get_feature_track_radius(feature, base_r)
    conn_r += _get_feature_width(feature) / 2 + 2
    cx2, cy2 = _polar_to_xy(cx, cy, conn_r, mid_deg)
    svg.append(
        f'<line x1="{cx2:.1f}" y1="{cy2:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" '
        f'stroke="{color}" stroke-width="0.75" opacity="0.4"/>'
    )

    # Draw label text
    svg.append(
        f'<text x="{lx:.1f}" y="{ly + 3:.1f}" text-anchor="{anchor}" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">'
        f'{_escape(feature["label"])}</text>'
    )


def _draw_legend(svg: list, features: list, w: float, h: float):
    """Draw a compact legend at the bottom."""
    # Collect unique feature types
    types_seen = []
    type_colors = {}
    for f in features:
        ftype = f["type"]
        if ftype not in types_seen:
            types_seen.append(ftype)
            type_colors[ftype] = _get_feature_color(f)

    if not types_seen:
        return

    # Layout legend items horizontally
    type_labels = {
        "gene": "Genes",
        "promoter": "Promoters",
        "terminator": "Terminators",
        "ori": "Origin",
        "marker": "Marker",
        "kill_switch": "Kill Switch",
    }

    y = h - 30
    total_items = len(types_seen)
    item_width = min(90, (w - 40) / total_items)
    start_x = (w - total_items * item_width) / 2

    for i, ftype in enumerate(types_seen):
        x = start_x + i * item_width
        color = type_colors[ftype]
        label = type_labels.get(ftype, ftype.title())

        # Color dot
        svg.append(f'<circle cx="{x + 6}" cy="{y}" r="4" fill="{color}" opacity="0.8"/>')
        # Label
        svg.append(
            f'<text x="{x + 14}" y="{y + 3.5}" font-size="9" fill="#6B7280">'
            f'{label}</text>'
        )


def _escape(text: str) -> str:
    """Escape text for SVG XML."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
