# app/generator/payload_generator_interface.py

from abc import ABC, abstractmethod
from typing import Dict


class PayloadGeneratorInterface(ABC):

    @abstractmethod
    def generate_payload(self) -> Dict:
        """
        Generate the payload.

        Returns:
            Dict: The generated payload.
        """
        pass
