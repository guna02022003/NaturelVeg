from pathlib import Path
import textwrap

REPORT_PATH = Path('NaturelVeg_Project_Report.pdf')

TITLE = 'NaturelVeg Online Vegetable Shopping System'

sections = [
    ('Abstract',
     'NaturelVeg is an online vegetable shopping system designed to provide customers with a simple and convenient way to buy fresh vegetables through a web interface. The project enables users to register, log in, browse products, add them to the cart, enter delivery address details, choose a payment method, and confirm orders. The system is built using HTML, CSS, JavaScript, Node.js, and SQLite, making it a practical e-commerce prototype for real-world demonstration.'),
    ('Introduction',
     'In modern life, people increasingly prefer online services for convenience and saving time. Traditional vegetable shopping often requires physical effort and time. NaturelVeg solves this by creating an online platform where users can buy vegetables from home. The project demonstrates a practical web application that improves the shopping experience with an interactive interface and order process.'),
    ('Objectives',
     '- To design an online vegetable shopping platform\n- To provide customer login and registration\n- To display products with price and description\n- To manage the shopping cart\n- To collect delivery address details\n- To support order placement and confirmation'),
    ('Modules',
     '- User Registration and Login\n- Product Module\n- Cart Module\n- Checkout and Address Module\n- Payment Module\n- Order Management Module'),
    ('Technology Used',
     'Frontend: HTML, CSS, JavaScript\nBackend: Node.js\nDatabase: SQLite\nServer: Express.js'),
    ('Important Code Snippet',
     'app.post(\'/api/login\', (req, res) => {\n  const { email, password } = req.body || {};\n  if (!email || !password) {\n    return res.status(400).json({ message: \'Email and password are required.\' });\n  }\n});\n\napp.post(\'/api/orders\', (req, res) => {\n  const { items = [], method = \'UPI\', details = \'\', email = \'\', deliveryAddress = \'\' } = req.body || {};\n  const total = items.reduce((sum, item) => sum + Number(item.price || 0), 0);\n  res.json({ message: \'Payment Successful!\', order: { total, items } });\n});'),
    ('Conclusion',
     'The NaturelVeg project demonstrates a practical online shopping system for vegetables. It offers a simple and attractive user interface along with a working order flow. Although it is a prototype, it clearly shows the idea and functionality of an e-commerce application.'),
]


def escape_pdf_text(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def wrap_lines(text: str, width: int = 86) -> list[str]:
    wrapped = []
    for para in text.split('\n'):
        if not para.strip():
            wrapped.append('')
            continue
        if len(para) <= width:
            wrapped.append(para)
        else:
            wrapped.extend(textwrap.wrap(para, width=width, break_long_words=False))
    return wrapped


def make_page(content_lines, page_no):
    lines = []
    y = 760
    font_size = 12
    lines.append('BT')
    lines.append('/F1 18 Tf')
    lines.append('50 780 Td')
    lines.append(f'({escape_pdf_text(TITLE)}) Tj')
    lines.append('ET')

    for i, line in enumerate(content_lines):
        if i == 0:
            y = 744
        elif i == 1:
            y = 728
        else:
            y -= 18

    current_y = 740
    for idx, entry in enumerate(content_lines):
        if entry.strip() == '':
            current_y -= 16
            continue
        lines.append('BT')
        lines.append('/F1 11 Tf')
        lines.append(f'50 {current_y} Td')
        lines.append(f'({escape_pdf_text(entry)}) Tj')
        lines.append('ET')
        current_y -= 16

    page_text = '\n'.join(lines)
    return page_text


def build_pdf():
    pages = []
    page_lines = []
    for section_title, content in sections:
        page_lines.append(section_title.upper())
        page_lines.extend(wrap_lines(content, width=84))
        page_lines.append('')

        if len(page_lines) >= 35:
            pages.append(make_page(page_lines, len(pages) + 1))
            page_lines = []

    if page_lines:
        pages.append(make_page(page_lines, len(pages) + 1))

    objects = []
    catalog = '<< /Type /Catalog /Pages 2 0 R >>'
    pages_obj = '<< /Type /Pages /Kids ['
    for idx in range(len(pages)):
        pages_obj += f' {idx * 2 + 3} 0 R'
    pages_obj += '] /Count ' + str(len(pages)) + ' >>'
    objects.append('<< /Type /Pages /Kids [] /Count 0 >>')

    # Use a simple object list layout
    pdf = bytearray()
    pdf.extend(b'%PDF-1.4\n')
    offsets = [0]

    content_streams = []
    for idx, page_text in enumerate(pages):
        stream_bytes = page_text.encode('latin-1', errors='replace')
        content_streams.append(stream_bytes)
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents {idx * 2 + 5} 0 R >>')
        objects.append(f'<< /Length {len(stream_bytes)} >>\nstream\n{page_text}\nendstream')

    # Recreate object list with proper numbering
    object_entries = []
    object_entries.append('<< /Type /Catalog /Pages 2 0 R >>')
    object_entries.append('<< /Type /Pages /Kids [' + ' '.join(f'{i} 0 R' for i in range(3, len(pages)*2 + 3, 2)) + '] /Count ' + str(len(pages)) + ' >>')
    object_entries.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    for i, content in enumerate(content_streams, start=5):
        object_entries.append(f'<< /Length {len(content)} >>\nstream\n{content.decode("latin-1", errors="replace")}\nendstream')

    # fix numbering precisely
    objects = []
    objects.append('<< /Type /Catalog /Pages 2 0 R >>')
    objects.append('<< /Type /Pages /Kids [' + ' '.join(f'{i} 0 R' for i in range(3, len(pages) * 2 + 3, 2)) + '] /Count ' + str(len(pages)) + ' >>')
    objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    for idx, page_text in enumerate(pages):
        stream_bytes = page_text.encode('latin-1', errors='replace')
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {len(objects) + 2} 0 R >>')
        objects.append(f'<< /Length {len(stream_bytes)} >>\nstream\n{page_text}\nendstream')

    # Recompute object order to correct references
    actual = [
        '<< /Type /Catalog /Pages 2 0 R >>',
        '<< /Type /Pages /Kids [' + ' '.join(f'{i} 0 R' for i in range(3, len(pages) * 2 + 3, 2)) + '] /Count ' + str(len(pages)) + ' >>',
        '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'
    ]
    page_idx = 3
    for page_text in pages:
        stream_bytes = page_text.encode('latin-1', errors='replace')
        actual.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {page_idx + 1} 0 R >>')
        actual.append(f'<< /Length {len(stream_bytes)} >>\nstream\n{page_text}\nendstream')
        page_idx += 2

    pdf = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for idx, obj in enumerate(actual, start=1):
        offsets.append(len(pdf))
        pdf.extend(f'{idx} 0 obj\n'.encode('latin-1'))
        pdf.extend(obj.encode('latin-1', errors='replace'))
        pdf.extend(b'\nendobj\n')

    xref_pos = len(pdf)
    pdf.extend(f'xref\n0 {len(actual)+1}\n'.encode('latin-1'))
    pdf.extend(b'0000000000 65535 f \n')
    for off in offsets[1:]:
        pdf.extend(f'{off:010d} 00000 n \n'.encode('latin-1'))
    pdf.extend(f'trailer\n<< /Size {len(actual)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n'.encode('latin-1'))

    REPORT_PATH.write_bytes(pdf)
    print(f'Created {REPORT_PATH} ({REPORT_PATH.stat().st_size} bytes)')


build_pdf()
