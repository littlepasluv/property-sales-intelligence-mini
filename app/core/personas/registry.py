from typing import Dict
from app.core.personas.base import PersonaBase

class PersonaRegistry:
    _registry: Dict[str, PersonaBase] = {}

    @classmethod
    def register(cls, persona: PersonaBase):
        cls._registry[persona.name] = persona

    @classmethod
    def get(cls, name: str) -> PersonaBase:
        return cls._registry.get(name)

    @classmethod
    def list_all(cls):
        return list(cls._registry.values())

registry = PersonaRegistry()
