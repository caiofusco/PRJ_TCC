from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..extensions import db
from ..models import Service
from .common import parse_int, parse_money

bp = Blueprint("services", __name__, url_prefix="/services")


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Service.query
    if q:
        like = f"%{q}%"
        query = query.filter((Service.name.ilike(like)) | (Service.category.ilike(like)))
    services = query.order_by(Service.name.asc()).all()
    return render_template("services/list.html", services=services, q=q)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    service = Service(active=True, estimated_minutes=60)
    if request.method == "POST":
        _fill_service(service)
        db.session.add(service)
        db.session.commit()
        flash("Serviço cadastrado com sucesso.", "success")
        return redirect(url_for("services.index"))
    return render_template("services/form.html", service=service, title="Novo serviço")


@bp.route("/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == "POST":
        _fill_service(service)
        db.session.commit()
        flash("Serviço atualizado com sucesso.", "success")
        return redirect(url_for("services.index"))
    return render_template("services/form.html", service=service, title="Editar serviço")


@bp.route("/<int:service_id>/toggle", methods=["POST"])
@login_required
def toggle(service_id):
    service = Service.query.get_or_404(service_id)
    service.active = not service.active
    db.session.commit()
    flash("Status do serviço atualizado.", "info")
    return redirect(url_for("services.index"))


def _fill_service(service: Service) -> None:
    service.name = request.form.get("name", "").strip()
    service.category = request.form.get("category") or None
    service.description = request.form.get("description") or None
    service.base_price = parse_money(request.form.get("base_price"))
    service.estimated_minutes = parse_int(request.form.get("estimated_minutes"), 60)
    service.active = request.form.get("active", "1") == "1"
