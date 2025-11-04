"""
Handler: create payment transaction
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import requests
import config
from logger import Logger
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class CreatePaymentHandler(Handler):
    """ Handle the creation of a payment transaction for a given order. Trigger rollback of previous steps in case of failure. """

    def __init__(self, order_id, order_data):
        """ Constructor method """
        self.order_id = order_id
        self.order_data = order_data
        self.total_amount = 0
        super().__init__()

    def run(self):
        """Call payment microservice to generate payment transaction"""
        try:
            # TODO: effectuer une requête à /orders pour obtenir le total_amount de la commande (que sera utilisé pour démander la transaction de paiement)
            """
            GET my-api-gateway-address/order/{id} ...
            """

            # TODO: effectuer une requête à /payments pour créer une transaction de paiement
            """
            POST my-api-gateway-address/payments ...
            json={ voir collection Postman pour en savoir plus ... }
            """
            response = requests.get(
                f"{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}",
                headers={"Content-Type": "application/json"}
            )

            if response.ok:
                order_data = response.json()
                self.total_amount = order_data.get("total_amount", 0)
                self.logger.debug("La création d'une transaction de paiement a réussi")
                #return OrderSagaState.COMPLETED
            else:
                text = response.json() 
                self.logger.error(f"Erreur {response.status_code} : {text}")
                return OrderSagaState.INCREASING_STOCK
            
            payment_payload = {
                "order_id": self.order_id,
                "amount": self.total_amount,
                "user_id": self.user_id
            }
            response_payment = requests.post(
                f"{config.API_GATEWAY_URL}/payment-api/payments",
                json=payment_payload,
                headers={"Content-Type": "application/json"}
            )
            if response_payment.ok:
                order_data = response_payment.json()
                self.logger.debug("La création d'une transaction de paiement a réussi")
                return OrderSagaState.COMPLETED
            else:
                text = response_payment.json()
                self.logger.error(f"Erreur {response_payment.status_code} : {text}")
                return OrderSagaState.INCREASING_STOCK
            
        except Exception as e:
            self.logger.error("La création d'une transaction de paiement a échoué : " + str(e))
            return OrderSagaState.INCREASING_STOCK
        
    def rollback(self):
        """Call payment microservice to delete payment transaction"""
        # ATTENTION: Nous pourrions utiliser cette méthode si nous avions des étapes supplémentaires, mais ce n'est pas le cas actuellement, elle restera donc INUTILISÉE.
        self.logger.debug("La suppression d'une transaction de paiement a réussi")
        return OrderSagaState.INCREASING_STOCK