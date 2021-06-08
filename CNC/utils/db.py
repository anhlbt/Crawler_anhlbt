import re
import json 
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)
        

class MyDatabase:
    # https://docs.sqlalchemy.org/en/13/core/engines.html
    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.upper()
        # DB_ENGINE = {"SQLITE":"sqlite:////media/anhlbt/DATA/nlp_2020/flask_fullstack/MadBlog/back-end/{DB}"}
        # engine = create_engine('postgresql+psycopg2://scott:tiger@localhost/mydatabase')
        DB_ENGINE = {"POSTGRESQL":"postgresql+pg8000://superset:superset@localhost/{DB}"}

        if dbtype in DB_ENGINE.keys():
            engine_url = DB_ENGINE[dbtype].format(DB=dbname)
            self.db_engine = db.create_engine(engine_url)
            print(self.db_engine) # we have 2 way to connect to db, self.db_engine.connect() or use Session
            Session = sessionmaker(bind=self.db_engine)
            self.session = Session()
        else:
            print("DBType is not found in DB_ENGINE")

    # Insert, Update, Delete
    def execute_query(self, query=''):
        if query == '' : return
        print (query)
        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
            except Exception as e:
                print(e)
                
    def add_post(self, post):
        try:
            self.session.add(post)
            
            self.session.commit()
        except Exception as ex:
            print(ex)    


class Post(Base): #dont create table, because we have existed already 
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    topic = db.Column(db.String(64))
    tags = db.Column(db.String(500))
    link_= db.Column(db.String(500))
    source = db.Column(db.String(500))
    audio_links = db.Column(db.PickleType)    
    summary = Column(Text)
    image = Column(db.PickleType, nullable=True)#anhlbt
    body = Column(Text)
    json_book = db.Column(JsonEncodedDict, nullable=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    views = Column(Integer, default=0)
    author_id = Column(Integer, default=1)
 
    def __repr__(self):
        return '<Post {}>'.format(self.title)
    
    
 


def load_json_from_file(json_path):
    with open(json_path, "r") as f:
        data = f.read()
        data = json.loads(data)
        if (len(data) > 0):
            return data
        else:
            return None