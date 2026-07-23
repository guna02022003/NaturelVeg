from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

TITLE = 'NaturelVeg Online Vegetable Shopping System'

sections = [
    ('Abstract', 'NaturelVeg is an online vegetable shopping system designed to provide customers with a simple and convenient way to buy fresh vegetables through a web interface. The project enables users to register, log in, browse products, add them to the cart, enter delivery address details, choose a payment method, and confirm orders. The system is built using HTML, CSS, JavaScript, Node.js, and SQLite, making it a practical e-commerce prototype for real-world demonstration.'),
    ('Introduction', 'In modern life, people increasingly prefer online services for convenience and saving time. Traditional vegetable shopping often requires physical effort and time. NaturelVeg solves this by creating an online platform where users can buy vegetables from home. The project demonstrates a practical web application that improves the shopping experience with an interactive interface and order process.'),
    ('Objectives', '- To design an online vegetable shopping platform\n- To provide customer login and registration\n- To display products with price and description\n- To manage the shopping cart\n- To collect delivery address details\n- To support order placement and confirmation'),
    ('Modules', '- User Registration and Login\n- Product Module\n- Cart Module\n- Checkout and Address Module\n- Payment Module\n- Order Management Module'),
    ('Technology Used', 'Frontend: HTML, CSS, JavaScript\nBackend: Node.js\nDatabase: SQLite\nServer: Express.js'),
    ('Important Code Snippet', 'app.post(\'/api/login\', (req, res) => {\n  const { email, password } = req.body || {};\n  if (!email || !password) {\n    return res.status(400).json({ message: \'Email and password are required.\' });\n  }\n});\n\napp.post(\'/api/orders\', (req, res) => {\n  const { items = [], method = \'UPI\', details = \'\', email = \'\', deliveryAddress = \'\' } = req.body || {};\n  const total = items.reduce((sum, item) => sum + Number(item.price || 0), 0);\n  res.json({ message: \'Payment Successful!\', order: { total, items } });\n});'),
    ('Conclusion', 'The NaturelVeg project demonstrates a practical online shopping system for vegetables. It offers a simple and attractive user interface along with a working order flow. Although it is a prototype, it clearly shows the idea and functionality of an e-commerce application.'),
]

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']
styleH2 = styles['Heading2']

story = []
story.append(Paragraph(TITLE, styleH))
story.append(Spacer(1, 0.2 * inch))

for heading, content in sections:
    story.append(Paragraph(heading, styleH2))
    story.append(Paragraph(content, styleN))
    story.append(Spacer(1, 0.15 * inch))

pdf_path = 'NaturelVeg_Project_Report.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
doc.build(story)
print(f'Generated {pdf_path}')
