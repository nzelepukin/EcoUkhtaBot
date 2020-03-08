import telebot,time,redis,os
from sqlalchemy import Table, Column,DateTime, Integer, String, Float,LargeBinary, MetaData, ForeignKey, engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship


                    # DB REDIS part STRATS
url=os.environ['REDIS_URL']
db_red=redis.Redis.from_url(url)
                    # DB POSTGRES part STRATS
db_url=os.environ['DATABASE_URL']
engine=create_engine(db_url+'?charset=utf8')
Base = declarative_base()
metadata = MetaData()

class Userinfo(Base):
    __tablename__='userinfo'
    id = Column(Integer, primary_key=True)
    username = Column( String(20))
    user_fio = Column( String(100))
    messanger = Column( String(20))
    role =Column( String(20))
    logs = relationship("UserLog", back_populates="user",cascade="all, delete, delete-orphan")

class UserLog(Base):
    __tablename__='userlog'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    date=Column(DateTime)
    place_id = Column(Integer, ForeignKey("place.id"))
    user = relationship("Userinfo", back_populates="logs")

class Place(Base):
    __tablename__='place'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    util_type=Column( String(20))
    loc_lat = Column(Float)
    loc_lon = Column(Float)
    info = Column( String(100))
    photo = Column(LargeBinary)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def insert_log(user_id:int, place_id:int)->None:
    ''' Save log'''
    session=Session()
    db_log =UserLog ( user_id=user_id, date= time.ctime(), place_id=place_id)
    session.add(db_log)
    session.commit()   
    session.close()

def insert_user(message)->None:
    ''' Save USER in Postgres DB '''
    session=Session()
    user=str(message.from_user.id)
    user_list=[i[0] for i in session.query(Userinfo.username)]
    if not user in user_list:
        db_user= Userinfo(  username=user, 
                            user_fio = '{} {}'.format(message.from_user.first_name, message.from_user.last_name),
                            messanger = 'telegram',
                            role = 'user')
        session.add(db_user)
    else: 
        print ('User already in base')
    session.commit()   
    session.close()

def insert_place(message)->None:
    # Save PLACEINFO in Postgres DB
    session=Session()
    user=str(message.from_user.id)
    with open('temp.jpg', 'rb') as tmp_file:
        photo=tmp_file.read()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    db_place = Place (  user_id = db_user.id, 
                        util_type = str(db_red.get(user+'_type')),
                        loc_lat = float(db_red.get(user+'_lat')),
                        loc_lon = float(db_red.get(user+'_lon')),
                        info = str(db_red.get(user+'_info')),
                        photo = photo )
    session.add(db_place)
    session.commit()
    session.close()

def select_places(util_type='batery'):
    session=Session()
    db_places= session.query(Place).all()
    print(db_places)
    places_dict=[{'id':p.id,'loc_lon':p.loc_lon,'loc_lat':p.loc_lat} for p in db_places]
    session.close()
    return places_dict

def select_place_param(place_id:int):
    session=Session()
    result=dict()
    db_place = session.query(Place).filter(Place.id==place_id).one()
    result['id']=db_place.id
    result['info']=db_place.info
    result['loc_lon']=db_place.loc_lon
    result['loc_lat']=db_place.loc_lat
    result['photo']=db_place.photo
    session.close()
    return result

def select_userid_by_name(user:str):
    session=Session()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    result= db_user.id
    session.close()
    return result

def delete_user(user):
    ''' Delete USER from Postgres and all his locations '''
    session=Session()
    user_list=[i[0] for i in session.query(Userinfo.username)]
    if user in user_list:
        myuser = session.query(Userinfo).filter(Userinfo.username==user).one()
        session.delete(myuser)
        session.commit()
    else: print ('Cant find {} in base'.format(user))
    session.close()

def red_set(key:str,value:str):
    db_red.set(key,value)

def red_get(key:str):
    print(db_red.get(key))
    return db_red.get(key)
