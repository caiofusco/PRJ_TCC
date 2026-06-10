from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Product, StockMovement
from .common import parse_int, parse_money

bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.description.ilike(like)))
    products = query.order_by(Product.name.asc()).all()
    return render_template("inventory/list.html", products=products, q=q)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    product = Product(active=True)
    if request.method == "POST":
        _fill_product(product)
        db.session.add(product)
        db.session.commit()
        flash("Produto cadastrado com sucesso.", "success")
        return redirect(url_for("inventory.index"))
    return render_template("inventory/form.html", product=product, title="Novo produto")


@bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        _fill_product(product)
        db.session.commit()
        flash("Produto atualizado com sucesso.", "success")
        return redirect(url_for("inventory.index"))
    return render_template("inventory/form.html", product=product, title="Editar produto")


@bp.route("/<int:product_id>/move", methods=["GET", "POST"])
@login_required
def move(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        movement_type = request.form.get("movement_type", "ENTRADA")
        quantity = parse_int(request.form.get("quantity"), 0)
        if quantity <= 0:
            flash("Informe uma quantidade válida.", "danger")
            return redirect(url_for("inventory.move", product_id=product.id))
        if movement_type == "SAIDA" and product.quantity < quantity:
            flash("Estoque insuficiente para saída.", "danger")
            return redirect(url_for("inventory.move", product_id=product.id))
        if movement_type == "SAIDA":
            product.quantity -= quantity
        elif movement_type == "AJUSTE":
            product.quantity = quantity
        else:
            product.quantity += quantity
        movement = StockMovement(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=parse_money(request.form.get("unit_cost")),
            reason=request.form.get("reason") or None,
            created_by_id=current_user.id,
        )
        db.session.add(movement)
        db.session.commit()
        flash("Movimentação registrada.", "success")
        return redirect(url_for("inventory.index"))
    return render_template("inventory/move.html", product=product)


@bp.route("/<int:product_id>/toggle", methods=["POST"])
@login_required
def toggle(product_id):
    product = Product.query.get_or_404(product_id)
    product.active = not product.active
    db.session.commit()
    flash("Status do produto atualizado.", "info")
    return redirect(url_for("inventory.index"))


def _fill_product(product: Product) -> None:
    product.name = request.form.get("name", "").strip()
    product.description = request.form.get("description") or None
    product.quantity = parse_int(request.form.get("quantity"), 0)
    product.min_quantity = parse_int(request.form.get("min_quantity"), 1)
    product.unit_price = parse_money(request.form.get("unit_price"))
    product.active = request.form.get("active", "1") == "1"
