from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..extensions import db
from ..models import Client, Vehicle
from .common import parse_int

bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Vehicle.query.join(Client)
    if q:
        like = f"%{q}%"
        query = query.filter((Vehicle.plate.ilike(like)) | (Vehicle.brand.ilike(like)) | (Vehicle.model.ilike(like)) | (Client.name.ilike(like)))
    vehicles = query.order_by(Vehicle.plate.asc()).all()
    return render_template("vehicles/list.html", vehicles=vehicles, q=q)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    vehicle = Vehicle()
    clients = Client.query.filter_by(status="ATIVO").order_by(Client.name.asc()).all()
    if request.method == "POST":
        _fill_vehicle(vehicle)
        db.session.add(vehicle)
        db.session.commit()
        flash("Veículo cadastrado com sucesso.", "success")
        return redirect(url_for("vehicles.index"))
    return render_template("vehicles/form.html", vehicle=vehicle, clients=clients, title="Novo veículo")


@bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
@login_required
def edit(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    clients = Client.query.filter_by(status="ATIVO").order_by(Client.name.asc()).all()
    if request.method == "POST":
        _fill_vehicle(vehicle)
        db.session.commit()
        flash("Veículo atualizado com sucesso.", "success")
        return redirect(url_for("vehicles.index"))
    return render_template("vehicles/form.html", vehicle=vehicle, clients=clients, title="Editar veículo")


@bp.route("/<int:vehicle_id>/delete", methods=["POST"])
@login_required
def delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    try:
        db.session.delete(vehicle)
        db.session.commit()
        flash("Veículo excluído.", "info")
    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir: veículo possui histórico vinculado.", "warning")
    return redirect(url_for("vehicles.index"))


def _fill_vehicle(vehicle: Vehicle) -> None:
    vehicle.plate = request.form.get("plate", "").strip().upper()
    vehicle.brand = request.form.get("brand", "").strip()
    vehicle.model = request.form.get("model", "").strip()
    vehicle.year = parse_int(request.form.get("year"), 0) or None
    vehicle.color = request.form.get("color") or None
    vehicle.client_id = parse_int(request.form.get("client_id"))
