from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import get_engine_url


engine = create_engine(get_engine_url(), echo=True, future=True)
# a sessionmaker(), also in the same scope as the engine
Session = sessionmaker(engine)

# we can now construct a Session() without needing to pass the
# engine each time
# with Session() as session:
#     session.add(some_object)
#     session.add(some_other_object)
#     session.commit()
# closes the session
# with engine.connect() as conn:
#   result = conn.execute(text("select 'hello world'"))
#   print(result.all())
