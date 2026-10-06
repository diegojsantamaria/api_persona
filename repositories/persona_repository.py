# repositories/persona_repository.py
# Capa de repositorio: solo guarda y recupera datos. No valida reglas de negocio.

from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Lock
from typing import Optional

from models.persona import Persona


class PersonaRepository(ABC):
    """
    Contrato del repositorio. El servicio depende de esta interfaz,
    así después podés cambiar la implementación en memoria por una
    base de datos sin tocar la capa de servicios.
    """

    @abstractmethod
    def listar(self) -> list[Persona]: ...

    @abstractmethod
    def obtener(self, dni: str) -> Optional[Persona]: ...

    @abstractmethod
    def crear(self, persona: Persona) -> Persona: ...

    @abstractmethod
    def actualizar(self, persona: Persona) -> Optional[Persona]: ...

    @abstractmethod
    def eliminar(self, dni: str) -> bool: ...


class PersonaRepositoryMemoria(PersonaRepository):
    """
    Implementación en memoria con un dict {dni: Persona}.
    Los datos se pierden al reiniciar la app.

    Usa un Lock porque el servidor de Flask atiende requests en varios hilos.
    Como Persona es inmutable, se puede devolver tal cual sin copiarla.
    """

    def __init__(self) -> None:
        self._personas: dict[str, Persona] = {}
        self._lock = Lock()

    def listar(self) -> list[Persona]:
        with self._lock:
            return list(self._personas.values())

    def obtener(self, dni: str) -> Optional[Persona]:
        with self._lock:
            return self._personas.get(dni)

    def crear(self, persona: Persona) -> Persona:
        with self._lock:
            if persona.dni in self._personas:
                raise KeyError(f"Ya existe una persona con DNI {persona.dni}")
            self._personas[persona.dni] = persona
            return persona

    def actualizar(self, persona: Persona) -> Optional[Persona]:
        """Reemplaza la persona guardada. Devuelve None si el DNI no existe."""
        with self._lock:
            if persona.dni not in self._personas:
                return None
            self._personas[persona.dni] = persona
            return persona

    def eliminar(self, dni: str) -> bool:
        """Devuelve True si la borró, False si no existía."""
        with self._lock:
            return self._personas.pop(dni, None) is not None