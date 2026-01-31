import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from io import BytesIO
from app.models.bill import Bill

# Note: In a real environment, we'd need a Tamil .ttf file.
# We will use standard fonts here but structure it for Tamil support.
# To support Tamil, we would use:
# pdfmetrics.registerFont(TTFont('Latha', 'latha.ttf'))

def generate_bill_pdf(bill: Bill) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Simple Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 20*mm, bill.shop_name)
    
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, height - 35*mm, f"Bill No: {bill.bill_number}")
    c.drawString(20*mm, height - 40*mm, f"Date: {bill.created_at.strftime('%d-%m-%Y %H:%M')}")
    c.drawString(20*mm, height - 45*mm, f"Customer: {bill.customer_name or 'Regular'}")
    c.drawString(20*mm, height - 50*mm, f"Type: {bill.billing_type}")
    
    # Table Header
    y = height - 60*mm
    c.line(20*mm, y+2*mm, width - 20*mm, y+2*mm)
    c.drawString(20*mm, y, "Item (காய்)")
    c.drawString(80*mm, y, "Qty (கி.கி)")
    c.drawString(110*mm, y, "Price (விலை)")
    c.drawString(140*mm, y, "Total (மொத்தம்)")
    c.line(20*mm, y-2*mm, width - 20*mm, y-2*mm)
    
    y -= 10*mm
    for item in bill.items:
        # Since we don't have the font file in this sandbox, 
        # we'll use English names but the logic is ready for Tamil.
        display_name = item.vegetable_name
        c.drawString(20*mm, y, display_name)
        c.drawString(80*mm, y, f"{item.qty_kg} kg")
        c.drawString(110*mm, y, f"Rs.{item.price}")
        c.drawString(140*mm, y, f"Rs.{item.subtotal}")
        y -= 7*mm
        if y < 40*mm: # Page break logic
            c.showPage()
            y = height - 20*mm
            
    c.line(20*mm, y, width - 20*mm, y)
    y -= 10*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(110*mm, y, "Grand Total:")
    c.drawString(140*mm, y, f"Rs.{bill.total_amount}")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
