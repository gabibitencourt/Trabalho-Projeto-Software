from sqlalchemy import Column, Date, Enum, Float, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

from eventos.domain.model import Evento, LoteDeIngresso, StatusEvento
from sqlalchemy import Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, MetaData, String, Table, Double
from sqlalchemy.orm import registry, relationship

from eventos.domain.model import (
    Inscricao,
    Organizador,
    Participante,
    RoleOrganizador,
    StatusInscricao,
    LoteDeIngresso
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

def start_mappers():
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
    Column("role", SqlEnum(RoleOrganizador, native_enum=False), nullable=False),
)

inscricoes = Table(
    "inscricoes",
    metadata,
    Column("identificador", Integer, primary_key=True),
    Column("participante_id", ForeignKey("participantes.identificador"), nullable=False),
    Column("lote", String(255), nullable=False),
    Column("status", SqlEnum(StatusInscricao, native_enum=False), nullable=False),
    Column("checkin_data_hora", DateTime, key="_checkin_data_hora", nullable=True),
)

lotes_ingresso = Table(
    "lote_ingresso",
    metadata,
    Column("identificador", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("preco", Double, nullable=False),
    Column("quant_total", Integer, nullable=False),
    Column("quant_vendida", Integer, nullable=False)
)

_mappers_started = False


def start_mappers():
    global _mappers_started
    if _mappers_started:
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
    mapper_registry.map_imperatively(LoteDeIngresso, lotes_ingresso)
    _mappers_started = True
