from enum import Enum


class UserRole(str, Enum):
    CLIENTE = "cliente"
    AJUDANTE = "ajudante"
    AJUDANTE_MECANICO = "ajudante_mecanico"
    MECANICO = "mecanico"
    GERENTE_MECANICA = "gerente_mecanica"
    ADMINISTRADOR = "administrador"
