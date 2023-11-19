from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from datetime import datetime, timedelta
from typing import List


class Base(DeclarativeBase):
    pass


class Subscription(Base):
    __tablename__ = "subscription"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(nullable=False)

    # Define a relationship to the User model
    user: Mapped["User"] = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.user_id} - {self.start_date} to {self.end_date}>"


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    number: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=True)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    subscription: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="user")
    email_var: Mapped[int] = mapped_column(default=0)
    telegram_id: Mapped[int] = mapped_column(default=0)
    logged: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"<User {self.email}>"


class Stadium(Base):
    __tablename__ = "stadium"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    image_url = Column(String(255))
    price = Column(Float, default=0.0)
    opening_time = Column(String, default="08:00:00")
    closing_time = Column(String, default="00:00:00")
    is_active = Column(Boolean, default=False)
    region = Column(String)
    district = Column(String)
    location = Column(String)
    number_of_orders = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship(User, backref="stadiums")

    def __repr__(self):
        return f"<Stadium {self.name}>"


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    status = Column(String)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    stadium_id = Column(Integer, ForeignKey(Stadium.id), nullable=False)
    user = relationship(User, backref="orders")
    stadium = relationship(Stadium, backref="orders")
    start_time = Column(DateTime)
    hour = Column(Integer)

    def __repr__(self):
        return f"<Order order{self.id}>"


class Config(Base):
    __tablename__ = "config"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str] = mapped_column(unique=True)
