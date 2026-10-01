from __future__ import annotations

from flask import Flask, Response, jsonify, render_template, request

from sciCalc.evaluator import CalculatorError, evaluate


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.post("/api/calculate")
    def calculate() -> tuple[Response, int]:
        payload = request.get_json(silent=True) or {}
        expression = payload.get("expression", "")

        if not isinstance(expression, str):
            return jsonify(error="expression must be a string"), 400

        try:
            result = evaluate(expression)
        except CalculatorError as exc:
            return jsonify(error=str(exc)), 400

        return jsonify(result=result), 200

    return app


app = create_app()
