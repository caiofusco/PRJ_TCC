from datetime import datetime, time, timedelta

from flask import Blueprint, render_template
from flask_login import login_required

from ..models import Appointment, Client, Product, Sale, User, WorkOrder
from ..ai_scheduler import suggest_restock

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/")
@login_required
def index():
    now = datetime.utcnow()
    today_start = datetime.combine(now.date(), time(0, 0))
    today_end = today_start + timedelta(days=1)

    kpis = {
        "clientes": Client.query.filter_by(status="ATIVO").count(),
        "agendamentos_hoje": Appointment.query.filter(
            Appointment.scheduled_start >= today_start,
            Appointment.scheduled_start < today_end,
            Appointment.status.notin_(["CANCELADO"]),
        ).count(),
        "os_abertas": WorkOrder.query.filter(WorkOrder.status.in_(["ABERTA", "EM_ANDAMENTO"])).count(),
        "tecnicos": User.query.filter_by(role="TECNICO", status="ATIVO").count(),
        "vendas": Sale.query.count(),
    }

    upcoming = (
        Appointment.query.filter(
            Appointment.scheduled_start >= now,
            Appointment.status.notin_(["CANCELADO", "CONCLUIDA"]),
        )
        .order_by(Appointment.scheduled_start.asc())
        .limit(6)
        .all()
    )
    open_orders = (
        WorkOrder.query.filter(WorkOrder.status.in_(["ABERTA", "EM_ANDAMENTO"]))
        .order_by(WorkOrder.opening_date.desc())
        .limit(6)
        .all()
    )
    low_stock = Product.query.filter(Product.active.is_(True), Product.quantity <= Product.min_quantity).order_by(Product.quantity.asc()).limit(6).all()

    article_metrics = [
        {"label": "Tempo de agendamento", "before": "15 min", "after": "5 min", "gain": "-67%"},
        {"label": "Erros de comunicação", "before": "12/semana", "after": "2/semana", "gain": "-83%"},
        {"label": "Precisão na alocação", "before": "60%", "after": "92%", "gain": "+53%"},
    ]

    return render_template(
        "dashboard.html",
        kpis=kpis,
        upcoming=upcoming,
        open_orders=open_orders,
        low_stock=low_stock,
        restock_suggestions=suggest_restock(),
        article_metrics=article_metrics,
    )
