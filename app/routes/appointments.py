from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..ai_scheduler import has_conflict
from ..extensions import db
from ..models import Appointment, Client, Service, User, Vehicle, WorkOrder, WorkOrderItem
from .common import parse_datetime_local, parse_int, parse_money

bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@bp.route("/")
@login_required
def index():
    status = request.args.get("status", "")
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.scheduled_start.desc()).all()
    return render_template("appointments/list.html", appointments=appointments, status=status)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    appointment = Appointment(status="AGENDADO")
    context = _form_context()
    if request.method == "POST":
        ok = _fill_appointment(appointment)
        if not ok:
            return render_template("appointments/form.html", appointment=appointment, title="Novo agendamento", **context)
        db.session.add(appointment)
        db.session.flush()

        if request.form.get("make_os") == "1":
            service = Service.query.get(appointment.service_id)
            wo = _work_order_from_appointment(appointment, service)
            db.session.add(wo)
        db.session.commit()
        flash("Agendamento cadastrado com sucesso.", "success")
        return redirect(url_for("appointments.index"))
    return render_template("appointments/form.html", appointment=appointment, title="Novo agendamento", **context)


@bp.route("/<int:appointment_id>/edit", methods=["GET", "POST"])
@login_required
def edit(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    context = _form_context()
    if request.method == "POST":
        ok = _fill_appointment(appointment, ignore_id=appointment.id)
        if not ok:
            return render_template("appointments/form.html", appointment=appointment, title="Editar agendamento", **context)
        db.session.commit()
        flash("Agendamento atualizado com sucesso.", "success")
        return redirect(url_for("appointments.index"))
    return render_template("appointments/form.html", appointment=appointment, title="Editar agendamento", **context)


@bp.route("/<int:appointment_id>/status/<status>", methods=["POST"])
@login_required
def set_status(appointment_id, status):
    appointment = Appointment.query.get_or_404(appointment_id)
    allowed = {"AGENDADO", "CONFIRMADO", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADO"}
    if status not in allowed:
        flash("Status inválido.", "danger")
    else:
        appointment.status = status
        db.session.commit()
        flash("Status do agendamento atualizado.", "success")
    return redirect(url_for("appointments.index"))


@bp.route("/<int:appointment_id>/create-os", methods=["POST"])
@login_required
def create_work_order(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.work_order:
        flash("Este agendamento já possui ordem de serviço.", "warning")
        return redirect(url_for("appointments.index"))
    service = appointment.service
    wo = _work_order_from_appointment(appointment, service)
    db.session.add(wo)
    appointment.status = "EM_ANDAMENTO"
    db.session.commit()
    flash("Ordem de serviço criada a partir do agendamento.", "success")
    return redirect(url_for("work_orders.detail", work_order_id=wo.id))


def _form_context():
    return {
        "clients": Client.query.filter_by(status="ATIVO").order_by(Client.name.asc()).all(),
        "vehicles": Vehicle.query.order_by(Vehicle.plate.asc()).all(),
        "services": Service.query.filter_by(active=True).order_by(Service.name.asc()).all(),
        "technicians": User.query.filter_by(role="TECNICO", status="ATIVO").order_by(User.name.asc()).all(),
    }


def _fill_appointment(appointment: Appointment, ignore_id: int | None = None) -> bool:
    service_id = parse_int(request.form.get("service_id"))
    service = Service.query.get(service_id)
    if not service:
        flash("Selecione um serviço válido.", "danger")
        return False

    start_raw = request.form.get("scheduled_start")
    if not start_raw:
        flash("Informe data e horário.", "danger")
        return False
    start = parse_datetime_local(start_raw)
    duration = parse_int(request.form.get("duration_minutes"), service.estimated_minutes)
    end = start + timedelta(minutes=max(duration, 15))
    technician_id = parse_int(request.form.get("technician_id"))

    conflicts = has_conflict(technician_id, start, end)
    if conflicts and not ignore_id:
        flash("Conflito de agenda detectado para o técnico escolhido.", "danger")
        return False
    if conflicts and ignore_id:
        existing_conflicts = [c for c in appointment_conflicts_for_edit(technician_id, start, end, ignore_id)]
        if existing_conflicts:
            flash("Conflito de agenda detectado para o técnico escolhido.", "danger")
            return False

    appointment.client_id = parse_int(request.form.get("client_id"))
    appointment.vehicle_id = parse_int(request.form.get("vehicle_id"))
    appointment.service_id = service_id
    appointment.technician_id = technician_id
    appointment.created_by_id = current_user.id
    appointment.scheduled_start = start
    appointment.scheduled_end = end
    appointment.status = request.form.get("status", "AGENDADO")
    appointment.notes = request.form.get("notes") or None
    appointment.ai_score = parse_money(request.form.get("ai_score") or None, default="0") or None
    appointment.ai_reason = request.form.get("ai_reason") or None
    return True


def appointment_conflicts_for_edit(technician_id, start, end, ignore_id):
    return Appointment.query.filter(
        Appointment.id != ignore_id,
        Appointment.technician_id == technician_id,
        Appointment.status.notin_(["CANCELADO", "CONCLUIDA"]),
        Appointment.scheduled_start < end,
        Appointment.scheduled_end > start,
    ).all()


def _work_order_from_appointment(appointment: Appointment, service: Service) -> WorkOrder:
    wo = WorkOrder(
        opening_date=appointment.scheduled_start,
        status="ABERTA",
        problem_description=appointment.notes or f"Serviço agendado: {service.name}",
        client_id=appointment.client_id,
        vehicle_id=appointment.vehicle_id,
        technician_id=appointment.technician_id,
        main_service_id=service.id,
        appointment=appointment,
        created_by_id=current_user.id,
    )
    item = WorkOrderItem(service=service, quantity=1, unit_price=service.base_price)
    item.recalc()
    wo.items.append(item)
    wo.recalc_totals()
    return wo
