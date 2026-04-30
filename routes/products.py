from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/')
def index():
    db = get_db()
    products = db.execute(
        'SELECT p.id, p.name, p.price, p.created_at, COALESCE(i.quantity, 0) as quantity '
        'FROM products p '
        'LEFT JOIN inventory i ON p.id = i.product_id '
        'ORDER BY p.name ASC'
    ).fetchall()
    return render_template('products/index.html', products=products)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        
        db = get_db()
        db.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
        db.execute('INSERT INTO inventory (product_id, quantity) VALUES (last_insert_rowid(), 0)')
        db.commit()
        
        return redirect(url_for('products.index'))
    
    return render_template('products/add.html')

@bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db()
    db.execute('DELETE FROM inventory WHERE product_id = ?', (id,))
    db.execute('DELETE FROM products WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('products.index'))