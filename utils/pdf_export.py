import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def build_monthly_report_pdf(report_data, company_name="Nexora Technologies"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{company_name} — AssetMind Monthly Maintenance Report</b>", styles["Title"]))
    elements.append(Paragraph(f"Period: {report_data['month']:02d}/{report_data['year']}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    summary_data = [
        ["Metric", "Value"],
        ["Total Tickets", str(report_data["total_tickets"])],
        ["Open Tickets", str(report_data["open_tickets"])],
        ["Resolved Tickets", str(report_data["resolved_tickets"])],
        ["Total Repair Cost", f"Rs. {report_data['repair_costs']:,.0f}"],
        ["Total Replacement Cost", f"Rs. {report_data['replacement_costs']:,.0f}"],
    ]
    summary_table = Table(summary_data, colWidths=[8 * cm, 6 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    if report_data["most_problematic_types"]:
        elements.append(Paragraph("<b>Most Problematic Asset Types</b>", styles["Heading3"]))
        rows = [["Asset Type", "Issue Count"]] + [[t, str(c)] for t, c in report_data["most_problematic_types"]]
        t = Table(rows, colWidths=[8 * cm, 6 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 10)]))
        elements.append(t)
        elements.append(Spacer(1, 16))

    if report_data["top_departments"]:
        elements.append(Paragraph("<b>Departments with Most Issues</b>", styles["Heading3"]))
        rows = [["Department", "Issue Count"]] + [[d, str(c)] for d, c in report_data["top_departments"]]
        t = Table(rows, colWidths=[8 * cm, 6 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 10)]))
        elements.append(t)
        elements.append(Spacer(1, 16))

    if report_data["frequently_repaired"]:
        elements.append(Paragraph("<b>Frequently Repaired Assets</b>", styles["Heading3"]))
        rows = [["Asset ID", "Repairs This Month"]] + [[a, str(c)] for a, c in report_data["frequently_repaired"]]
        t = Table(rows, colWidths=[8 * cm, 6 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 10)]))
        elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer