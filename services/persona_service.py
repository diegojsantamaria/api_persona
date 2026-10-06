# services/persona_service.py
# Capa de servicios: reglas de negocio. Usa el repositorio para guardar y leer.

from __future__ import annotations

from dataclasses import replace

from models.persona import ActualizarPersonaDTO, CrearPersonaDTO, Persona
from repositories.persona_repository import PersonaRepository


class PersonaYaExisteError(Exception):
    """Se intentó crear una persona con un DNI que ya está registrado."""

    def __init__(self, dni: str) -> None:
        super().__init__(f"Ya existe una persona con DNI {dni}")
        self.dni = dni


class PersonaNoEncontradaError(Exception):
    """No hay ninguna persona con ese DNI."""

    def __init__(self, dni: str) -> None:
        super().__init__(f"No existe una persona con DNI {dni}")
        self.dni = dni


class NombreInvalidoError(Exception):
    """El nombre no cumple las reglas de formato."""


NOMBRE_LARGO_MAXIMO = 30


def validar_nombre(nombre: object) -> None:
    """
    Reglas:
    - Es texto y no está vacío.
    - Tiene como máximo 30 caracteres.
    - Una o más palabras separadas por un solo espacio.
    - Cada palabra empieza con mayúscula y sigue en minúsculas, solo letras
      (se aceptan acentos y ñ: "María", "Ñato", "Ángel").
    Lanza NombreInvalidoError si algo no se cumple.
    """
    if not isinstance(nombre, str) or not nombre:
        raise NombreInvalidoError("El nombre es obligatorio")

    if len(nombre) > NOMBRE_LARGO_MAXIMO:
        raise NombreInvalidoError(
            f"El nombre no puede tener más de {NOMBRE_LARGO_MAXIMO} caracteres"
        )

    for palabra in nombre.split(" "):
        if not palabra:
            raise NombreInvalidoError(
                "El nombre no puede tener espacios al principio, al final ni dobles"
            )
        if not palabra.isalpha():
            raise NombreInvalidoError(
                f'"{palabra}" tiene caracteres que no son letras'
            )
        resto = palabra[1:]
        if not palabra[0].isupper() or (resto and not resto.islower()):
            raise NombreInvalidoError(
                f'"{palabra}" debe empezar con mayúscula y seguir en minúsculas'
            )


class PersonaService:
    def __init__(self, repositorio: PersonaRepository) -> None:
        self._repo = repositorio

    def listar(self) -> list[Persona]:
        return self._repo.listar()

    def obtener(self, dni: str) -> Persona:
        persona = self._repo.obtener(dni)
        if persona is None:
            raise PersonaNoEncontradaError(dni)
        return persona

    def crear(self, dto: CrearPersonaDTO) -> Persona:
        validar_nombre(dto.nombre)

        # Validación: el DNI no puede estar repetido.
        if self._repo.obtener(dto.dni) is not None:
            raise PersonaYaExisteError(dto.dni)

        persona = Persona(dni=dto.dni, nombre=dto.nombre)
        try:
            return self._repo.crear(persona)
        except KeyError:
            # Otro request pudo haberla creado entre el chequeo y el guardado.
            raise PersonaYaExisteError(dto.dni)

    def actualizar(self, dni: str, dto: ActualizarPersonaDTO) -> Persona:
        actual = self.obtener(dni)  # lanza PersonaNoEncontradaError si no existe
        if dto.nombre is None:
            return actual  # no hay nada para cambiar

        validar_nombre(dto.nombre)
        actualizada = replace(actual, nombre=dto.nombre)
        resultado = self._repo.actualizar(actualizada)
        if resultado is None:
            # La borraron entre la lectura y la actualización.
            raise PersonaNoEncontradaError(dni)
        return resultado

    def eliminar(self, dni: str) -> None:
        if not self._repo.eliminar(dni):
            raise PersonaNoEncontradaError(dni)