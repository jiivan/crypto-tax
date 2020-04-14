import sqlalchemy
import sqlalchemy.orm

engine = sqlalchemy.create_engine('sqlite:///tax.db')
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()

if __name__ == '__main__':
    from crypto_tax import models
    models.Base.metadata.create_all(engine)
