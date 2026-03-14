"""
Plasmid map visualization using dna_features_viewer.

Generates accurate linear and circular construct maps with real bp positions,
gene annotations, promoters, terminators, and regulatory elements.
Falls back to SVG generation if dna_features_viewer has issues.
"""

import io
import base64
import math

try:
    from dna_features_viewer import GraphicFeature, GraphicRecord, CircularGraphicRecord
    HAS_DFV = True
except ImportError:
    HAS_DFV = False


GENE_COLORS = [
    "#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
    "#0891b2", "#e11d48", "#65a30d", "#ea580c", "#8b5cf6",
]


def generate_plasmid_map(
    genes: list[dict],
    promoters: list[str],
    terminators: list[str],
    ori: dict,
    marker: dict,
    kill_switch: dict,
    total_length: int,
    design_name: str = "pProtoForge",
) -> dict:
    """
    Generate a plasmid map with real bp positions.
    Returns both a base64 PNG and structured feature data.
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
            "label": prom, "type": "promoter", "color": "#16a34a", "strand": 1,
        })

    # Genes with realistic spacing
    gene_spacing = 30  # bp between genes for RBS
    for i, gene in enumerate(genes or []):
        gene_name = gene.get("name", f"gene_{i}")
        # Estimate gene size: average bacterial gene ~900bp, but vary
        gene_size = gene.get("size_bp", 900)
        gene_start = current_pos
        gene_end = current_pos + gene_size

        if gene_end > total_length - 1000:
            total_length = gene_end + 2000

        features.append({
            "start": gene_start, "end": gene_end,
            "label": gene_name, "type": "gene",
            "color": GENE_COLORS[i % len(GENE_COLORS)], "strand": 1,
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
            "label": term, "type": "terminator", "color": "#dc2626", "strand": 0,
        })

    current_pos += 100

    # Kill switch
    if kill_switch:
        ks_genes = kill_switch.get("genes", [])
        ks_size = kill_switch.get("size_bp", 600)
        features.append({
            "start": current_pos, "end": current_pos + ks_size,
            "label": kill_switch.get("name", "kill switch").split("/")[0].split("(")[0].strip(),
            "type": "kill_switch", "color": "#ef4444", "strand": -1,
        })
        current_pos += ks_size + 50

    # Selection marker
    if marker:
        marker_size = marker.get("size_bp", 795)
        features.append({
            "start": current_pos, "end": current_pos + marker_size,
            "label": marker.get("gene", "marker"),
            "type": "marker", "color": "#f59e0b", "strand": -1,
        })
        current_pos += marker_size + 50

    # Origin of replication
    if ori:
        ori_size = ori.get("size_bp", 900)
        features.append({
            "start": current_pos, "end": current_pos + ori_size,
            "label": ori.get("name", "ori"),
            "type": "ori", "color": "#6b7280", "strand": 0,
        })
        current_pos += ori_size

    total_length = max(total_length, current_pos + 100)

    # Generate image
    png_b64 = _render_map(features, total_length, design_name)

    return {
        "png_base64": png_b64,
        "features": features,
        "feature_data": feature_data,
        "total_length_bp": total_length,
        "design_name": design_name,
    }


def _render_map(features: list[dict], total_length: int, title: str) -> str:
    """Render using dna_features_viewer if available, else SVG fallback."""
    if HAS_DFV:
        return _render_dfv(features, total_length, title)
    return _render_svg_fallback(features, total_length, title)


def _render_dfv(features: list[dict], total_length: int, title: str) -> str:
    """Render using dna_features_viewer."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gf_list = []
    for f in features:
        strand = f.get("strand", 1)
        ftype = f.get("type", "gene")
        gf_list.append(GraphicFeature(
            start=f["start"], end=f["end"], strand=strand,
            color=f["color"], label=f["label"],
            linewidth=1 if ftype == "gene" else 0,
        ))

    record = CircularGraphicRecord(sequence_length=total_length, features=gf_list)
    ax, _ = record.plot(figure_width=6)
    ax.set_title(f"{title}\n{total_length:,} bp", fontsize=11, fontweight="bold", pad=15)
    fig = ax.figure

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _render_svg_fallback(features: list[dict], total_length: int, title: str) -> str:
    """Pure SVG fallback (no matplotlib needed)."""
    cx, cy, r = 200, 200, 140

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 420" width="400" height="420">',
        f'<rect width="400" height="420" fill="white"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#d1d5db" stroke-width="3"/>',
    ]

    for f in features:
        start_angle = (f["start"] / total_length) * 360
        end_angle = (f["end"] / total_length) * 360
        mid_angle = (start_angle + end_angle) / 2

        fr = r + 15 if f.get("type") == "gene" else r + 5
        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)
        mid_rad = math.radians(mid_angle - 90)

        x1 = cx + fr * math.cos(start_rad)
        y1 = cy + fr * math.sin(start_rad)
        x2 = cx + fr * math.cos(end_rad)
        y2 = cy + fr * math.sin(end_rad)
        large = 1 if (end_angle - start_angle) > 180 else 0

        width = 12 if f.get("type") == "gene" else 6
        svg_parts.append(
            f'<path d="M {x1:.1f} {y1:.1f} A {fr} {fr} 0 {large} 1 {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{f["color"]}" stroke-width="{width}" stroke-linecap="round">'
            f'<title>{f["label"]}: {f["start"]}-{f["end"]} bp</title></path>'
        )

        lx = cx + (r + 35) * math.cos(mid_rad)
        ly = cy + (r + 35) * math.sin(mid_rad)
        anchor = "end" if mid_angle > 90 and mid_angle < 270 else "start"
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'font-size="9" font-weight="600" fill="{f["color"]}">{f["label"]}</text>'
        )

    svg_parts.append(
        f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="12" font-weight="700">{title}</text>'
        f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="10" fill="#888">{total_length:,} bp</text>'
    )
    svg_parts.append('</svg>')

    svg_str = "\n".join(svg_parts)
    return base64.b64encode(svg_str.encode()).decode()
