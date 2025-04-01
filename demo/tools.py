import random
from typing import List

from autogen_core import SingleThreadedAgentRuntime, TopicId
from datastore import Car, CarDB, CarIdCache, Order
from messages import OrderUpdateMessage
from typing_extensions import Annotated
from utils import print_error, print_tool


class Tools:

    db: CarDB = CarDB()
    runtime: SingleThreadedAgentRuntime

    @staticmethod
    async def get_available_cars(
        brand: Annotated[
            str | None, "The brand of the car, or None to consider all brands"
        ],
        year: Annotated[int | None, "The year of the car or None to consider any year"],
        budget: Annotated[
            int | None,
            "The available budged for the car or None to consider any budget",
        ],
    ) -> List[Car]:
        """Use this tool you need to get the available cars"""

        print_tool("get_available_cars", f"{brand}-{year}-{budget}")
        return Tools.db.find_cars(brand=brand, year=year, price=budget)

    @staticmethod
    async def get_car(id: Annotated[int, "The id of the car"]):
        """Use this tool to get a car info by its id"""

        print_tool("get_car", f"{id}")
        return Tools.db.get_car(id)

    @staticmethod
    async def cache_carId(
        agent_id: Annotated[str, "The agent_id of the agent invoking the tool"],
        car_id: Annotated[int, "The id of the car the user is interested to"],
    ) -> None:
        """
        Use this tool every time the user identifies a car they are interested in.
        """
        print_tool("cache_carId", f"{agent_id}-{car_id}")
        CarIdCache.cache[agent_id] = car_id

    @staticmethod
    async def create_order(
        car_id: Annotated[int, "The id of the car the user wants to order"],
        customer_name: Annotated[str, "The name of the customer"],
        customer_email: Annotated[str, "The email of the customer"],
    ) -> Annotated[
        Order | None,
        "The order info to communicate to the user, or None if the order could not be created",
    ]:
        """Use this tool to create a new order for a car"""

        print_tool("create_order", f"{car_id}-{customer_name}-{customer_email}")
        try:
            return Tools.db.create_order(car_id, customer_name, customer_email)
        except Exception as e:
            print_error(f"Error creating order: {e}")
            return None

    @staticmethod
    async def delete_order(
        order_id: Annotated[int, "The id of the order to delete"],
    ) -> Annotated[
        bool | str,
        "True if the order was deleted successfully, or a message if the order could not be deleted",
    ]:
        """Use this tool to delete an order"""

        print_tool("delete_order", f"{order_id}")
        try:
            order = Tools.db.get_order(order_id)
            if order is None:
                print_error(f"Order {order} not found")
                return "Order not found!"
            Tools.db.delete_order(order_id)
            return True
        except Exception as e:
            print_error(f"Error deleting order: {e}")
            return "An error occurred while deleting the order."

    @staticmethod
    async def get_order(
        order_id: Annotated[int, "The id of the order to retrieve"],
    ) -> Annotated[
        Order | str,
        "The found order, or a message if the order was not found",
    ]:
        """Use this tool to find an order by its id"""

        print_tool("get_order", f"{order_id}")

        try:
            order = Tools.db.get_order(order_id)
            if order is None:
                message = f"Order {order} not found"
                print_error(message)
                return message
            return order
        except Exception as e:
            print_error(f"Error getting order: {e}")
            return "An error occurred while retrieving the order"

    @staticmethod
    async def lookup_order(
        order_id: Annotated[int, "The id of the order to retrieve"],
    ) -> Annotated[
        Order | str,
        "The found order, or a message if the order was not found",
    ]:
        """Use this tool to find an order by its id"""

        print_tool("lookup_order", f"{order_id}")
        try:
            order = Tools.db.get_order(order_id, include_deleted=True)
            if order is None:
                message = f"Order {order} not found"
                print_error(message)
                return message
            return order
        except Exception as e:
            print_error(f"Error getting order: {e}")
            return "An error occurred while retrieving the order"

    @staticmethod
    async def get_orders(
        customer_name: Annotated[
            str, "The name of the customer to retrieve orders for"
        ],
    ) -> Annotated[
        List[Order] | str,
        "The list of orders for the customer, or a message if no orders were found",
    ]:
        """Use this tool to find an the orders of a customer by their name"""

        print_tool("get_orders", f"{customer_name}")

        try:
            orders = Tools.db.get_orders_by_customer(customer_name)
            if len(orders) == 0:
                return f"No orders found for {customer_name}!"
            return orders
        except Exception as e:
            print_error(f"Error getting customer orders: {e}")
            return "An error occurred while retrieving customer's orders"

    @staticmethod
    async def inform_after_sales_department(
        order_id: Annotated[
            str,
            "The id of the order to notify about",
        ],
        status: Annotated[
            str,
            "The status of the order to notify about",
        ],
    ) -> Annotated[
        int | None,
        "The notification id, or None if the notification could not be created",
    ]:
        """Use this tool to notifiy the after sales department about an order status change"""

        print_tool("create_status_notification", f"{order_id}-{status}")

        await Tools.runtime.publish_message(
            OrderUpdateMessage(order_id=order_id),
            topic_id=TopicId(
                type="order_update", source="default"
            ),  # the after_sales is not tied to any specific session, it just listen to this topic
        )
        return random.randint(1, 1000)  # Simulate a notification id
