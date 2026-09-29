from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventos.adapters.orm import metadata, start_mappers
from eventos.adapters.repository import SqlAlchemyInscricaoRepository
from eventos.domain.model import Participante
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


def create_app(session=None):
    start_mappers()
    if session is None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        session = sessionmaker(bind=engine)()

    repository = SqlAlchemyInscricaoRepository(session)
    app = Flask(__name__)

    @app.errorhandler(services.InscricaoNaoEncontradaError)
    def inscricao_nao_encontrada(error):
        return jsonify({"erro": str(error)}), 404

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

    return app


app = create_app()
