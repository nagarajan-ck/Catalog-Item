'''
this file sets up the database declaring the tables and columns in it.
It creates a database file catalogitem.db
'''

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# All classes derive the base class
Base = declarative_base()

# User class has the info about the users


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    email = Column(String(50))


# Category class contains the categories
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))


# Item class has all the items, has ForeignKey from category and user
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    title = Column(String(30), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category id": self.category_id,
            "user_id": self.user_id
        }


# creates the DB file
engine = create_engine('sqlite:///catalogitem.db')


Base.metadata.create_all(engine)
