from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Client, Service, User, Vehicle, WorkOrder, WorkOrderItem
from .common import parse_int, parse_money

bp = Blueprint("work_orders", __name__, url_prefix="/work-orders")


@bp.route("/")
@login_required
def index():
    status = request.args.get("status", "")
    query = WorkOrder.query
    if status:
        query = query.filter_by(status=status)
    work_orders = query.order_by(WorkOrder.opening_date.desc()).all()
    return render_template("work_orders/list.html", work_orders=work_orders, status=status)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    wo = WorkOrder(status="ABERTA")
    context = _form_context()
    if request.method == "POST":
        _fill_work_order(wo)
        db.session.add(wo)
        service = Service.query.get(wo.main_service_id)
        if service:
            item = WorkOrderItem(service=service, quantity=1, unit_price=service.base_price)
            item.recalc()
            wo.items.append(item)
        wo.recalc_totals()
        db.session.commit()
        flash("Ordem de serviço criada com sucesso.", "success")
        return redirect(url_for("work_orders.detail", work_order_id=wo.id))
    return render_template("work_orders/form.html", work_order=wo, title="Nova ordem de serviço", **context)


@bp.route("/<int:work_order_id>")
@login_required
def detail(work_order_id):
    work_order = WorkOrder.query.get_or_404(work_order_id)
    services = Service.query.filter_by(active=True).order_by(Service.name.asc()).all()
    return render_template("work_orders/detail.html", work_order=work_order, services=services)


@bp.route("/<int:work_order_id>/edit", methods=["GET", "POST"])
@login_required
def edit(work_order_id):
    work_order = WorkOrder.query.get_or_404(work_order_id)
    context = _form_context()
    if request.method == "POST":
        _fill_work_order(work_order)
        work_order.recalc_totals()
        db.session.commit()
        flash("Ordem de serviço atualizada.", "success")
        return redirect(url_for("work_orders.detail", work_order_id=work_order.id))
    return render_template("work_orders/form.html", work_order=work_order, title="Editar ordem de serviço", **context)


@bp.route("/<int:work_order_id>/add-item", methods=["POST"])
@login_required
def add_item(work_order_id):
    work_order = WorkOrder.query.get_or_404(work_order_id)
    service = Service.query.get_or_404(parse_int(request.form.get("service_id")))
    item = WorkOrderItem(
        work_order=work_order,
        service=service,
        quantity=parse_int(request.form.get("quantity"), 1),
        unit_price=parse_money(request.form.get("unit_price"), str(service.base_price)),
    )
    item.recalc()
    db.session.add(item)
    work_order.recalc_totals()
    db.session.commit()
    flash("Item adicionado à ordem de serviço.", "success")
    return redirect(url_for("work_orders.detail", work_order_id=work_order.id))


@bp.route("/<int:work_order_id>/remove-item/<int:item_id>", methods=["POST"])
@login_required
def remove_item(work_order_id, item_id):
    work_order = WorkOrder.query.get_or_404(work_order_id)
    item = WorkOrderItem.query.get_or_404(item_id)
    if item.work_order_id != work_order.id:
        flash("Item não pertence à OS.", "danger")
    else:
        db.session.delete(item)
        work_order.recalc_totals()
        db.session.commit()
        flash("Item removido.", "info")
    return redirect(url_for("work_orders.detail", work_order_id=work_order.id))


@bp.route("/<int:work_order_id>/status/<status>", methods=["POST"])
@login_required
def set_status(work_order_id, status):
    work_order = WorkOrder.query.get_or_404(work_order_id)
    allowed = {"ABERTA", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA"}
    if status not in allowed:
        flash("Status inválido.", "danger")
    else:
        work_order.status = status
        if status == "CONCLUIDA" and not work_order.closing_date:
            work_order.closing_date = datetime.utcnow()
        work_order.recalc_totals()
        db.session.commit()
        flash("Status da OS atualizado.", "success")
    return redirect(url_for("work_orders.detail", work_order_id=work_order.id))


def _form_context():
    return {
        "clients": Client.query.filter_by(status="ATIVO").order_by(Client.name.asc()).all(),
        "vehicles": Vehicle.query.order_by(Vehicle.plate.asc()).all(),
        "services": Service.query.filter_by(active=True).order_by(Service.name.asc()).all(),
        "technicians": User.query.filter_by(role="TECNICO", status="ATIVO").order_by(User.name.asc()).all(),
    }


def _fill_work_order(work_order: WorkOrder) -> None:
    work_order.client_id = parse_int(request.form.get("client_id"))
    work_order.vehicle_id = parse_int(request.form.get("vehicle_id"))
    work_order.technician_id = parse_int(request.form.get("technician_id"))
    work_order.main_service_id = parse_int(request.form.get("main_service_id")) or None
    work_order.status = request.form.get("status", "ABERTA")
    work_order.problem_description = request.form.get("problem_description", "").strip()
    work_order.diagnosis = request.form.get("diagnosis") or None
    work_order.parts_total = parse_money(request.form.get("parts_total"))
    work_order.created_by_id = current_user.id
