from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="ATENDENTE")
    specialties = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ATIVO")

    technician_appointments = db.relationship(
        "Appointment",
        back_populates="technician",
        foreign_keys="Appointment.technician_id",
    )
    created_appointments = db.relationship(
        "Appointment",
        back_populates="created_by",
        foreign_keys="Appointment.created_by_id",
    )
    technician_work_orders = db.relationship(
        "WorkOrder",
        back_populates="technician",
        foreign_keys="WorkOrder.technician_id",
    )

    @property
    def is_active(self):
        return self.status == "ATIVO"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "ADMIN"

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Client(TimestampMixin, db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    cpf_cnpj = db.Column(db.String(20), nullable=True, unique=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ATIVO")

    vehicles = db.relationship("Vehicle", back_populates="client", cascade="all, delete-orphan")
    appointments = db.relationship("Appointment", back_populates="client")
    work_orders = db.relationship("WorkOrder", back_populates="client")
    sales = db.relationship("Sale", back_populates="client")

    def __repr__(self) -> str:
        return f"<Client {self.name}>"


class Vehicle(TimestampMixin, db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(12), nullable=False, unique=True, index=True)
    brand = db.Column(db.String(60), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    color = db.Column(db.String(40), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)

    client = db.relationship("Client", back_populates="vehicles")
    appointments = db.relationship("Appointment", back_populates="vehicle")
    work_orders = db.relationship("WorkOrder", back_populates="vehicle")

    @property
    def label(self) -> str:
        return f"{self.plate} - {self.brand} {self.model}"

    def __repr__(self) -> str:
        return f"<Vehicle {self.plate}>"


class Service(TimestampMixin, db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(80), nullable=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    estimated_minutes = db.Column(db.Integer, nullable=False, default=60)
    active = db.Column(db.Boolean, nullable=False, default=True)

    appointments = db.relationship("Appointment", back_populates="service")
    work_orders = db.relationship("WorkOrder", back_populates="main_service")
    items = db.relationship("WorkOrderItem", back_populates="service")

    def __repr__(self) -> str:
        return f"<Service {self.name}>"


class Appointment(TimestampMixin, db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    scheduled_start = db.Column(db.DateTime, nullable=False, index=True)
    scheduled_end = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="AGENDADO")
    notes = db.Column(db.Text, nullable=True)
    ai_score = db.Column(db.Numeric(5, 2), nullable=True)
    ai_reason = db.Column(db.String(255), nullable=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False, index=True)
    technician_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    client = db.relationship("Client", back_populates="appointments")
    vehicle = db.relationship("Vehicle", back_populates="appointments")
    service = db.relationship("Service", back_populates="appointments")
    technician = db.relationship("User", back_populates="technician_appointments", foreign_keys=[technician_id])
    created_by = db.relationship("User", back_populates="created_appointments", foreign_keys=[created_by_id])
    work_order = db.relationship("WorkOrder", back_populates="appointment", uselist=False)

    @property
    def duration_minutes(self) -> int:
        return int((self.scheduled_end - self.scheduled_start).total_seconds() // 60)

    def __repr__(self) -> str:
        return f"<Appointment {self.id} {self.scheduled_start}>"


class WorkOrder(TimestampMixin, db.Model):
    __tablename__ = "work_orders"

    id = db.Column(db.Integer, primary_key=True)
    opening_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    closing_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="ABERTA")
    problem_description = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=True)
    labor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    parts_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    technician_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    main_service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=True, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True, unique=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    client = db.relationship("Client", back_populates="work_orders")
    vehicle = db.relationship("Vehicle", back_populates="work_orders")
    technician = db.relationship("User", back_populates="technician_work_orders", foreign_keys=[technician_id])
    main_service = db.relationship("Service", back_populates="work_orders")
    appointment = db.relationship("Appointment", back_populates="work_order")
    items = db.relationship("WorkOrderItem", back_populates="work_order", cascade="all, delete-orphan")
    sale = db.relationship("Sale", back_populates="work_order", uselist=False)

    @property
    def execution_minutes(self) -> int | None:
        if not self.closing_date:
            return None
        return int((self.closing_date - self.opening_date).total_seconds() // 60)

    def recalc_totals(self) -> None:
        labor = Decimal("0.00")
        for item in self.items:
            labor += Decimal(item.total or 0)
        self.labor_total = labor
        self.total_value = labor + Decimal(self.parts_total or 0)

    def __repr__(self) -> str:
        return f"<WorkOrder {self.id}>"


class WorkOrderItem(TimestampMixin, db.Model):
    __tablename__ = "work_order_items"

    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey("work_orders.id"), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    work_order = db.relationship("WorkOrder", back_populates="items")
    service = db.relationship("Service", back_populates="items")

    def recalc(self) -> None:
        self.total = Decimal(self.quantity or 0) * Decimal(self.unit_price or 0)


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    min_quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)

    sale_items = db.relationship("SaleItem", back_populates="product")
    movements = db.relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")

    @property
    def needs_restock(self) -> bool:
        return self.quantity <= self.min_quantity

    def __repr__(self) -> str:
        return f"<Product {self.name}>"


class StockMovement(TimestampMixin, db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    product = db.relationship("Product", back_populates="movements")


class Sale(TimestampMixin, db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="PAGA")
    payment_method = db.Column(db.String(40), nullable=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True, index=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey("work_orders.id"), nullable=True, unique=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    client = db.relationship("Client", back_populates="sales")
    work_order = db.relationship("WorkOrder", back_populates="sale")
    items = db.relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    def recalc_total(self) -> None:
        total = Decimal("0.00")
        for item in self.items:
            total += Decimal(item.total or 0)
        self.total_value = total


class SaleItem(TimestampMixin, db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    sale = db.relationship("Sale", back_populates="items")
    product = db.relationship("Product", back_populates="sale_items")

    def recalc(self) -> None:
        self.total = Decimal(self.quantity or 0) * Decimal(self.unit_price or 0)


class AIRecommendationLog(TimestampMixin, db.Model):
    __tablename__ = "ai_recommendation_logs"

    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(60), nullable=False)
    payload = db.Column(db.Text, nullable=True)
    result = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)


def seed_data() -> None:
    """Carrega dados de demonstração sem duplicar registros."""
    if User.query.first():
        return

    admin = User(name="Administrador", email="admin@oficina.local", role="ADMIN", status="ATIVO")
    admin.set_password("admin123")
    attendant = User(name="Atendente", email="atendente@oficina.local", role="ATENDENTE", status="ATIVO")
    attendant.set_password("atendente123")
    tech1 = User(
        name="Marcos Silva",
        email="marcos@oficina.local",
        role="TECNICO",
        specialties="diagnóstico eletrônico, ecu, remap, injeção eletrônica",
        status="ATIVO",
    )
    tech1.set_password("tecnico123")
    tech2 = User(
        name="Rafael Costa",
        email="rafael@oficina.local",
        role="TECNICO",
        specialties="troca de óleo, freios, revisão, suspensão, manutenção preventiva",
        status="ATIVO",
    )
    tech2.set_password("tecnico123")
    db.session.add_all([admin, attendant, tech1, tech2])
    db.session.flush()

    services = [
        Service(
            name="Diagnóstico eletrônico",
            category="diagnóstico",
            description="Leitura de módulos, falhas e parâmetros do veículo.",
            base_price=Decimal("180.00"),
            estimated_minutes=60,
        ),
        Service(
            name="Remap de ECU",
            category="ecu",
            description="Ajuste de mapas de injeção e performance com validação.",
            base_price=Decimal("850.00"),
            estimated_minutes=180,
        ),
        Service(
            name="Limpeza de bicos injetores",
            category="injeção",
            description="Teste, limpeza e equalização dos bicos injetores.",
            base_price=Decimal("320.00"),
            estimated_minutes=120,
        ),
        Service(
            name="Troca de óleo e filtros",
            category="manutenção preventiva",
            description="Substituição de óleo, filtro de óleo e inspeção básica.",
            base_price=Decimal("120.00"),
            estimated_minutes=45,
        ),
        Service(
            name="Revisão de freios",
            category="freios",
            description="Inspeção de pastilhas, discos, fluido e sistema de frenagem.",
            base_price=Decimal("250.00"),
            estimated_minutes=90,
        ),
    ]
    db.session.add_all(services)
    db.session.flush()

    clients = [
        Client(name="Sofia Andrade", cpf_cnpj="123.456.789-10", phone="(21) 99999-1000", email="sofia@email.com", address="Rio de Janeiro - RJ"),
        Client(name="Bruno Lima", cpf_cnpj="234.567.890-11", phone="(21) 98888-2000", email="bruno@email.com", address="Niterói - RJ"),
        Client(name="Carla Menezes", cpf_cnpj="345.678.901-12", phone="(21) 97777-3000", email="carla@email.com", address="São Gonçalo - RJ"),
    ]
    db.session.add_all(clients)
    db.session.flush()

    vehicles = [
        Vehicle(plate="ABC1D23", brand="Volkswagen", model="Golf TSI", year=2018, color="Prata", client=clients[0]),
        Vehicle(plate="RJO2E45", brand="Fiat", model="Toro Diesel", year=2021, color="Preta", client=clients[1]),
        Vehicle(plate="KAI3F67", brand="Chevrolet", model="Onix", year=2020, color="Branco", client=clients[2]),
    ]
    db.session.add_all(vehicles)
    db.session.flush()

    products = [
        Product(name="Óleo 5W30 sintético", description="Lubrificante 1L", quantity=16, min_quantity=5, unit_price=Decimal("48.90")),
        Product(name="Filtro de óleo", description="Filtro linha leve", quantity=8, min_quantity=4, unit_price=Decimal("39.90")),
        Product(name="Aditivo de radiador", description="Aditivo concentrado", quantity=3, min_quantity=4, unit_price=Decimal("34.90")),
        Product(name="Jogo de velas", description="Jogo com 4 unidades", quantity=2, min_quantity=2, unit_price=Decimal("189.90")),
    ]
    db.session.add_all(products)
    db.session.flush()

    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    appointments = [
        Appointment(
            scheduled_start=now + timedelta(days=1, hours=2),
            scheduled_end=now + timedelta(days=1, hours=3),
            status="CONFIRMADO",
            notes="Cliente relatou luz de injeção acesa.",
            client=clients[0],
            vehicle=vehicles[0],
            service=services[0],
            technician=tech1,
            created_by=attendant,
        ),
        Appointment(
            scheduled_start=now + timedelta(days=2, hours=1),
            scheduled_end=now + timedelta(days=2, hours=3),
            status="AGENDADO",
            notes="Avaliar limpeza de bicos.",
            client=clients[1],
            vehicle=vehicles[1],
            service=services[2],
            technician=tech1,
            created_by=attendant,
        ),
        Appointment(
            scheduled_start=now + timedelta(days=3, hours=4),
            scheduled_end=now + timedelta(days=3, hours=5),
            status="AGENDADO",
            notes="Troca de óleo com filtro.",
            client=clients[2],
            vehicle=vehicles[2],
            service=services[3],
            technician=tech2,
            created_by=attendant,
        ),
    ]
    db.session.add_all(appointments)

    durations = [55, 70, 165, 190, 130, 115, 40, 50, 85, 95, 175, 160]
    completed_orders = []
    for i, duration in enumerate(durations):
        service = services[i % len(services)]
        tech = tech1 if service.category in {"diagnóstico", "ecu", "injeção"} else tech2
        client = clients[i % len(clients)]
        vehicle = vehicles[i % len(vehicles)]
        opened = now - timedelta(days=35 - i * 2, hours=(i % 4) + 1)
        closed = opened + timedelta(minutes=duration)
        wo = WorkOrder(
            opening_date=opened,
            closing_date=closed,
            status="CONCLUIDA",
            problem_description=f"Histórico de execução: {service.name}",
            diagnosis="Serviço concluído em ambiente de demonstração.",
            client=client,
            vehicle=vehicle,
            technician=tech,
            main_service=service,
            created_by_id=admin.id,
        )
        item = WorkOrderItem(service=service, quantity=1, unit_price=service.base_price)
        item.recalc()
        wo.items.append(item)
        wo.recalc_totals()
        completed_orders.append(wo)
    db.session.add_all(completed_orders)

    open_wo = WorkOrder(
        opening_date=now - timedelta(hours=2),
        status="EM_ANDAMENTO",
        problem_description="Veículo com falha intermitente em marcha lenta.",
        diagnosis="Em análise com scanner.",
        client=clients[0],
        vehicle=vehicles[0],
        technician=tech1,
        main_service=services[0],
        created_by_id=attendant.id,
    )
    item = WorkOrderItem(service=services[0], quantity=1, unit_price=services[0].base_price)
    item.recalc()
    open_wo.items.append(item)
    open_wo.recalc_totals()
    db.session.add(open_wo)

    db.session.commit()
