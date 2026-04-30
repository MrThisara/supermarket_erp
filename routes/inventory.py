from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/')
def index():
    db = get_db()
    inventory = db.execute(
        'SELECT p.name, p.price, i.id, i.quantity, i.reorder_level '
        'FROM inventory i '
        'JOIN products p ON i.product_id = p.id '
        'ORDER BY i.quantity ASC'
    ).fetchall()
    return render_template('inventory/index.html', inventory=inventory)

@bp.route('/adjust/<int:id>', methods=['GET', 'POST'])
def adjust(id):
    db = get_db()
    
    if request.method == 'POST':
        quantity = request.form['quantity']
        reorder_level = request.form['reorder_level']
        
        db.execute(
            'UPDATE inventory SET quantity = ?, reorder_level = ? WHERE id = ?',
            (quantity, reorder_level, id)
        )
        db.commit()
        return redirect(url_for('inventory.index'))
    
    item = db.execute(
        'SELECT i.id, i.quantity, i.reorder_level, p.name '
        'FROM inventory i '
        'JOIN products p ON i.product_id = p.id '
        'WHERE i.id = ?', (id,)
    ).fetchone()
    
    return render_template('inventory/adjust.html', item=item)