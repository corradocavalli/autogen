from typing import List

from autogen_core import SingleThreadedAgentRuntime, TopicId
from datastore import Car, CarDB, CarIdCache, Order
from messages import OrderUpdateMessage
from rich import print
from typing_extensions import Annotated


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

        print(
            f"[bold blue italic]'get_available_cars' invoked with: {brand}-{year}-{budget}[/bold blue italic]"
        )

        return Tools.db.find_cars(brand=brand, year=year, price=budget)

    @staticmethod
    async def get_car(id: Annotated[int, "The id of the car"]):
        """Use this tool to get a car info by its id"""

        print(f"[bold blue italic]'get_car' invoked with: {id}[/bold blue italic]")

        return Tools.db.get_car(id)

    @staticmethod
    async def cache_carId(
        agent_id: Annotated[str, "The agent_id of the agent invoking the tool"],
        car_id: Annotated[int, "The id of the car the user is interested to"],
    ) -> None:
        """
        Use this tool every time the user identifies a car they are interested in.
        """
        print(
            f"[bold blue italic]Tool cache_carId invoked: {agent_id}-{car_id}[/bold blue italic]"
        )
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

        print(
            f"[bold blue italic]'create_order' invoked with: {car_id}-{customer_name}-{customer_email}[/bold blue italic]"
        )

        try:
            order = Tools.db.create_order(car_id, customer_name, customer_email)
            print("[bold blue italic]Order created successfully![/bold blue italic]")
            return order
        except Exception as e:
            print(f"[bold red]Error creating order: {e}[/bold red]")
            return None

    @staticmethod
    async def delete_order(
        order_id: Annotated[int, "The id of the order to delete"],
    ) -> Annotated[
        bool | str,
        "True if the order was deleted successfully, or a message if the order could not be deleted",
    ]:
        """Use this tool to delete an order"""

        print(
            f"[bold blue italic]'delete_order' invoked with: {order_id}[/bold blue italic]"
        )

        try:
            order = Tools.db.get_order(order_id)
            if order is None:
                print(f"[bold red]Order {order} not found[/bold red]")
                return "Order not found!"
            Tools.db.delete_order(order_id)
            return True
        except Exception as e:
            print(f"[bold red]Error deleting order: {e}[/bold red]")
            return "An error occurred while deleting the order."

    @staticmethod
    async def get_order(
        order_id: Annotated[int, "The id of the order to retrieve"],
    ) -> Annotated[
        Order | str,
        "The found order, or a message if the order was not found",
    ]:
        """Use this tool to find an order by its id"""

        print(
            f"[bold blue italic]'get_order' invoked with: {order_id}[/bold blue italic]"
        )

        try:
            order = Tools.db.get_order(order_id)
            if order is None:
                print(f"[bold red]Order {order} not found[/bold red]")
                return "Order not found!"
            return order
        except Exception as e:
            print(f"[bold red]Error getting order: {e}[/bold red]")
            return f"An error occurred while getting the order: {order_id}"

    @staticmethod
    async def lookup_order(
        order_id: Annotated[int, "The id of the order to retrieve"],
    ) -> Annotated[
        Order | str,
        "The found order, or a message if the order was not found",
    ]:
        """Use this tool to find an order by its id"""

        print(
            f"[bold blue italic]'find_order' invoked with: {order_id}[/bold blue italic]"
        )

        try:
            order = Tools.db.get_order(order_id, include_deleted=True)
            if order is None:
                print(f"[bold red]Order {order} not found[/bold red]")
                return "Order not found!"
            return order
        except Exception as e:
            print(f"[bold red]Error getting order: {e}[/bold red]")
            return f"An error occurred while getting the order: {order_id}"

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

        print(
            f"[bold blue italic]'get_orders' invoked with: {customer_name}[/bold blue italic]"
        )

        try:
            orders = Tools.db.get_orders_by_customer(customer_name)
            if len(orders) == 0:
                return f"No orders found for {customer_name}!"
            return orders
        except Exception as e:
            print(f"[bold red]Error getting customer orders: {e}[/bold red]")
            return f"An error occurred while getting the orders for customer {customer_name}"

    @staticmethod
    async def inform_user_about_order_status(
        order_id: Annotated[
            str,
            "The id of the order to notify about",
        ],
        status: Annotated[
            str,
            "The status of the order to notify about",
        ],
    ) -> Annotated[
        bool, "True when notification was sent successfully, false otherwise"
    ]:
        """Use this tool to inform the user about an order update"""

        print(
            f"[bold blue italic]'notify_order_update' invoked with: {order_id}-{status}[/bold blue italic]"
        )

        await Tools.runtime.publish_message(
            OrderUpdateMessage(
                order_id=order_id,
                status=status,
            ),
            topic_id=TopicId(
                type="order_update", source="default"
            ),  # the communication agent is not tied to any specific session
        )
        return True
