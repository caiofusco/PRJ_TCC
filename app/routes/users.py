from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import User
from .common import admin_required

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.route("/")
@login_required
@admin_required
def index():
    users = User.query.order_by(User.role.asc(), User.name.asc()).all()
    return render_template("users/list.html", users=users)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    user = User(role="ATENDENTE", status="ATIVO")
    if request.method == "POST":
        _fill_user(user, require_password=True)
        db.session.add(user)
        db.session.commit()
        flash("Usuário cadastrado com sucesso.", "success")
        return redirect(url_for("users.index"))
    return render_template("users/form.html", user=user, title="Novo usuário")


@bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        _fill_user(user, require_password=False)
        db.session.commit()
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("users.index"))
    return render_template("users/form.html", user=user, title="Editar usuário")


@bp.route("/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Você não pode inativar sua própria conta.", "warning")
        return redirect(url_for("users.index"))
    user.status = "INATIVO" if user.status == "ATIVO" else "ATIVO"
    db.session.commit()
    flash("Status do usuário atualizado.", "info")
    return redirect(url_for("users.index"))


def _fill_user(user: User, require_password: bool) -> None:
    user.name = request.form.get("name", "").strip()
    user.email = request.form.get("email", "").strip().lower()
    user.role = request.form.get("role", "ATENDENTE")
    user.status = request.form.get("status", "ATIVO")
    user.specialties = request.form.get("specialties") or None
    password = request.form.get("password", "")
    if password or require_password:
        user.set_password(password or "123456")
