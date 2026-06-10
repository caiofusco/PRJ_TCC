from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any
import unicodedata

from .models import Appointment, Product, Service, User, WorkOrder


BUSINESS_START = time(8, 0)
BUSINESS_END = time(18, 0)
SATURDAY_END = time(13, 0)
SLOT_STEP_MINUTES = 30


def _normalize(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return ascii_text.lower().strip()


def parse_start_date(value: str | None) -> date:
    if not value:
        return datetime.utcnow().date()
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return datetime.strptime(value, "%Y-%m-%d").date()


def predict_duration_minutes(service_id: int) -> dict[str, Any]:
    """Prevê duração com histórico de OS concluídas e fallback para cadastro do serviço."""
    service = Service.query.get_or_404(service_id)
    orders = (
        WorkOrder.query.filter(
            WorkOrder.main_service_id == service_id,
            WorkOrder.status == "CONCLUIDA",
            WorkOrder.closing_date.isnot(None),
        )
        .order_by(WorkOrder.closing_date.desc())
        .limit(20)
        .all()
    )
    durations = [order.execution_minutes for order in orders if order.execution_minutes and order.execution_minutes > 0]
    estimated = int(service.estimated_minutes or 60)

    if len(durations) >= 3:
        recent = durations[:8]
        historical_avg = sum(recent) / len(recent)
        predicted = int(round((historical_avg * 0.75) + (estimated * 0.25)))
        source = f"histórico de {len(recent)} OS recentes + estimativa cadastrada"
        confidence = min(0.95, 0.60 + len(recent) * 0.04)
    elif durations:
        historical_avg = sum(durations) / len(durations)
        predicted = int(round((historical_avg * 0.45) + (estimated * 0.55)))
        source = f"histórico limitado de {len(durations)} OS + estimativa cadastrada"
        confidence = 0.55
    else:
        predicted = estimated
        source = "estimativa cadastrada; ainda sem histórico suficiente"
        confidence = 0.35

    predicted = max(30, int(round(predicted / 15) * 15))
    return {
        "service_id": service.id,
        "service_name": service.name,
        "predicted_minutes": predicted,
        "confidence": round(confidence, 2),
        "source": source,
    }


def technician_skill_score(technician: User, service: Service) -> float:
    searchable = _normalize(" ".join([technician.specialties or "", technician.name or ""]))
    terms = [_normalize(service.category), _normalize(service.name)]
    score = 0.0
    for term in terms:
        if term and term in searchable:
            score += 1.0
    service_words = [w for w in _normalize(service.name).replace("-", " ").split() if len(w) >= 4]
    for word in service_words:
        if word in searchable:
            score += 0.35
    return min(score, 2.0)


def appointment_conflicts(technician_id: int, start: datetime, end: datetime) -> list[Appointment]:
    return (
        Appointment.query.filter(
            Appointment.technician_id == technician_id,
            Appointment.status.notin_(["CANCELADO", "CONCLUIDA"]),
            Appointment.scheduled_start < end,
            Appointment.scheduled_end > start,
        )
        .order_by(Appointment.scheduled_start.asc())
        .all()
    )


def has_conflict(technician_id: int, start: datetime, end: datetime) -> bool:
    return bool(appointment_conflicts(technician_id, start, end))


def daily_workload_minutes(technician_id: int, current_day: date) -> int:
    day_start = datetime.combine(current_day, time(0, 0))
    day_end = day_start + timedelta(days=1)
    appointments = (
        Appointment.query.filter(
            Appointment.technician_id == technician_id,
            Appointment.status.notin_(["CANCELADO", "CONCLUIDA"]),
            Appointment.scheduled_start >= day_start,
            Appointment.scheduled_start < day_end,
        )
        .order_by(Appointment.scheduled_start.asc())
        .all()
    )
    return sum(appt.duration_minutes for appt in appointments)


def _business_window(current_day: date) -> tuple[datetime, datetime] | None:
    if current_day.weekday() == 6:
        return None
    end_time = SATURDAY_END if current_day.weekday() == 5 else BUSINESS_END
    return datetime.combine(current_day, BUSINESS_START), datetime.combine(current_day, end_time)


def suggest_schedule_slots(
    service_id: int,
    start_date: str | None = None,
    days: int = 7,
    top_n: int = 6,
) -> dict[str, Any]:
    """Retorna sugestões de agenda ordenadas por score operacional."""
    service = Service.query.get_or_404(service_id)
    prediction = predict_duration_minutes(service_id)
    duration = int(prediction["predicted_minutes"])
    first_day = parse_start_date(start_date)
    technicians = (
        User.query.filter(User.role == "TECNICO", User.status == "ATIVO")
        .order_by(User.name.asc())
        .all()
    )

    suggestions: list[dict[str, Any]] = []
    now = datetime.utcnow()

    for day_offset in range(max(days, 1)):
        current_day = first_day + timedelta(days=day_offset)
        window = _business_window(current_day)
        if not window:
            continue
        business_start, business_end = window
        slot = business_start
        if current_day == now.date() and slot < now:
            minutes_to_next_slot = ((now.minute // SLOT_STEP_MINUTES) + 1) * SLOT_STEP_MINUTES
            slot = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes_to_next_slot)

        while slot + timedelta(minutes=duration) <= business_end:
            end = slot + timedelta(minutes=duration)
            for tech in technicians:
                if has_conflict(tech.id, slot, end):
                    continue
                workload = daily_workload_minutes(tech.id, current_day)
                skill = technician_skill_score(tech, service)
                day_penalty = day_offset * 4.0
                hour_penalty = abs(slot.hour - 10) * 0.7
                workload_penalty = workload / 45.0
                skill_bonus = skill * 16.0
                score = 100 + skill_bonus - day_penalty - hour_penalty - workload_penalty
                reason_parts = [
                    f"duração prevista: {duration} min",
                    f"carga do técnico no dia: {workload} min",
                ]
                if skill >= 1:
                    reason_parts.append("especialidade compatível com o serviço")
                else:
                    reason_parts.append("técnico disponível sem conflito de agenda")

                suggestions.append(
                    {
                        "start": slot.isoformat(timespec="minutes"),
                        "end": end.isoformat(timespec="minutes"),
                        "date_label": slot.strftime("%d/%m/%Y"),
                        "time_label": f"{slot.strftime('%H:%M')} - {end.strftime('%H:%M')}",
                        "technician_id": tech.id,
                        "technician_name": tech.name,
                        "predicted_minutes": duration,
                        "score": round(max(score, 0), 2),
                        "reason": "; ".join(reason_parts),
                    }
                )
            slot += timedelta(minutes=SLOT_STEP_MINUTES)

    suggestions.sort(key=lambda item: (-item["score"], item["start"]))
    return {
        "service": {"id": service.id, "name": service.name},
        "prediction": prediction,
        "suggestions": suggestions[:top_n],
    }


def suggest_restock() -> list[dict[str, Any]]:
    products = (
        Product.query.filter(Product.active.is_(True), Product.quantity <= Product.min_quantity)
        .order_by(Product.quantity.asc(), Product.name.asc())
        .all()
    )
    suggestions = []
    for product in products:
        suggested_quantity = max(product.min_quantity * 2 - product.quantity, product.min_quantity)
        suggestions.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "current_quantity": product.quantity,
                "min_quantity": product.min_quantity,
                "suggested_purchase_quantity": suggested_quantity,
                "reason": "estoque igual ou abaixo do mínimo cadastrado",
            }
        )
    return suggestions
