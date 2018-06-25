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


item = Item(id = 1, title='Gloves', description='Goalkeeper uses this', category_id=1)
session.add(item)
session.commit()

item = Item(id = 2, title='Ball', description='Baseball ball', category_id=2)
session.add(item)
session.commit()

item = Item(id = 3, title='Hoops', description='Ball goes in here', category_id=3)
session.add(item)
session.commit()

item = Item(id = 4, title='Goggles', description='Underwater vision', category_id=4)
session.add(item)
session.commit()

item = Item(id = 5, title='Boots', description='Shooting accuracy', category_id=1)
session.add(item)
session.commit()

item = Item(id = 6, title='Cap', description='For the striker', category_id=2)
session.add(item)
session.commit()

item = Item(id = 7, title='Jersey', description='Mens basketball team', category_id=3)
session.add(item)
session.commit()

item = Item(id = 8, title='Swimming Suit', description='Light on the body', category_id=4)
session.add(item)
session.commit()


print ("added menu items!")
