"""Local demonstration UI for the JSON export library."""

import json
from datetime import datetime

from flask import Flask, Response, jsonify, render_template, request

from export_json import export_visible_to_json, make_export_filename


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024

    @app.get("/")
    def index():
        rows = [
            {"id": index, "name": name, "department": department, "active": index % 3 != 0}
            for index, (name, department) in enumerate([
                ("Анна", "Разработка"), ("Иван", "Дизайн"),
                ("Мария", "Разработка"), ("Пётр", "Аналитика"),
                ("Ольга", "Дизайн"), ("Алексей", "Аналитика"),
                ("Елена", "Разработка"), ("Дмитрий", "Дизайн"),
                ("София", "Аналитика"), ("Николай", "Разработка"),
                ("Ирина", "Дизайн"), ("Михаил", "Аналитика"),
            ], start=1)
        ]
        return render_template("index.html", rows=rows)

    @app.post("/export")
    def export():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="invalid_request"), 400
        try:
            payload = export_visible_to_json(body.get("data"), body.get("filters_applied"))
        except ValueError as error:
            if str(error) == "Empty dataset":
                return jsonify(error="empty_dataset"), 409
            return jsonify(error="export_failed"), 422
        except (TypeError, RecursionError):
            return jsonify(error="export_failed"), 422
        except Exception:
            app.logger.exception("Export failed")
            return jsonify(error="export_failed"), 500
        moment = datetime.fromisoformat(json.loads(payload)["export_date"].replace("Z", "+00:00"))
        response = Response(payload, content_type="application/json; charset=utf-8")
        response.headers["Content-Disposition"] = f'attachment; filename="{make_export_filename(moment)}"'
        response.headers["Cache-Control"] = "no-store"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
