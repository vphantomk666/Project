from database import Base, engine
from database_modal import ProductDB

Base.metadata.create_all(bind=engine)
print("✅ Tables created")
