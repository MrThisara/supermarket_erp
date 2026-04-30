from flask import Blueprint, render_template
from database import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/')

@bp.route('/')
def index():
    db = get_db()

    sales_today = db.execute(
        "SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as revenue "
        "FROM sales WHERE DATE(created_at) = DATE('now')"
    ).fetchone()

    low_stock = db.execute(
        "SELECT p.name, i.quantity, i.reorder_level "
        "FROM inventory i "
        "JOIN products p ON i.product_id = p.id "
        "WHERE i.quantity <= i.reorder_level "
        "ORDER BY i.quantity ASC"
    ).fetchall()

    recent_sales = db.execute(
        "SELECT * FROM sales ORDER BY created_at DESC LIMIT 5"
    ).fetchall()

    pending_orders = db.execute(
        "SELECT COUNT(*) as count FROM purchase_orders WHERE status = 'pending'"
    ).fetchone()

    total_products = db.execute(
        "SELECT COUNT(*) as count FROM products"
    ).fetchone()

    return render_template('dashboard/index.html',
        sales_today=sales_today,
        low_stock=low_stock,
        recent_sales=recent_sales,
        pending_orders=pending_orders,
        total_products=total_products
    )