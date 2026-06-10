from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..extensions import db
from ..models import Client

bp = Blueprint("clients", __name__, url_prefix="/clients")


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Client.query
    if q:
        like = f"%{q}%"
        query = query.filter((Client.name.ilike(like)) | (Client.cpf_cnpj.ilike(like)) | (Client.phone.ilike(like)))
    clients = query.order_by(Client.name.asc()).all()
    return render_template("clients/list.html", clients=clients, q=q)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    client = Client(status="ATIVO")
    if request.method == "POST":
        _fill_client(client)
        db.session.add(client)
        db.session.commit()
        flash("Cliente cadastrado com sucesso.", "success")
        return redirect(url_for("clients.index"))
    return render_template("clients/form.html", client=client, title="Novo cliente")


@bp.route("/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def edit(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == "POST":
        _fill_client(client)
        db.session.commit()
        flash("Cliente atualizado com sucesso.", "success")
        return redirect(url_for("clients.index"))
    return render_template("clients/form.html", client=client, title="Editar cliente")


@bp.route("/<int:client_id>/delete", methods=["POST"])
@login_required
def delete(client_id):
    client = Client.query.get_or_404(client_id)
    client.status = "INATIVO"
    db.session.commit()
    flash("Cliente inativado. O histórico foi preservado.", "info")
    return redirect(url_for("clients.index"))


def _fill_client(client: Client) -> None:
    client.name = request.form.get("name", "").strip()
    client.cpf_cnpj = request.form.get("cpf_cnpj") or None
    client.phone = request.form.get("phone") or None
    client.email = request.form.get("email") or None
    client.address = request.form.get("address") or None
    client.status = request.form.get("status", "ATIVO")
