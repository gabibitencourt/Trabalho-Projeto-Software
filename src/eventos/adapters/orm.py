from sqlalchemy import Column, Date, Enum, Float, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

from eventos.domain.model import Evento, LoteDeIngresso, StatusEvento


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
