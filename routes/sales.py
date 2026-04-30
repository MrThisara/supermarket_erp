from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db

bp = Blueprint('sales', __name__, url_prefix='/sales')

@bp.route('/')
def index():
    db = get_db()
    sales = db.execute(
        'SELECT * FROM sales ORDER BY created_at DESC'
    ).fetchall()
    return render_template('sales/index.html', sales=sales)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    db = get_db()

    if request.method == 'POST':
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        cursor = db.execute('INSERT INTO sales (total_amount) VALUES (0)')
        sale_id = cursor.lastrowid

        total = 0

        for product_id, quantity in zip(product_ids, quantities):
            quantity = int(quantity)
            if quantity <= 0:
                continue

            product = db.execute(
                'SELECT * FROM products WHERE id = ?', (product_id,)
            ).fetchone()

            subtotal = product['price'] * quantity
            total += subtotal

            db.execute(
                'INSERT INTO sale_items (sale_id, product_id, quantity, unit_price) '
                'VALUES (?, ?, ?, ?)',
                (sale_id, product_id, quantity, product['price'])
            )

            db.execute(
                'UPDATE inventory SET quantity = quantity - ? WHERE product_id = ?',
                (quantity, product_id)
            )

        db.execute(
            'UPDATE sales SET total_amount = ? WHERE id = ?',
            (total, sale_id)
        )
        db.commit()
        return redirect(url_for('sales.detail', id=sale_id))

    products = db.execute(
        'SELECT p.id, p.name, p.price, i.quantity '
        'FROM products p '
        'JOIN inventory i ON p.id = i.product_id '
        'WHERE i.quantity > 0 '
        'ORDER BY p.name ASC'
    ).fetchall()
    return render_template('sales/new.html', products=products)

@bp.route('/<int:id>')
def detail(id):
    db = get_db()
    sale = db.execute(
        'SELECT * FROM sales WHERE id = ?', (id,)
    ).fetchone()
    items = db.execute(
        'SELECT si.quantity, si.unit_price, p.name, '
        '(si.quantity * si.unit_price) as subtotal '
        'FROM sale_items si '
        'JOIN products p ON si.product_id = p.id '
        'WHERE si.sale_id = ?', (id,)
    ).fetchall()
    return render_template('sales/detail.html', sale=sale, items=items)