from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base, get_brazil_time


class CartaoCredito(Base):
    __tablename__ = "cartoes_credito"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)                # "Nubank", "Inter", "Itaú"
    bandeira = Column(String, nullable=True)              # "Visa", "Mastercard", "Elo"
    ultimos_digitos = Column(String(4), nullable=True)    # "1234"
    cor = Column(String, nullable=True, default="#6B7280")  # hex color
    dia_fechamento = Column(Integer, nullable=False, default=1)   # 1-31
    dia_vencimento = Column(Integer, nullable=False, default=10)  # 1-31
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=get_brazil_time)

    despesas = relationship("Despesa", back_populates="cartao", lazy="select")
