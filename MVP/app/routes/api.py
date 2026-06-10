import json

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from ..ai_scheduler import appointment_conflicts, suggest_restock, suggest_schedule_slots
from ..extensions import db
from ..models import AIRecommendationLog, Vehicle
from .common import parse_datetime_local, parse_int

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/vehicles/by-client/<int:client_id>")
@login_required
def vehicles_by_client(client_id):
    vehicles = Vehicle.query.filter_by(client_id=client_id).order_by(Vehicle.plate.asc()).all()
    return jsonify([
        {"id": vehicle.id, "label": vehicle.label, "plate": vehicle.plate}
        for vehicle in vehicles
    ])


@bp.route("/ai/schedule", methods=["POST"])
@login_required
def ai_schedule():
    payload = request.get_json(silent=True) or request.form.to_dict()
    service_id = parse_int(payload.get("service_id"))
    if not service_id:
        return jsonify({"error": "service_id é obrigatório"}), 400
    result = suggest_schedule_slots(
        service_id=service_id,
        start_date=payload.get("start_date"),
        days=parse_int(payload.get("days"), 7),
        top_n=parse_int(payload.get("top_n"), 6),
    )
    log = AIRecommendationLog(
        request_type="schedule_suggestion",
        payload=json.dumps(payload, ensure_ascii=False),
        result=json.dumps(result, ensure_ascii=False),
        user_id=current_user.id,
    )
    db.session.add(log)
    db.session.commit()
    return jsonify(result)


@bp.route("/ai/restock")
@login_required
def ai_restock():
    return jsonify({"suggestions": suggest_restock()})


@bp.route("/appointments/check-conflict", methods=["POST"])
@login_required
def check_conflict():
    payload = request.get_json(silent=True) or request.form.to_dict()
    technician_id = parse_int(payload.get("technician_id"))
    start = parse_datetime_local(payload.get("start"))
    end = parse_datetime_local(payload.get("end"))
    conflicts = appointment_conflicts(technician_id, start, end)
    return jsonify(
        {
            "has_conflict": bool(conflicts),
            "conflicts": [
                {
                    "id": item.id,
                    "client": item.client.name,
                    "service": item.service.name,
                    "start": item.scheduled_start.isoformat(timespec="minutes"),
                    "end": item.scheduled_end.isoformat(timespec="minutes"),
                }
                for item in conflicts
            ],
        }
    )
