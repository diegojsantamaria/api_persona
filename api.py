# app.py
# Capa de controladores (rutas HTTP). Conecta Flask con el servicio.

from flask import Flask, jsonify, request

from models.persona import ActualizarPersonaDTO, CrearPersonaDTO
from repositories.persona_repository import PersonaRepositoryMemoria
from services.persona_service import (
    NombreInvalidoError,  
    PersonaNoEncontradaError,
    PersonaService,
    PersonaYaExisteError,
)

app = Flask(__name__)
app.json.ensure_ascii = False  # que "María" no salga como "Mar\u00eda"

# Una sola instancia para toda la app, así los datos se mantienen entre requests.
repositorio = PersonaRepositoryMemoria()
servicio = PersonaService(repositorio)


# ---------- Manejo de errores ----------

@app.errorhandler(PersonaYaExisteError)
def dni_duplicado(e):
    return jsonify({"error": str(e)}), 409


@app.errorhandler(PersonaNoEncontradaError)
def no_encontrada(e):
    return jsonify({"error": str(e)}), 404

@app.errorhandler(NombreInvalidoError)
def nombre_invalido(e):
    return jsonify({"error": str(e)}), 400


# ---------- Rutas ----------

@app.get("/personas")
def listar_personas():
    return jsonify([p.to_dict() for p in servicio.listar()])


@app.get("/personas/<dni>")
def obtener_persona(dni):
    return jsonify(servicio.obtener(dni).to_dict())


@app.post("/personas")
def crear_persona():
    dto = CrearPersonaDTO.from_dict(request.get_json(silent=True) or {})
    persona = servicio.crear(dto)
    return jsonify(persona.to_dict()), 201


@app.put("/personas/<dni>")
def actualizar_persona(dni):
    dto = ActualizarPersonaDTO.from_dict(request.get_json(silent=True) or {})
    return jsonify(servicio.actualizar(dni, dto).to_dict())


@app.delete("/personas/<dni>")
def eliminar_persona(dni):
    servicio.eliminar(dni)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5001)