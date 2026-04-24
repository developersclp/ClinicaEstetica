from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from database import Base, get_brazil_time


# Many-to-many: plano <-> servicos
plano_servicos = Table(
    "plano_servicos",
    Base.metadata,
    Column("plano_id", Integer, ForeignKey("planos.id", ondelete="CASCADE"), primary_key=True),
    Column("servico_id", Integer, ForeignKey("servicos.id", ondelete="CASCADE"), primary_key=True),
)


class Plano(Base):
    __tablename__ = "planos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    quantidade_sessoes = Column(Integer, nullable=False)
    valor = Column(Float, nullable=False, default=0.0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=get_brazil_time)

    servicos = relationship("Servico", secondary=plano_servicos, lazy="joined")
    clientes = relationship("PlanoCliente", back_populates="plano", cascade="all, delete-orphan")


class PlanoCliente(Base):
    __tablename__ = "plano_clientes"

    id = Column(Integer, primary_key=True, index=True)
    plano_id = Column(Integer, ForeignKey("planos.id", ondelete="CASCADE"), nullable=False)
    agenda_cliente_id = Column(Integer, ForeignKey("agenda_clientes.id", ondelete="CASCADE"), nullable=False)
    sessoes_restantes = Column(Integer, nullable=False)
    observacoes = Column(Text, nullable=True)
    pagamento_id = Column(Integer, ForeignKey("pagamentos.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, nullable=False, default="ativo")  # ativo | concluido | cancelado
    created_at = Column(DateTime(timezone=True), default=get_brazil_time)

    plano = relationship("Plano", back_populates="clientes", lazy="joined")
    cliente = relationship("AgendaCliente", backref="planos_cliente", lazy="joined")
    pagamento = relationship("Pagamento", lazy="joined")
