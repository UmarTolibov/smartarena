import json

from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, reconstructor
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta
from typing import List


class Base(DeclarativeBase):
    pass


class Subscription(Base):
    __tablename__ = "subscription"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(nullable=False)

    # Define a relationship to the User model
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.user_id} - {self.start_date} to {self.end_date}>"


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(nullable=True)
    number: Mapped[str] = mapped_column(unique=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    lang: Mapped[str] = mapped_column(default="eng")
    email_var: Mapped[int] = mapped_column(default=0)

    sessions: Mapped[List["UserSessions"]] = relationship(back_populates="user", overlaps="session")
    subscription: Mapped[List["Subscription"]] = relationship(back_populates="user")
    stadiums: Mapped[List["Stadium"]] = relationship(back_populates="user")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class UserSessions(Base):
    __tablename__ = "user_session"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column()
    logged: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=True)
    user: Mapped["User"] = relationship(User, back_populates="sessions")


class Stadium(Base):
    __tablename__ = "stadium"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    image_url: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(default=0.0)
    opening_time: Mapped[str] = mapped_column(default="08:00:00")
    closing_time: Mapped[str] = mapped_column(default="00:00:00")
    is_active: Mapped[bool] = mapped_column(default=False)
    region: Mapped[str] = mapped_column()
    district: Mapped[str] = mapped_column()
    location: Mapped[dict] = mapped_column(JSON, default={"longitude": 0, "latitude": 0})
    number_of_orders: Mapped[int] = mapped_column(default=0)
    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped["User"] = relationship(back_populates="stadiums")
    orders: Mapped["Order"] = relationship(back_populates="stadium")
    # etc..
    available_slots: Mapped[str] = mapped_column(default="[]")

    @reconstructor
    def init_on_load(self):
        self.calculate_available_slots()

    def calculate_available_slots(self):
        busy_slots = self.calculate_busy_slots()
        total_slots = self.calculate_total_slots()

        # Convert datetime objects to string format
        busy_slots_str = [(str(slot[0]), str(slot[1])) for slot in busy_slots]
        total_slots_str = [(str(slot[0]), str(slot[1])) for slot in total_slots]

        # Calculate available slots by subtracting busy slots from total slots
        self.available_slots = json.dumps(list(set(total_slots_str) - set(busy_slots_str)))

    def calculate_busy_slots(self):
        busy_slots = [(order.start_time, order.start_time + timedelta(hours=order.hour)) for order in self.orders]
        return busy_slots

    def calculate_total_slots(self):
        opening_time = datetime.strptime(self.opening_time, "%H:%M:%S")
        closing_time = datetime.strptime(self.closing_time, "%H:%M:%S")
        total_slots = [(opening_time + timedelta(hours=i), opening_time + timedelta(hours=i + 1)) for i in
                       range(int((closing_time - opening_time).seconds / 3600))]
        return total_slots

    def __repr__(self):
        return f"<Stadium {self.name}>"


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[int] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    hour: Mapped[int] = mapped_column(default=1)

    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped["User"] = relationship(User, back_populates="orders")

    stadium_id: Mapped[int] = mapped_column(ForeignKey(Stadium.id), nullable=False)
    stadium: Mapped["Stadium"] = relationship(Stadium, back_populates="orders")

    @property
    def end_time(self):
        if self.start_time and self.hour is not None:
            return self.start_time + timedelta(hours=self.hour)
        return None

    def __repr__(self):
        return f"<Order order{self.id}>"


class Config(Base):
    __tablename__ = "config"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str] = mapped_column(unique=True)


class Table(Base):
    __tablename__ = "table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    subject: Mapped[str] = mapped_column()
    message: Mapped[str] = mapped_column()
