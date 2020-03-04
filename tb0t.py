import os,telebot,sys,json,time
from sqlalchemy import Table, Column,DateTime, Integer, String, Float,LargeBinary, MetaData, ForeignKey, engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship


keyboard1=telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row('/add','/list','/reset')
bot = telebot.TeleBot(token)

place_dict={}
# DB part STRATS
db_url=os.environ['DATABASE_URL']
engine=create_engine(db_url)
Base = declarative_base()
metadata = MetaData()

class Userinfo(Base):
    __tablename__='userinfo'
    id = Column(Integer, primary_key=True)
    username = Column( String(20))
    user_fio = Column( String(100))
    messanger = Column( String(20))
    logs = relationship("UserLog", back_populates="user",cascade="all, delete, delete-orphan")

class UserLog(Base):
    __tablename__='userlog'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    date=Column(DateTime)
    #place_id = Column(Integer, ForeignKey("place.id"))
    user = relationship("Userinfo", back_populates="logs")
'''
class Place(Base):
    __tablename__='place'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("userinfo.id"))
    util_type=Column( String(20))
    loc_lat = Column(Float)
    loc_lon = Column(Float)
    text = Column( String(100))
    photo = Column(LargeBinary)
'''
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def insert_log(user:str, place:str):
    ''' Save log'''
    session=Session()
    db_user = session.query(Userinfo).filter(Userinfo.username==user).one()
    db_log =UserLog ( user_id=db_user.id, date= time.ctime())
    session.add(db_log)
    session.commit()   
    session.close()

def insert_user(user:str,message)->None:
    ''' Save USER in Postgres DB '''
    session=Session()
    user_list=[i[0] for i in session.query(Userinfo.username)]
    if not user in user_list:
        db_user= Userinfo(  username=user, 
                            user_fio = '{} {}'.format(message.from_user.first_name, message.from_user.last_name),
                            messanger = 'telegram')
        session.add(db_user)
    else: 
        print ('User already in base')
    session.commit()   
    session.close()
'''
def insert_location(lat:float,lon:float,user:str)->None:
    # Save LOCATION (latitude, longitude) in Postgres DB 
    session=Session()
    user_list=[i[0] for i in session.query(Teleuser.username)]
    if user in user_list:
        myuser = session.query(Teleuser).filter(Teleuser.username==user).one()
        location = Location(user_id = myuser.id,loc_lat = lat,loc_lon = lon)
        session.add(location)
        session.commit()
    else: print ('Cant find {} in base'.format(user))
    session.close()
'''
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
# DB part ENDS




@bot.message_handler(commands=['start'])
def start_message(message):
    greeting='''
    Привет это бот напоминалка о тех местах которые ты хотел бы посетить повторно
    /add - для добавления места в список
    /list - для отображения списка
    /reset - для удаления инфы из списка
    '''
    bot.send_message(message.chat.id,greeting)

@bot.message_handler(commands=['reset'])
def reset_message(message):
    session=Session()
    user_list=[i[0] for i in session.query(Userinfo.user_id)]
    session.close()
    if not str(message.chat.id) in user_list: 
        bot.send_message(message.chat.id,'Пока данных по вам нет',reply_markup=keyboard1)
    else: 
        delete_user(str(message.chat.id))
        bot.send_message(message.chat.id,'Ваши данные успешно удалены',reply_markup=keyboard1)
'''
@bot.message_handler(commands=['users_list'])
def list_message(message):
    session=Session()
    user_list=[i[0] for i in session.query(Teleuser.username)]
    if not str(message.chat.id) in user_list:
        bot.send_message(message.chat.id,'Пока данных нет',reply_markup=keyboard1)
    else:
        myuser = session.query(Teleuser).filter(Teleuser.username==str(message.chat.id)).one()
        loc_list=[{'lat':i,'lon':j} for i,j in session.query(Location.loc_lat,Location.loc_lon).filter(Location.user_id==myuser.id)]
        counter=0
        if len(loc_list)>10 : loc_list=loc_list[-10:] # Case was to list last 10 locations
        for loc in loc_list:
            counter+=1
            bot.send_message(message.chat.id, '{} - место'.format(counter))
            bot.send_location(message.chat.id, loc['lat'], loc['lon'])
    session.close()
    bot.send_message(message.chat.id,'-= END =-',reply_markup=keyboard1) 

'''
@bot.message_handler(commands=['add'])
def add_message(message):
    bot.send_message(message.chat.id,'Привет, введи место')
    insert_user(str(message.from_user.id),message)

'''
@bot.message_handler(content_types=['location'])
def get_location(message):
    session=Session()
    user_list=[i[0] for i in session.query(Teleuser.username)]
    print (user_list)
    session.close()
    if not str(message.chat.id) in user_list:    
        bot.send_message(message.chat.id,'Введите /add',reply_markup=keyboard1)
    else:
        insert_location(message.location.latitude,message.location.longitude,str(message.chat.id))
        bot.send_message(message.chat.id,'Мастонахождение добавлено',reply_markup=keyboard1)
'''
    def start_bot(token):
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    
    def stop_bot(token):
        bot.remove_webhook()
        bot.set_webhook(url='https://ecoukhta.herokuapp.com/' + token)


bot.polling()