import firebase_admin
from firebase_admin import credentials, firestore
import os

# Inicializar Firebase solo una vez
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate('/etc/secrets/nequi-comprobantes-firebase-adminsdk-fbsvc-19b6f5603c.json')
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

class Whitelist:
    def __init__(self):
        self.collection = db.collection("Telegram")
        self.document = self.collection.document("bot")
        self.field = "ids_autorizados"

    def _get_ids(self):
        doc = self.document.get()
        if doc.exists and self.field in doc.to_dict():
            return set(doc.to_dict()[self.field])
        return set()

    def _set_ids(self, ids):
        self.document.set({self.field: list(ids)}, merge=True)

    def add_id(self, id: int) -> None:
        ids = self._get_ids()
        ids.add(id)
        self._set_ids(ids)

    def remove_id(self, id: int) -> None:
        ids = self._get_ids()
        if id in ids:
            ids.remove(id)
            self._set_ids(ids)

    def is_authorized(self, id: int) -> bool:
        ids = self._get_ids()
        return id in ids 