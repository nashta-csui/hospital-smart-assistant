from typing import Dict, Optional

from app.domain.pasien import Pasien
from app.repositories.interfaces import IPasienRepository

class InMemoryPasienRepository(IPasienRepository):
    def __init__(self):
        self.data: Dict[str, Pasien] = {}

    def get_by_id(self, id_pasien: str) -> Optional[Pasien]:
        pasien = self.data.get(id_pasien)
        if pasien:
            return pasien.model_copy()
        return None

    def update(self, pasien: Pasien) -> Pasien:
        self.data[pasien.id_pasien] = pasien
        return pasien.model_copy()
