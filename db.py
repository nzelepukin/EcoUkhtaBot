import telebot,time,redis,os,datetime
from sqlalchemy import Table, Column,DateTime, Integer, String, Float,LargeBinary, MetaData, ForeignKey, engine, create_engine,Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.sql import func

                    # DB REDIS part STRATS
url=os.environ['REDIS_URL']
db_red=redis.Redis.from_url(url)


def red_set(key:str,value:str)->None:
    ''' REDIS write parameter '''
    db_red.set(key,value)

def red_get(key:str)->str:
    ''' REDIS read parameter '''
    print(db_red.get(key))
    return db_red.get(key)
                    # DB REDIS part ENDS

                    # DB POSTGRES part STRATS
db_url=os.environ['DATABASE_URL']
print(db_url)
engine=create_engine(db_url,encoding='UTF8')
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
    date=Column(DateTime(timezone=True), onupdate=func.now())
    place_id = Column(Integer, ForeignKey("place.id"))
    user = relationship("Userinfo", back_populates="logs")

class Place(Base):
    __tablename__='place'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    util_type=Column( String(20))
    loc_lat = Column(Float)
    loc_lon = Column(Float)
    info = Column( String)
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

def select_log()->dict:
    ''' Select log information '''
    session=Session()
    db_log = session.query(UserLog).all()
    log_dict=[{'user_id':l.user_id,'date':l.date,'place_id':l.place_id} for l in db_log]
    session.close()
    return log_dict

def select_log_stats()->dict:
    ''' Select statistic log information '''
    session=Session()
    current_time = datetime.datetime.utcnow()
    periods= {
        'month' : current_time - datetime.timedelta(weeks=4),
        'quarter' : current_time - datetime.timedelta(weeks=12),
        'year' : current_time - datetime.timedelta(days=365)}
    results = { period:len(session.query(UserLog).filter(UserLog.date<periods[period]).all()) for period in periods }
    session.close()
    return results

def insert_place(message)->None:
    ''' Save PLACE info in Postgres DB '''
    session=Session()
    user=str(message.from_user.id)
    with open('temp.jpg', 'rb') as f:
        photo=f.read()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    db_place = Place (  user_id = db_user.id, 
                        util_type = db_red.get(user+'_type').decode('utf-8'),
                        loc_lat = float(db_red.get(user+'_lat')),
                        loc_lon = float(db_red.get(user+'_lon')),
                        info = db_red.get(user+'_info').decode('utf-8'),
                        photo = photo )
    session.add(db_place)
    session.commit()
    session.close()

def select_places(util_type='batery')->dict:
    ''' Select PLACE info from Postgres DB '''
    session=Session()
    db_places= session.query(Place).all()
    places_dict=[{'id':p.id,'loc_lon':p.loc_lon,'loc_lat':p.loc_lat} for p in db_places]
    session.close()
    return places_dict

def delete_place(place:int)->None:
    ''' Delete Place from Postgres and all his locations '''
    session=Session()
    db_place = session.query(Place).filter(Place.place_id==place).one()
    session.delete(db_place)
    session.commit()
    session.close()

def select_place_param(place_id:int)->dict:
    ''' Get all parameters of PLACES from Postgres DB '''
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


def insert_user(user:str,first_name:str,last_name:str,messanger:str)->None:
    ''' Save USER in Postgres DB '''
    session=Session()
    user_list=[i[0] for i in session.query(Userinfo.username)]
    if not str(user) in user_list:
        db_user= Userinfo(  username=user, 
                            user_fio = '{} {}'.format(first_name, last_name),
                            messanger = messanger,
                            role = 'user')
        session.add(db_user)
    else: 
        print ('User already in base')
    session.commit()   
    session.close()

def delete_user(user:int)->None:
    ''' Delete User from Postgres and all his locations '''
    session=Session()
    db_user = session.query(Userinfo).filter(Userinfo.id==user).one()
    session.delete(db_user)
    session.commit()
    session.close()

def set_role(user:str,new_role:str)->None:
    ''' Set ROLE to USER '''
    session=Session()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    db_user.role = new_role
    session.commit()
    session.close()

def isAdmin(user:str)->bool:
    ''' Checks ROLE and return True if ADMIN'''
    session=Session()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    result= db_user.role
    session.close()
    if result == 'admin': return True
    else: return False

def select_users()->dict:
    ''' Select USERS from Postgres DB '''
    session=Session()
    db_users= session.query(Userinfo).all()
    users_dict=[{'id':p.id,'username':p.username,'fio':p.user_fio,'role':p.role, 'messanger':p.messanger} for p in db_users]
    session.close()
    return users_dict

def select_userid_by_name(user:str)->int:
    ''' Returns User ID by USERNAME '''
    session=Session()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    result= db_user.id
    session.close()
    return result
