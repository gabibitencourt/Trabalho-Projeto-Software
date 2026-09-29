from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventos.adapters.orm import metadata, start_mappers
from eventos.adapters.repository import (
    SqlAlchemyInscricaoRepository,
    SqlAlchemyPagamentoRepository,
    SqlAlchemyEventoRepository,
    SqlAlchemyLoteDeIngressoRepository
)
from eventos.domain.model import OperacaoInvalidaError, Participante
from eventos.service_layer import services


def _serializar_inscricao(inscricao):
    return {
        "identificador": inscricao.identificador,
        "participante": {
            "identificador": inscricao.participante.identificador,
            "nome": inscricao.participante.nome,
            "email": inscricao.participante.email,
            "documento": inscricao.participante.documento,
        },
        "lote": inscricao.lote,
        "status": inscricao.status.value,
        "checkin": (
            inscricao.checkin.data_hora.isoformat()
            if inscricao.checkin is not None
            else None
        ),
    }


def _serializar_pagamento(pagamento):
    return {
        "identificador": pagamento.identificador,
        "inscricao_id": pagamento.inscricao.identificador,
        "valor": pagamento.valor,
        "status": pagamento.status.value,
    }

def _serializar_lote(lote):
    return {
        "identificador": lote.identificador,
        "evento_id": lote.evento_id,
        "nome": lote.nome,
        "preco": lote.preco,
        "quant_total": lote.quant_total,
        "quanto_vendidae": lote.quant_vendida
    }


def create_app(session=None):
    start_mappers()
    if session is None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        session = sessionmaker(bind=engine)()

    repository = SqlAlchemyInscricaoRepository(session)
    repositorio_pagamento = SqlAlchemyPagamentoRepository(session)
    repositorio_evento = SqlAlchemyEventoRepository(session)
    repositorio_lote_ingresso = SqlAlchemyLoteDeIngressoRepository(session)
    app = Flask(__name__)

    @app.errorhandler(services.InscricaoNaoEncontradaError)
    def inscricao_nao_encontrada(error):
        return jsonify({"erro": str(error)}), 404

    @app.errorhandler(services.PagamentoNaoEncontradoError)
    def pagamento_nao_encontrado(error):
        return jsonify({"erro": str(error)}), 404

    @app.errorhandler(OperacaoInvalidaError)
    def operacao_invalida(error):
        return jsonify({"erro": str(error)}), 400

    @app.errorhandler(ValueError)
    def requisicao_invalida(error):
        return jsonify({"erro": str(error)}), 400

    @app.post("/inscricoes")
    def criar_inscricao():
        dados = request.get_json(silent=True) or {}
        try:
            participante = Participante(**dados["participante"])
            inscricao = services.criar_inscricao(
                identificador=dados["identificador"],
                participante=participante,
                lote=dados["lote"],
                repositorio=repository,
            )
        except KeyError as error:
            raise ValueError(f"campo obrigatorio: {error.args[0]}") from error

        session.commit()
        return jsonify(_serializar_inscricao(inscricao)), 201

    @app.get("/inscricoes/<int:identificador>")
    def obter_inscricao(identificador):
        inscricao = services.obter_inscricao(identificador, repository)
        return jsonify(_serializar_inscricao(inscricao))

    @app.post("/inscricoes/<int:identificador>/confirmar")
    def confirmar_inscricao(identificador):
        inscricao = services.confirmar_inscricao(identificador, repository)
        session.commit()
        return jsonify(_serializar_inscricao(inscricao))

    @app.post("/inscricoes/<int:identificador>/cancelar")
    def cancelar_inscricao(identificador):
        inscricao = services.cancelar_inscricao(identificador, repository)
        session.commit()
        return jsonify(_serializar_inscricao(inscricao))

    @app.post("/pagamentos")
    def registrar_pagamento():
        dados = request.get_json(silent=True) or {}
        try:
            pagamento = services.registrar_pagamento(
                identificador=dados["identificador"],
                inscricao_id=dados["inscricao_id"],
                valor=dados["valor"],
                repositorio_pagamento=repositorio_pagamento,
                repositorio_inscricao=repository,
            )
        except KeyError as error:
            raise ValueError(f"campo obrigatorio: {error.args[0]}") from error

        session.commit()
        return jsonify(_serializar_pagamento(pagamento)), 201

    @app.get("/pagamentos/<int:identificador>")
    def obter_pagamento(identificador):
        pagamento = services.obter_pagamento(identificador, repositorio_pagamento)
        return jsonify(_serializar_pagamento(pagamento))

    @app.post("/pagamentos/<int:identificador>/aprovar")
    def aprovar_pagamento(identificador):
        pagamento = services.aprovar_pagamento(identificador, repositorio_pagamento)
        session.commit()
        return jsonify(_serializar_pagamento(pagamento))

    @app.post("/pagamentos/<int:identificador>/recusar")
    def recusar_pagamento(identificador):
        pagamento = services.recusar_pagamento(identificador, repositorio_pagamento)
        session.commit()
        return jsonify(_serializar_pagamento(pagamento))

    @app.post("/pagamentos/<int:identificador>/estornar")
    def estornar_pagamento(identificador):
        pagamento = services.estornar_pagamento(identificador, repositorio_pagamento)
        session.commit()
        return jsonify(_serializar_pagamento(pagamento))

    @app.post("/pagamentos/<int:identificador>/confirmar-inscricao")
    def confirmar_inscricao_apos_pagamento(identificador):
        inscricao = services.confirmar_inscricao_apos_pagamento(
            identificador=identificador,
            repositorio_pagamento=repositorio_pagamento,
            repositorio_inscricao=repository,
        )
        session.commit()
        return jsonify(_serializar_inscricao(inscricao))    

    @app.post("/lotes")
    def registrar_lote():
        dados = request.get_json(silent=True) or {}
        try:
            lote = services.criar_lote_ingresso(
                repositorio_evento,
                dados["evento_id"],
                dados["identificador"],
                dados["nome"],
                dados["preco"],
                dados["quant_total"],
                dados["quant_vendida"]
            )
        except KeyError as error:
            raise ValueError(f"campo obrigatorio: {error.args[0]}") from error

        session.commit()
        return jsonify(_serializar_lote(lote)), 201

    @app.get("/lote/<int:identificador>")
    def obter_lote(identificador):
        lote = services.obter_lote(repositorio_lote_ingresso, identificador)
        return jsonify(_serializar_lote(lote))
    return app

app = create_app()
