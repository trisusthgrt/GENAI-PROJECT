from fpdf import FPDF

def create_pdf(content: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    # Get PDF as bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes