# models/persona.py
# Capa de modelo: solo define la forma de los datos.
# Las validaciones van en la capa de servicios y el almacenamiento en el repositorio.

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass(frozen=True)
class Persona:
    """
    Entidad. El DNI es el identificador.
    Es inmutable (frozen): para modificarla se crea una nueva con
    dataclasses.replace(persona, nombre="...").
    """
    dni: str
    nombre: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CrearPersonaDTO:
    """Datos que llegan en el body de un POST."""
    dni: str
    nombre: str

    @classmethod
    def from_dict(cls, datos: dict[str, Any]) -> CrearPersonaDTO:
        return cls(
            dni=datos.get("dni", ""),
            nombre=datos.get("nombre", ""),
        )


@dataclass
class ActualizarPersonaDTO:
    """
    Datos para un PUT/PATCH. El DNI no se cambia: viene en la URL
    (/personas/<dni>) porque es el identificador.
    """
    nombre: Optional[str] = None

    @classmethod
    def from_dict(cls, datos: dict[str, Any]) -> ActualizarPersonaDTO:
        return cls(nombre=datos.get("nombre"))