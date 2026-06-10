from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Client, Product, Sale, SaleItem, StockMovement, WorkOrder
from .common import parse_int

bp = Blueprint("sales", __name__, url_prefix="/sales")


@bp.route("/")
@login_required
def index():
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template("sales/list.html", sales=sales)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    clients = Client.query.filter_by(status="ATIVO").order_by(Client.name.asc()).all()
    products = Product.query.filter_by(active=True).order_by(Product.name.asc()).all()
    work_orders = WorkOrder.query.filter(WorkOrder.status.in_(["ABERTA", "EM_ANDAMENTO", "CONCLUIDA"])).order_by(WorkOrder.opening_date.desc()).all()
    if request.method == "POST":
        product = Product.query.get_or_404(parse_int(request.form.get("product_id")))
        quantity = parse_int(request.form.get("quantity"), 1)
        if quantity <= 0:
            flash("Quantidade inválida.", "danger")
            return render_template("sales/form.html", clients=clients, products=products, work_orders=work_orders)
        if product.quantity < quantity:
            flash("Estoque insuficiente para a venda.", "danger")
            return render_template("sales/form.html", clients=clients, products=products, work_orders=work_orders)

        sale = Sale(
            client_id=parse_int(request.form.get("client_id")) or None,
            work_order_id=parse_int(request.form.get("work_order_id")) or None,
            payment_method=request.form.get("payment_method") or None,
            status=request.form.get("status", "PAGA"),
            created_by_id=current_user.id,
        )
        item = SaleItem(product=product, quantity=quantity, unit_price=product.unit_price)
        item.recalc()
        sale.items.append(item)
        sale.recalc_total()
        product.quantity -= quantity
        movement = StockMovement(
            product=product,
            movement_type="SAIDA",
            quantity=quantity,
            unit_cost=product.unit_price,
            reason=f"Venda #{sale.id or 'nova'}",
            created_by_id=current_user.id,
        )
        db.session.add_all([sale, movement])
        db.session.commit()
        movement.reason = f"Venda #{sale.id}"
        db.session.commit()
        flash("Venda registrada com sucesso.", "success")
        return redirect(url_for("sales.detail", sale_id=sale.id))
    return render_template("sales/form.html", clients=clients, products=products, work_orders=work_orders)


@bp.route("/<int:sale_id>")
@login_required
def detail(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    return render_template("sales/detail.html", sale=sale)
