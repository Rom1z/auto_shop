from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_pdf(order_details):
    pdf_file_name = "order_details.pdf"
    c = canvas.Canvas ( pdf_file_name , pagesize=letter )

    # Set up the content for the PDF
    c.setFont ( "Helvetica" , 12 )
    text = "Order Details:\n\n" + order_details
    textobject = c.beginText ( 100 , 750 )
    textobject.textLines ( text )
    c.drawText ( textobject )

    # Save the PDF file
    c.save ()

    return pdf_file_name
