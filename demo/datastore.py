import csv
import datetime
import sqlite3
from dataclasses import dataclass
from typing import Any, List, Optional

from utils import print_error, print_info


@dataclass
class Car:
    id: int
    brand: str
    year: int
    price: int
    color: str
    mileage: int
    fuel: str
    model: str
    is_available: bool


@dataclass
class Order:
    id: int
    car: Car
    customer_name: str
    customer_email: str
    date: str
    status: str
    is_available: bool


# Represents a temporary cache for car IDs that the Advisor agent uses to get the id of the car the user wishes to buy.
# A better approach could be to use a database, and pass the session id to the order agent instead of the car id in the prompt.
class CarIdCache:
    """
    Represents a temporary cache for car IDs that the Advisor agent uses to get the id of the car the user wishes to buy.
    # A better approach could be to use a database, and pass the session id to the order agent instead of the car id in the cache.
    """

    cache: dict = {}


class CarDB:
    """
    A class to manage the car database using SQLite.
    It provides methods to create, read, update, and delete car and order records.
    """

    def __init__(self, db_name: str = "data/cars.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row

    def init(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if len(tables) == 0:
            try:
                print_info("Database does not exist, creating...")
                self._create_tables()
                print_info("Importing cars...")
                self._import_cars("data/cars.csv")
                print_info("Database initialized successfully!")
            except Exception as e:
                print_error(f"Error initializing database: {e}")

    def _create_tables(self):
        """Creates the Cars and Orders tables if they don't exist."""

        print_info("Creating tables...")

        # Create Cars table
        create_cars_table_sql = """
        CREATE TABLE IF NOT EXISTS Cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            year INTEGER NOT NULL,
            price INTEGER NOT NULL,
            color TEXT,
            mileage INTEGER,
            fuel TEXT,
            model TEXT,
            is_available BOOLEAN NOT NULL
        );
        """
        self.conn.execute(create_cars_table_sql)

        create_orders_table_sql = """
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT,
            is_available BOOLEAN NOT NULL,
            FOREIGN KEY (car_id) REFERENCES Cars (id)
        );
        """
        self.conn.execute(create_orders_table_sql)
        self.conn.commit()

    def create_order(
        self, car_id: int, customer_name: str, customer_email: str
    ) -> Order:
        """
        Creates a new order in the Orders table.
        Updates the associated car's is_available field to False.
        Returns the newly created Order object.
        """

        car = self.get_car(car_id)
        if not car:
            raise ValueError(f"Car with id {car_id} not found.")

        date = datetime.date.today().isoformat()
        status = "order created"

        cursor = self.conn.execute(
            """
            INSERT INTO Orders (car_id, customer_name, customer_email, date, status, is_available)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (car_id, customer_name.lower(), customer_email.lower(), date, status, True),
        )

        self.conn.execute("UPDATE Cars SET is_available = 0 WHERE id = ?;", (car_id,))
        self.conn.commit()

        return Order(
            id=cursor.lastrowid,
            car=car,
            customer_name=customer_name,
            customer_email=customer_email,
            date=date,
            status=status,
            is_available=True,
        )

    def order_exists(self, order_id: int) -> bool:
        """
        Checks if an order exists in the Orders table by its ID.
        Returns True if the order exists, False otherwise.
        """
        cursor = self.conn.execute(
            "SELECT 1 FROM Orders WHERE id = ? AND is_deleted = 0;", (order_id,)
        )
        return cursor.fetchone() is not None

    def delete_order(self, order_id: int) -> None:
        """
        Deletes (marks as unavailable) an order from the Orders table by its ID.
        Updates the associated car's is_available field to True and sets the order's status to 'Deleted'.
        """
        cursor = self.conn.execute(
            "SELECT car_id FROM Orders WHERE id = ?;", (order_id,)
        )
        row = cursor.fetchone()
        if row:
            car_id = row["car_id"]
            self.conn.execute(
                "UPDATE Cars SET is_available = 1 WHERE id = ?;", (car_id,)
            )
            self.conn.execute(
                "UPDATE Orders SET is_available = 0, status = 'Deleted' WHERE id = ?;",
                (order_id,),
            )
            self.conn.commit()

    def get_orders_by_customer(self, customer_name: str) -> List[Order]:
        """
        Retrieves all orders made by a specific customer, including the associated Car object.
        """
        cursor = self.conn.execute(
            """
            SELECT o.*, c.id as car_id, c.brand, c.year, c.price, c.color, c.mileage, c.fuel, c.model, c.is_available
            FROM Orders o
            JOIN Cars c ON o.car_id = c.id
            WHERE o.customer_name = ? AND o.is_available = 1;
            """,
            (customer_name.lower(),),
        )
        rows = cursor.fetchall()
        return [
            Order(
                id=row["id"],
                car=Car(
                    id=row["car_id"],
                    brand=row["brand"],
                    year=row["year"],
                    price=row["price"],
                    color=row["color"],
                    mileage=row["mileage"],
                    fuel=row["fuel"],
                    model=row["model"],
                    is_available=row["is_available"],
                ),
                customer_name=row["customer_name"],
                customer_email=row["customer_email"],
                date=row["date"],
                status=row["status"],
                is_available=row["is_available"],
            )
            for row in rows
        ]

    def get_order(
        self, order_id: int, include_deleted: bool = False
    ) -> Optional[Order]:
        """
        Retrieves an order from the Orders table based on its ID, including the associated Car object.
        If `include_deleted` is True, retrieves orders regardless of their availability.
        """
        query = """
            SELECT o.*, c.id as car_id, c.brand, c.year, c.price, c.color, c.mileage, c.fuel, c.model, c.is_available
            FROM Orders o
            JOIN Cars c ON o.car_id = c.id
            WHERE o.id = ?
        """
        if not include_deleted:
            query += " AND o.is_available = 1"

        cursor = self.conn.execute(query, (order_id,))
        row = cursor.fetchone()
        if row:
            return Order(
                id=row["id"],
                car=Car(
                    id=row["car_id"],
                    brand=row["brand"],
                    year=row["year"],
                    price=row["price"],
                    color=row["color"],
                    mileage=row["mileage"],
                    fuel=row["fuel"],
                    model=row["model"],
                    is_available=row["is_available"],
                ),
                customer_name=row["customer_name"],
                customer_email=row["customer_email"],
                date=row["date"],
                status=row["status"],
                is_available=row["is_available"],
            )
        return None

    def _import_cars(self, csv_file: str):
        """
        Reads cars data from a CSV file and inserts them into the Cars table.
        Assumes the CSV has columns: id, brand, year, price, color, mileage, fuel, model.
        """
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cars = []
            for row in reader:
                car = (
                    int(row["id"]),
                    row["brand"],
                    int(row["year"]),
                    int(row["price"]),
                    row["color"],
                    int(row["mileage"]),
                    row["fuel"],
                    row["model"],
                    True,
                )
                cars.append(car)
            self.conn.executemany(
                "INSERT OR REPLACE INTO Cars (id,brand, year, price, color, mileage, fuel, model, is_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                cars,
            )
            self.conn.commit()

    def delete_car(self, car_id: int) -> None:
        """Deletes a car from the Cars table based on its id."""
        self.conn.execute("DELETE FROM Cars WHERE id = ?;", (car_id,))
        self.conn.commit()

    def get_car(self, car_id: int, include_unavailable: bool = False) -> Optional[Car]:
        """
        Retrieves a car from the Cars table based on its id.
        By default, only retrieves available cars unless `include_unavailable` is True.
        """
        query = "SELECT * FROM Cars WHERE id = ?"
        if not include_unavailable:
            query += " AND is_available = 1"
        cursor = self.conn.execute(query, (car_id,))
        row = cursor.fetchone()
        if row:
            return Car(
                id=row["id"],
                brand=row["brand"],
                year=row["year"],
                price=row["price"],
                color=row["color"],
                mileage=row["mileage"],
                fuel=row["fuel"],
                model=row["model"],
                is_available=row["is_available"],
            )
        return None

    def find_cars(
        self,
        brand: Optional[str] = None,
        year: Optional[int] = None,
        price: Optional[int] = None,
    ) -> List[Car]:
        """
        Finds all available cars that match the provided filters.
        Filters can be combined (e.g., brand and year).
        """
        query = "SELECT * FROM Cars WHERE is_available = 1"
        params: List[Any] = []

        if brand is not None:
            query += " AND brand = ?"
            params.append(brand)
        if year is not None:
            query += " AND year = ?"
            params.append(year)
        if price is not None:
            query += " AND price <= ?"
            params.append(price)

        cursor = self.conn.execute(query, params)
        rows = cursor.fetchall()
        return [
            Car(
                id=row["id"],
                brand=row["brand"],
                year=row["year"],
                price=row["price"],
                color=row["color"],
                mileage=row["mileage"],
                fuel=row["fuel"],
                model=row["model"],
                is_available=row["is_available"],
            )
            for row in rows
        ]

    def close(self):
        self.conn.close()
