import enum

from dotenv import load_dotenv
import os
from typing import List
from sqlalchemy import create_engine, URL, String, LargeBinary, Integer, MetaData, TIMESTAMP, ForeignKey, Enum, Numeric, \
    Date, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, annotations, validates, relationship
load_dotenv()

connection_string = URL.create(
"mysql+mysqldb",
    port = os.getenv("DB_PORT"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST"),
    username = os.getenv("DB_USERNAME"),
    database = os.getenv("DB_NAME")
)

engine = create_engine(connection_string, echo=True)
metadata_obj = MetaData()

class Base(DeclarativeBase):
    metadata = metadata_obj
    annotations = {}

PROFILE_IMAGE_SIZE = 2*1024*1024

class StatusComponent(enum.Enum):
    PENDING = "Pending"
    PREPARED = "Prepared"
    SERVED = "Served"
    PAID = "Paid"

class RolesComponent(enum.Enum):
    MANGER="Manager"
    CHEF="Chef"
    WAITER="Waiter"
    CASHIER="Cashier"

class CategoryComponent(enum.Enum):
    STARTER="Starter"
    MAIN_COURSE="Main course"
    DESERT="Desert"
    DRINK="Drink"

class AvailableComponent(enum.Enum):
    AVAILABLE="Available"
    RESERVED="Reserved"
    OCCUPIED="Occupied"

class ReserveComponent(enum.Enum):
    PENDING="Pending"
    CONFIRMED="Confirmed"
    CANCELLED="Cancelled"

class PaymentStatus(enum.Enum):
    PENDING="Pending"
    CONFIRMED="Confirmed"
    FAILED="Failed"

class PaymentComponent(enum.Enum):
    POS="POS"
    CARD="CARD"
    TRANSFER="Bank Transfer"



class Customer(Base):
    __tablename__ = "customer"
    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    contact: Mapped[str] = mapped_column(String(12), nullable=False)
    email: Mapped[str] = mapped_column(String(25), unique=True)
    address: Mapped[str] = mapped_column(String(45))
    profile_image: Mapped[bytes] = mapped_column(LargeBinary(length=PROFILE_IMAGE_SIZE), nullable=False)

    order: Mapped[List["Order"]] = relationship(back_populates="customer")
    reservation: Mapped['Reservation'] = relationship(back_populates="customer", cascade="all, delete-orphan")

class Staff(Base):
    __tablename__ = "staff"

    staff_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    role: Mapped["RolesComponent"] = mapped_column(Enum(RolesComponent))
    contact: Mapped[str] = mapped_column(String(45), nullable=False)
    salary: Mapped[int] = mapped_column(Numeric(10, 2))

    order: Mapped[List["Order"]] = relationship(back_populates="staff")

class Menu(Base):
    __tablename__ = "menu"

    item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(45))
    description: Mapped[str] = mapped_column(String(1200))
    price: Mapped[Numeric] = mapped_column(Numeric(12, 2))
    category: Mapped[CategoryComponent] = mapped_column(Enum(CategoryComponent))
    image: Mapped[LargeBinary] = mapped_column(LargeBinary(length=PROFILE_IMAGE_SIZE))

    order_item: Mapped['OrderItem'] = relationship(back_populates="menu")
class Table(Base):
    __tablename__ = "table"

    table_id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AvailableComponent] = mapped_column(Enum(AvailableComponent))

    order: Mapped['Order'] = relationship(back_populates="table")
    reservation: Mapped['Reservation'] = relationship(back_populates="table")

class Reservation(Base):
    __tablename__ = "reservation"

    reservation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.customer_id"))
    table_id: Mapped[int] = mapped_column(ForeignKey("table.table_id"))
    date_time: Mapped[Date] = mapped_column(TIMESTAMP)
    status: Mapped[ReserveComponent] = mapped_column(Enum(ReserveComponent))

    customer: Mapped['Customer'] = relationship(back_populates="reservation")
    table: Mapped['Table'] = relationship(back_populates="reservation")
class Order(Base):
    __tablename__ = "order"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer.customer_id"))
    table_id: Mapped[int] = mapped_column(Integer, ForeignKey("table.table_id"))
    staff_id: Mapped[int] = mapped_column(Integer, ForeignKey("staff.staff_id"))
    status: Mapped[StatusComponent] = mapped_column(Enum(StatusComponent))
    orderdate: Mapped[Date] = mapped_column(Date)

    customer: Mapped["Customer"] = relationship(back_populates="order")
    staff: Mapped["Staff"] = relationship(back_populates="order")
    table: Mapped["Table"] = relationship(back_populates="order")
    order_item: Mapped['OrderItem'] = relationship(back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_item"

    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.order_id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("menu.item_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer)
    subtotal: Mapped[Numeric] = mapped_column(Numeric(12, 2))

    order: Mapped["Order"] = relationship(back_populates="order_item")
    menu: Mapped['Menu'] = relationship(back_populates="order_item")

class Payment(Base):
    __tablename__ = "payment"

    payment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.order_id"), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[PaymentComponent] = mapped_column(Enum(PaymentComponent))
    date: Mapped[Date] = mapped_column(Date)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus))


def create_all():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_all()
    print("Schema created.")