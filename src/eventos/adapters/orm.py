from sqlalchemy import Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

from eventos.domain.model import (
    Inscricao,
    Organizador,
    Participante,
    RoleOrganizador,
    StatusInscricao,
)


metadata = MetaData()
mapper_registry = registry(metadata=metadata)

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
    _mappers_started = True
