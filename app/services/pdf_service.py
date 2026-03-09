from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab import rl_config
from io import BytesIO
from app.models.bill import Bill
from xml.sax.saxutils import escape

# STICKY RULES: Unicode, UTF-8, Shaping, Professional Quality
rl_config.shaping = "harfbuzz"

# ---- FONT REGISTRATION (SAFE) ----
try:
    TAMIL_FONT_PATH = "C:/Windows/Fonts/Nirmala.ttf"
    TAMIL_BOLD_FONT_PATH = "C:/Windows/Fonts/NirmalaB.ttf"
    
    pdfmetrics.registerFont(TTFont("TamilFont", TAMIL_FONT_PATH))
    pdfmetrics.registerFont(TTFont("TamilFont-Bold", TAMIL_BOLD_FONT_PATH))
    
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily("TamilFont", normal="TamilFont", bold="TamilFont-Bold")
    
    FONT_NAME = "TamilFont"
    BOLD_FONT_NAME = "TamilFont-Bold"
except Exception as e:
    print(f"CRITICAL: Font registration failed: {e}")
    FONT_NAME = "Helvetica"
    BOLD_FONT_NAME = "Helvetica-Bold"

# ---- PDF GENERATOR ----
def generate_bill_pdf(bill: Bill) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    # ---- STYLES ----
    styles = getSampleStyleSheet()
    
    tamil_style = ParagraphStyle(
        name="Tamil",
        fontName=FONT_NAME,
        fontSize=10,
        leading=14,
        textColor=colors.black
    )

    tamil_bold_style = ParagraphStyle(
        name="TamilBold",
        parent=tamil_style,
        fontName=BOLD_FONT_NAME
    )

    shop_name_style = ParagraphStyle(
        name="ShopName",
        parent=tamil_bold_style,
        fontSize=28,
        alignment=1, # Center
        spaceAfter=2 * mm
    )

    address_style = ParagraphStyle(
        name="Address",
        parent=tamil_style,
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor("#666666") # Grey
    )

    elements = []

    # ---- HEADER SECTION ----
    elements.append(Paragraph("Suji Vegetables", shop_name_style))
    elements.append(Paragraph("Pondy - Tindivanam Main Raod, Kiliyanur", address_style))
    elements.append(Paragraph("Phone: +91 9095938085", address_style))

    elements.append(Spacer(1, 5 * mm))
    
    # Dotted Divider
    divider = Table([[""]], colWidths=[180 * mm])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey, 1, (1, 2))
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 8 * mm))

    # ---- BILL META SECTION ----
    customer = escape(bill.customer_name or 'Walking Customer')
    customer_mobile = escape(bill.customer_mobile or 'N/A')
    bill_no = escape(bill.bill_number)
    bill_type = escape(bill.billing_type)
    bill_date = bill.created_at.strftime("%d/%m/%Y %H:%M")

    meta_data = [
        [
            Paragraph(f"<b>Bill To:</b> {customer}", tamil_style),
            Paragraph(f"<b>Bill No:</b> {bill_no}", tamil_style)
        ],
        [
            Paragraph(f"<b>Contact:</b> {customer_mobile}", tamil_style),
            Paragraph(f"<b>Date:</b> {bill_date}", tamil_style)
        ],
        [
            Paragraph(f"<b>Type:</b> {bill_type}", tamil_style),
            ""
        ]
    ]
    meta_table = Table(meta_data, colWidths=[110 * mm, 70 * mm])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2 * mm),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10 * mm))

    # ---- ITEMS TABLE SECTION ----
    items_data = [[
        Paragraph("<b>Item</b>", tamil_style),
        Paragraph("<b>Qty</b>", tamil_style),
        Paragraph("<b>Price</b>", tamil_style),
        Paragraph("<b>Total</b>", tamil_style),
    ]]

    for item in bill.items:
        eng_name = escape(item.vegetable_name)
        tam_name = escape(item.tamil_name or "")
        
        # English + Tamil (Grey) on same line
        item_html = eng_name
        if tam_name:
            item_html += f' <font color="#888888" size="9">{tam_name}</font>'

        if item.qty_kg < 1:
            qty_text = f"{int(item.qty_kg * 1000)} g"
        else:
            qty_text = f"{int(item.qty_kg)} kg" if item.qty_kg.is_integer() else f"{item.qty_kg:g} kg"

        items_data.append([
            Paragraph(item_html, tamil_style),
            Paragraph(qty_text, tamil_style),
            Paragraph(f"{item.price:.2f}", tamil_style),
            Paragraph(f"{item.subtotal:.2f}", tamil_style),
        ])

    items_table = Table(items_data, colWidths=[100 * mm, 25 * mm, 25 * mm, 30 * mm])
    items_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1.2, colors.black), # Line above header
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.black), # Line below header
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (0,-1), 1.5 * mm),
        ('TOPPADDING', (0,1), (0,-1), 1.5 * mm),
        ('LINEBELOW', (0,-1), (-1,-1), 1.2, colors.black), # Bottom line
    ]))
    elements.append(items_table)
    
    # ---- TOTALS SECTION ----
    elements.append(Spacer(1, 3 * mm))
    
    totals_data = []
    
    # Subtotal
    subtotal_row = [
        "", 
        Paragraph('<font color="#666666">Subtotal:</font>', tamil_style), 
        Paragraph(f"₹{bill.subtotal:.2f}", tamil_style)
    ]
    totals_data.append(subtotal_row)
    
    if bill.tax_amount > 0:
        totals_data.append(["", Paragraph('<font color="#666666">Tax:</font>', tamil_style), f"₹{bill.tax_amount:.2f}"])
    
    if bill.discount_amount > 0:
        totals_data.append(["", Paragraph('<font color="#666666">Discount:</font>', tamil_style), f"-₹{bill.discount_amount:.2f}"])
    
    # Grand Total
    grand_total_row = [
        "",
        Paragraph("<b>Grand Total:</b>", ParagraphStyle(name="GT", parent=tamil_bold_style, fontSize=16)),
        Paragraph(f"<b>₹{bill.total_amount:.2f}</b>", ParagraphStyle(name="GV", parent=tamil_bold_style, fontSize=16))
    ]
    totals_data.append(grand_total_row)
    
    totals_table = Table(totals_data, colWidths=[100 * mm, 40 * mm, 40 * mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1 * mm),
        # Dotted line above grand total
        ('LINEABOVE', (1,-1), (-1,-1), 0.5, colors.black, 1, (1, 2)),
        ('TOPPADDING', (1,-1), (-1,-1), 3 * mm),
    ]))
    
    elements.append(totals_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
