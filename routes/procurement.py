from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db

bp = Blueprint('procurement', __name__, url_prefix='/procurement')

@bp.route('/')
def index():
    db = get_db()
    orders = db.execute(
        'SELECT * FROM purchase_orders ORDER BY created_at DESC'
    ).fetchall()
    return render_template('procurement/index.html', orders=orders)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    db = get_db()

    if request.method == 'POST':
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        cursor = db.execute("INSERT INTO purchase_orders (status) VALUES ('pending')")
        order_id = cursor.lastrowid

        for product_id, quantity in zip(product_ids, quantities):
            quantity = int(quantity)
            if quantity <= 0:
                continue
            db.execute(
                'INSERT INTO purchase_order_items (order_id, product_id, quantity) '
                'VALUES (?, ?, ?)',
                (order_id, product_id, quantity)
            )

        db.commit()
        return redirect(url_for('procurement.detail', id=order_id))

    low_stock = db.execute(
        'SELECT p.id, p.name, i.quantity, i.reorder_level '
        'FROM inventory i '
        'JOIN products p ON i.product_id = p.id '
        'WHERE i.quantity <= i.reorder_level '
        'ORDER BY i.quantity ASC'
    ).fetchall()

    all_products = db.execute(
        'SELECT p.id, p.name, i.quantity '
        'FROM products p '
        'JOIN inventory i ON p.id = i.product_id '
        'ORDER BY p.name ASC'
    ).fetchall()

    return render_template('procurement/new.html', low_stock=low_stock, all_products=all_products)

@bp.route('/<int:id>')
def detail(id):
    db = get_db()
    order = db.execute(
        'SELECT * FROM purchase_orders WHERE id = ?', (id,)
    ).fetchone()
    items = db.execute(
        'SELECT poi.quantity, p.name '
        'FROM purchase_order_items poi '
        'JOIN products p ON poi.product_id = p.id '
        'WHERE poi.order_id = ?', (id,)
    ).fetchall()
    return render_template('procurement/detail.html', order=order, items=items)

@bp.route('/receive/<int:id>', methods=['POST'])
def receive(id):
    db = get_db()

    items = db.execute(
        'SELECT * FROM purchase_order_items WHERE order_id = ?', (id,)
    ).fetchall()

    for item in items:
        db.execute(
            'UPDATE inventory SET quantity = quantity + ? WHERE product_id = ?',
            (item['quantity'], item['product_id'])
        )

    db.execute(
        "UPDATE purchase_orders SET status = 'received' WHERE id = ?", (id,)
    )
    db.commit()
    return redirect(url_for('procurement.detail', id=id))

@bp.route('/cancel/<int:id>', methods=['POST'])
def cancel(id):
    db = get_db()
    db.execute(
        "UPDATE purchase_orders SET status = 'cancelled' WHERE id = ?", (id,)
    )
    db.commit()
    return redirect(url_for('procurement.detail', id=id))