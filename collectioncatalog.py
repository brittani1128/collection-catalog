from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbsetup import Base, Collection, CollectionItem, User

engine = create_engine('sqlite:///collectioncatalogwithusers.db')
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

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Items for Yoga Collection
yoga = Collection(user_id=1, name="Yoga")

session.add(yoga)
session.commit()

collectionItem1 = CollectionItem(user_id=1, name="Long Sleeve", description="Supersoft. Lightweight. Breathable.",
                     price="$39", category="clothing", collection=yoga)

session.add(collectionItem1)
session.commit()


collectionItem2 = CollectionItem(user_id=1, name="Flow Tank", description="Lightweight. Airy. Supersoft.",
                     price="$29", category="clothing", collection=yoga)

session.add(collectionItem2)
session.commit()

collectionItem3 = CollectionItem(user_id=1, name="High Rise Tight", description="Moisture wicking. Sculpting. 4 way stretch. ",
                     price="$59", category="clothing", collection=yoga)

session.add(collectionItem3)
session.commit()

collectionItem4 = CollectionItem(user_id=1, name="Beanie", description="Black, White, Grey",
                     price="$14", category="accessories", collection=yoga)

session.add(collectionItem4)
session.commit()

collectionItem5 = CollectionItem(user_id=1, name="Leg Warmers", description="Black, Grey",
                     price="$19", category="accessories", collection=yoga)

session.add(collectionItem5)
session.commit()

collectionItem6 = CollectionItem(user_id=1, name="Yoga Mat", description="Black",
                     price="$49", category="accessories", collection=yoga)

session.add(collectionItem6)
session.commit()



# Items for Run Category

run = Collection(user_id=1, name="Run")

session.add(run)
session.commit()

collectionItem1 = CollectionItem(user_id=1, name="Run Long Sleeve", description="Moisture wicking. Slim fit. 4 way stretch.",
                     price="$49", category="clothing", collection=run)

session.add(collectionItem1)
session.commit()

collectionItem2 = CollectionItem(user_id=1, name="Run Tank", description="Moisture wicking. Slim fit. Breathable.",
                     price="$29", category="clothing", collection=run)

session.add(collectionItem2)
session.commit()

collectionItem3 = CollectionItem(user_id=1, name="Reflective Tight", description="Moisture wicking. Breathable. Sculpting.",
                     price="$59", category="clothing", collection=run)

session.add(collectionItem3)
session.commit()

collectionItem4 = CollectionItem(user_id=1, name="Headband", description="Black, Beige",
                     price="$9", category="accessories", collection=run)

session.add(collectionItem4)
session.commit()

collectionItem5 = CollectionItem(user_id=1, name="Infinity Scarf", description="Black, Grey",
                     price="$19", category="accessories", collection=run)

session.add(collectionItem5)
session.commit()

collectionItem6 = CollectionItem(user_id=1, name="Trainers", description="Black and grey",
                     price="$99", category="accessories", collection=run)

session.add(collectionItem6)
session.commit()



# Items for Train Category
train = Collection(user_id=1, name="Train")

session.add(train)
session.commit()

collectionItem1 = CollectionItem(user_id=1, name="Crop Tank", description="Lightweight. Breathable. Moisture wicking.",
                     price="$29", category="clothing", collection=train)

session.add(collectionItem1)
session.commit()


collectionItem2 = CollectionItem(user_id=1, name="Crop Hoodie", description="Supersoft. Moisture wicking. Cozy.",
                     price="$49", category="clothing", collection=train)

session.add(collectionItem2)
session.commit()

collectionItem3 = CollectionItem(user_id=1, name="Train Crop", description="Moisture wicking. Breathable. Sculpting.",
                     price="$59", category="clothing", collection=train)

session.add(collectionItem3)
session.commit()

collectionItem4 = CollectionItem(user_id=1, name="Headband", description="Black, Beige",
                     price="$9", category="accessories", collection=train)

session.add(collectionItem4)
session.commit()

collectionItem5 = CollectionItem(user_id=1, name="Gym Bag", description="Black",
                     price="$29", category="accessories", collection=train)

session.add(collectionItem5)
session.commit()

collectionItem6 = CollectionItem(user_id=1, name="Trainers", description="Black and grey",
                     price="$99", category="accessories", collection=train)

session.add(collectionItem6)
session.commit()


print "added collection items!"
