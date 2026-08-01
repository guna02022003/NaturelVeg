const express = require('express');
const path = require('path');
const crypto = require('crypto');
const { DatabaseSync } = require('node:sqlite');

const app = express();
const port = process.env.PORT || 3000;
const db = new DatabaseSync('naturelveg.db');

function svgDataUri(label, background, accent) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="260" viewBox="0 0 400 260">
      <rect width="100%" height="100%" fill="${background}" />
      <text x="200" y="130" text-anchor="middle" font-size="34" fill="#2E8B57" font-family="Arial">${label}</text>
      <circle cx="110" cy="110" r="58" fill="${accent}" opacity="0.8" />
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

const products = [
  { name: 'Tomato', price: 20, img: '/assets/tomato.svg', desc: 'Fresh red tomatoes, rich in vitamins and antioxidants.' },
  { name: 'Potato', price: 30, img: '/assets/potato.jpg', desc: 'Organic potatoes, perfect for fries, baking, and healthy meals.' },
  { name: 'Onion', price: 18, img: '/assets/onion.jpg', desc: 'Crisp and flavorful onions, great for all dishes.' },
  { name: 'Carrot', price: 25, img: '/assets/carrot.jpg', desc: 'Sweet and crunchy carrots, rich in vitamin A.' },
  { name: 'Cucumber', price: 15, img: '/assets/cucumber.svg', desc: 'Fresh cucumbers, perfect for salads and detox drinks.' },
  { name: 'Black Pepper', price: 40, img: '/assets/black-pepper.jpg', desc: 'Premium black pepper for your daily cooking and seasoning.' }
];

db.exec(`
  PRAGMA journal_mode = WAL;
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    token TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    email TEXT,
    method TEXT NOT NULL,
    details TEXT,
    unit TEXT,
    delivery_address TEXT,
    total INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    quantity REAL NOT NULL DEFAULT 1,
    unit TEXT DEFAULT 'kgs',
    img TEXT,
    desc TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(id)
  );
`);

app.use(express.json());
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');

  if (req.method === 'OPTIONS') {
    return res.sendStatus(204);
  }

  next();
});
app.use(express.static(path.join(__dirname)));

app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({ message: 'Invalid JSON payload.' });
  }

  next(err);
});

function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

function createToken() {
  return `tok_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

function getAuthToken(req) {
  const authHeader = req.headers.authorization || '';
  return authHeader.startsWith('Bearer ') ? authHeader.split(' ')[1] : '';
}

function addDeliveryAddressColumnIfMissing() {
  const columns = db.prepare('PRAGMA table_info(orders)').all();
  const hasDeliveryAddress = columns.some((column) => column.name === 'delivery_address');

  if (!hasDeliveryAddress) {
    db.exec('ALTER TABLE orders ADD COLUMN delivery_address TEXT');
  }
}

function addUnitColumnIfMissing() {
  const columns = db.prepare('PRAGMA table_info(orders)').all();
  const hasUnit = columns.some((column) => column.name === 'unit');

  if (!hasUnit) {
    db.exec('ALTER TABLE orders ADD COLUMN unit TEXT');
  }
}

function addOrderItemColumnsIfMissing() {
  const columns = db.prepare('PRAGMA table_info(order_items)').all();
  if (!columns.some((column) => column.name === 'quantity')) {
    db.exec('ALTER TABLE order_items ADD COLUMN quantity REAL DEFAULT 1');
  }

  if (!columns.some((column) => column.name === 'unit')) {
    db.exec("ALTER TABLE order_items ADD COLUMN unit TEXT DEFAULT 'kgs'");
  }
}

function ensureDemoAccounts() {
  const demoAccounts = [
    { email: 'gu', password: 'secret123' },
    { email: 'naturelveg@example.com', password: 'secret123' },
    { email: 'test@example.com', password: 'secret123' },
    { email: 'customer@test.com', password: 'secret123' }
  ];

  for (const account of demoAccounts) {
    const email = account.email.trim().toLowerCase();
    const passwordHash = hashPassword(account.password);
    const existingUser = db.prepare('SELECT * FROM users WHERE email = ?').get(email);

    if (!existingUser) {
      db.prepare('INSERT INTO users (email, password_hash) VALUES (?, ?)')
        .run(email, passwordHash);
      continue;
    }

    if (existingUser.password_hash !== passwordHash) {
      db.prepare('UPDATE users SET password_hash = ? WHERE email = ?').run(passwordHash, email);
    }
  }
}

addDeliveryAddressColumnIfMissing();
addUnitColumnIfMissing();
addOrderItemColumnsIfMissing();
ensureDemoAccounts();

app.get('/api/products', (req, res) => {
  res.json({ products });
});

app.post('/api/register', (req, res) => {
  const { email, password } = req.body || {};

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required.' });
  }

  try {
    db.prepare('INSERT INTO users (email, password_hash) VALUES (?, ?)')
      .run(email.trim().toLowerCase(), hashPassword(password));

    res.status(201).json({ message: 'Account created successfully.' });
  } catch (error) {
    if (error?.code === 'SQLITE_CONSTRAINT_UNIQUE') {
      return res.status(409).json({ message: 'Email already exists.' });
    }
    return res.status(500).json({ message: 'Unable to create account.' });
  }
});

app.post('/api/login', (req, res) => {
  const { email, password } = req.body || {};

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required.' });
  }

  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email.trim().toLowerCase());
  if (!user) {
    return res.status(401).json({ message: 'Invalid email or password.' });
  }

  if (user.password_hash !== hashPassword(password)) {
    return res.status(401).json({ message: 'Invalid email or password.' });
  }

  const token = createToken();
  db.prepare('UPDATE users SET token = ? WHERE id = ?').run(token, user.id);

  res.json({ message: 'Login successful.', token, email: user.email });
});

app.get('/api/admin/orders', (req, res) => {
  const token = getAuthToken(req);
  const user = db.prepare('SELECT * FROM users WHERE token = ?').get(token);

  if (!user) {
    return res.status(401).json({ message: 'Unauthorized' });
  }

  const orders = db.prepare('SELECT * FROM orders ORDER BY created_at DESC').all();
  const rows = orders.map((order) => {
    const items = db.prepare('SELECT * FROM order_items WHERE order_id = ?').all(order.id);
    return { ...order, items };
  });

  res.json({ orders: rows });
});

app.post('/api/orders', (req, res) => {
  const { items = [], method = 'UPI', details = '', unit = 'kgs', email = '', deliveryAddress = '' } = req.body || {};

  if (!Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ message: 'Cart is empty.' });
  }

  const total = items.reduce((sum, item) => sum + Number(item.price || 0), 0);
  const orderId = `ORD-${Date.now()}`;

  db.prepare('INSERT INTO orders (id, email, method, details, unit, delivery_address, total) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(orderId, email || null, method, details, unit, deliveryAddress || null, total);

  const insertItem = db.prepare('INSERT INTO order_items (order_id, name, price, quantity, unit, img, desc) VALUES (?, ?, ?, ?, ?, ?, ?)');
  for (const item of items) {
    insertItem.run(orderId, item.name, Number(item.price || 0), Number(item.quantity || 1), item.unit || 'kgs', item.img || '', item.desc || '');
  }

  res.json({ message: 'Payment Successful!', order: { id: orderId, email, method, details, unit, deliveryAddress, delivery_address: deliveryAddress, total, items } });
});

app.get('/api/orders', (req, res) => {
  const emailFilter = (req.query.email || '').trim().toLowerCase();
  let rows = [];

  if (emailFilter) {
    const orders = db.prepare('SELECT * FROM orders WHERE email = ? ORDER BY created_at DESC').all(emailFilter);
    rows = orders.map((order) => {
      const items = db.prepare('SELECT * FROM order_items WHERE order_id = ?').all(order.id);
      return {
        ...order,
        deliveryAddress: order.delivery_address,
        delivery_address: order.delivery_address,
        unit: order.unit || 'kgs',
        items
      };
    });
  } else {
    const orders = db.prepare('SELECT * FROM orders ORDER BY created_at DESC').all();
    rows = orders.map((order) => {
      const items = db.prepare('SELECT * FROM order_items WHERE order_id = ?').all(order.id);
      return {
        ...order,
        deliveryAddress: order.delivery_address,
        delivery_address: order.delivery_address,
        items
      };
    });
  }

  res.json({ orders: rows });
});

app.listen(port, () => {
  console.log(`NaturelVeg backend running at http://localhost:${port}`);
});
