from sqlalchemy.orm import registry, relationship
from eventos.domain.model import Evento, LoteDeIngresso, StatusEvento
from sqlalchemy import Column, DateTime, Enum , ForeignKey, Integer, MetaData, String, Table, Float, Date

from eventos.domain.model import (
    Evento,
    Inscricao,
    LoteDeIngresso,
    Organizador,
    Pagamento,
    Participante,
    RoleOrganizador,
    StatusEvento,
    StatusInscricao,
    StatusPagamento,
)


metadata = MetaData()
mapper_registry = registry(metadata=metadata)

eventos = Table(
	"eventos",
	metadata,
	Column("identificador", Integer, primary_key=True),
	Column("nome", String(255), nullable=False),
	Column("data", Date, nullable=False),
	Column("local", String(255), nullable=False),
	Column("status", Enum(StatusEvento), nullable=False),
)

lotes = Table(
	"lotes",
	metadata,
	Column("identificador", Integer, primary_key=True, autoincrement=True),
	Column("evento_id", ForeignKey("eventos.identificador"), nullable=False),
	Column("nome", String(255), nullable=False),
	Column("preco", Float, nullable=False),
	Column("quant_total", Integer, nullable=False),
	Column("quant_vendida", Integer, nullable=False),
)

participantes = Table(
    "participantes",
    metadata,
    Column("identificador", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("email", String(255), nullable=False),
    Column("documento", String(14), nullable=False, unique=True),
)

organizadores = Table(
    "organizadores",
    metadata,
    Column("identificador", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("email", String(255), nullable=False),
    Column("role", Enum(RoleOrganizador, native_enum=False), nullable=False),
)

inscricoes = Table(
    "inscricoes",
    metadata,
    Column("identificador", Integer, primary_key=True),
    Column("participante_id", ForeignKey("participantes.identificador"), nullable=False),
    Column("lote", String(255), nullable=False),
    Column("status", Enum(StatusInscricao, native_enum=False), nullable=False),
    Column("checkin_data_hora", DateTime, key="_checkin_data_hora", nullable=True),
)

pagamentos = Table(
    "pagamentos",
    metadata,
    Column("identificador", String(255), primary_key=True),
    Column("inscricao_id", Integer, ForeignKey("inscricoes.identificador"), nullable=True),
    Column("valor", Float, nullable=False),
    Column("status", Enum(StatusPagamento, native_enum=False), nullable=False),
)

_mappers_started = False


def start_mappers():
    if Evento in {m.class_ for m in mapper_registry.mappers}:
        return

    mapper_registry.map_imperatively(Participante, participantes)
    mapper_registry.map_imperatively(Organizador, organizadores)
    mapper_registry.map_imperatively(
        Inscricao,
        inscricoes,
        properties={
            "participante": relationship(Participante),
        },
    )
    mapper_registry.map_imperatively(LoteDeIngresso, lotes)
    mapper_registry.map_imperatively(
        Evento,
        eventos,
        properties={
            "_lotes": relationship(
                LoteDeIngresso,
                cascade="all, delete-orphan",
                collection_class=list,
            ),
        },
    )
    mapper_registry.map_imperatively(
        Pagamento,
        pagamentos,
        properties={
            "inscricao": relationship(Inscricao),
        },
    )
