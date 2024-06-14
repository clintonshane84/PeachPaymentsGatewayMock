# app/generator/payload_generator_factory.py

from typing import Type, Dict, Any
from .payload_generator_interface import PayloadGeneratorInterface
from .card_register_final_payload_generator import CardRegisterFinalPayloadGenerator
from .recurring_payment_final_payload_generator import RecurringPaymentFinalPayloadGenerator
from ..models import Transaction


class PayloadGeneratorFactory:

    @staticmethod
    def get_payload_generator(generator_type: str, transaction: Transaction,
                              params: Dict[str, Any] = None) -> PayloadGeneratorInterface:
        """
        Factory method to get the appropriate payload generator.

        Args:
            generator_type (str): The type of the generator to be created.
            transaction (Transaction): The transaction instance.
            params (Dict[str, Any]): Additional parameters for the generator.

        Returns:
            PayloadGeneratorInterface: An instance of a class that implements the PayloadGeneratorInterface.
        """
        if params is None:
            params = {}
        if generator_type == 'card_register':
            return CardRegisterFinalPayloadGenerator(transaction, params)
        elif generator_type == 'recurring_payment':
            return RecurringPaymentFinalPayloadGenerator(transaction, params)
        else:
            raise ValueError(f"Unknown generator type: {generator_type}")
