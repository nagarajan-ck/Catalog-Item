from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Item, Base, Category

engine = create_engine('sqlite:///catalogitem.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



item = Category(id = 1, name='Football')
session.add(item)
session.commit()
item = Category(id = 2, name='Baseball')
session.add(item)
session.commit()
item = Category(id = 3, name='Basketball')
session.add(item)
session.commit()
item = Category(id = 4, name='Swimming')
session.add(item)
session.commit()


print ("added menu items!")
