"""
Handler: Stock Decreased
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer


class StockIncreasedHandler(EventHandler):
    """Handles StockIncrease events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "StockIncreased"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        try:
            # 1. Restaurer le stock (compensation)
            self.logger.debug(f"Restoring stock")

            session = get_sqlalchemy_session()
            check_in_items_to_stock(session, event_data['order_items'])
            session.commit()

            # 2. Si l'operation a réussi, déclenchez OrderCancelled.
            event_data['event'] = "OrderCancelled"
        except Exception as e:
            # 3. Si l'opération a échoué, on termine quand même la compensation
            self.logger.error(f"StockIncrease compensation failed: {str(e)}")
            event_data['event'] = "OrderCancelled"
            event_data['error'] = str(e)
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)

        finally : 
            session.close()
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)





