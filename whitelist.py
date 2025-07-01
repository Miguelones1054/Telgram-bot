from typing import Set, Union
import json
import os

class Whitelist:
    def __init__(self, filename: str = "authorized_ids.json"):
        self.filename = filename
        self.authorized_ids: Set[int] = set()
        self._load_whitelist()

    def _load_whitelist(self) -> None:
        """Carga la lista de IDs autorizados desde el archivo JSON"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.authorized_ids = set(data.get('authorized_ids', []))
            except Exception as e:
                print(f"Error al cargar la lista blanca: {e}")
                self.authorized_ids = set()
        else:
            # Crear archivo con lista vacía si no existe
            self._save_whitelist()

    def _save_whitelist(self) -> None:
        """Guarda la lista de IDs autorizados en el archivo JSON"""
        try:
            with open(self.filename, 'w') as f:
                json.dump({'authorized_ids': list(self.authorized_ids)}, f, indent=2)
        except Exception as e:
            print(f"Error al guardar la lista blanca: {e}")

    def add_id(self, id: int) -> None:
        """Añade un ID a la lista blanca"""
        self.authorized_ids.add(id)
        self._save_whitelist()

    def remove_id(self, id: int) -> None:
        """Elimina un ID de la lista blanca"""
        if id in self.authorized_ids:
            self.authorized_ids.remove(id)
            self._save_whitelist()

    def is_authorized(self, id: int) -> bool:
        """Verifica si un ID está autorizado"""
        return id in self.authorized_ids 