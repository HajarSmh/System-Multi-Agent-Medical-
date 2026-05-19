# backend/app/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io


def generate_pdf(final_report: str, thread_id: str) -> bytes:
    """
    Génère un PDF à partir du rapport final texte.
    Retourne les bytes du PDF prêts à être envoyés ou sauvegardés.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Rapport d'Orientation Clinique Préliminaire",
        author="Système Multi-Agents Médical"
    )

    styles = getSampleStyleSheet()

    # ── Styles personnalisés ─────────────────────────────────────────
    style_title = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    style_h1 = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.HexColor("#2E75B6"),
        spaceBefore=16,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )
    style_h2 = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2F5597"),
        spaceBefore=12,
        spaceAfter=4,
        fontName="Helvetica-Bold"
    )
    style_body = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName="Helvetica"
    )
    style_warning = ParagraphStyle(
        "Warning",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#C0392B"),
        backColor=colors.HexColor("#FDECEA"),
        borderPadding=(6, 6, 6, 6),
        spaceAfter=6,
        spaceBefore=12,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    style_meta = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
        fontName="Helvetica"
    )

    # ── Construction du contenu ──────────────────────────────────────
    story = []

    # En-tête
    story.append(Paragraph("🏥 RAPPORT D'ORIENTATION CLINIQUE PRÉLIMINAIRE", style_title))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2E75B6")))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Référence de consultation : {thread_id}", style_meta))
    story.append(Spacer(1, 0.5 * cm))

    # Parser le rapport texte ligne par ligne
    for line in final_report.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2 * cm))
            continue

        # Titres markdown → styles PDF
        if line.startswith("## "):
            story.append(Paragraph(line.replace("## ", ""), style_h1))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                     color=colors.HexColor("#CCCCCC")))
        elif line.startswith("### "):
            story.append(Paragraph(line.replace("### ", ""), style_h2))
        elif line.startswith("⚠️") or "ne remplace pas" in line.lower():
            story.append(Paragraph(line, style_warning))
        elif line.startswith("•") or line.startswith("-"):
            story.append(Paragraph("&nbsp;&nbsp;" + line, style_body))
        else:
            story.append(Paragraph(line, style_body))

    # Pied de page
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "⚠️ Ce système est un exercice académique. Il ne remplace pas une consultation médicale.",
        style_warning
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Généré par le Système Multi-Agents Médical — Projet académique EMSI S8",
        style_meta
    ))

    doc.build(story)
    return buffer.getvalue()