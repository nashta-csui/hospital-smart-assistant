from abc import ABC, abstractmethod
from typing import Optional
from app.domain.pasien import Pasien

class IPasienRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_pasien: str) -> Optional[Pasien]:
        pass

    @abstractmethod
    def update(self, pasien: Pasien) -> Pasien:
        pass