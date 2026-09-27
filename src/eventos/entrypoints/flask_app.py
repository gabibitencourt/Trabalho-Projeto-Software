from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventos.adapters import orm
from eventos.adapters.repository import (
    SqlAlchemyInscricaoRepository,
    SqlAlchemyPagamentoRepository,
)
from eventos.domain.model import OperacaoInvalidaError
from eventos.service_layer import services


def create_app(db_url="sqlite:///:memory:"):
    engine = create_engine(db_url)
    orm.start_mappers()
    orm.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    app = Flask(__name__)
    app.session_factory = session_factory

    @app.post("/pagamentos")
    def processar_pagamento():
        dados = request.get_json()
        session = session_factory()
        try:
            pagamento = services.processar_pagamento(
                identificador=dados["identificador"],
                inscricao_id=dados["inscricao_id"],
                valor=dados["valor"],
                aprovado=dados["aprovado"],
                repositorio_pagamentos=SqlAlchemyPagamentoRepository(session),
                repositorio_inscricoes=SqlAlchemyInscricaoRepository(session),
            )
            session.commit()
            resposta = {
                "identificador": pagamento.identificador,
                "status": pagamento.status.value,
            }
        except OperacaoInvalidaError as erro:
            session.rollback()
            return jsonify({"erro": str(erro)}), 400
        finally:
            session.close()

        return jsonify(resposta), 201

    @app.post("/pagamentos/<int:pagamento_id>/confirmar-inscricao")
    def confirmar_inscricao(pagamento_id):
        session = session_factory()
        try:
            services.confirmar_inscricao_apos_pagamento(
                pagamento_id=pagamento_id,
                repositorio_pagamentos=SqlAlchemyPagamentoRepository(session),
                repositorio_inscricoes=SqlAlchemyInscricaoRepository(session),
            )
            session.commit()
        except OperacaoInvalidaError as erro:
            session.rollback()
            return jsonify({"erro": str(erro)}), 400
        finally:
            session.close()

        return jsonify({"mensagem": "inscricao confirmada"}), 200

    return app
