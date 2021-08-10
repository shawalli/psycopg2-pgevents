from sqlalchemy import Column, Integer, String                                                                                                                                                                          
from sqlalchemy import create_engine                                                                                                                                                                                    
from sqlalchemy.ext.declarative import declarative_base                                                                                                                                                                 
from sqlalchemy import inspect                                                                                                                                                                                          
from sqlalchemy.orm import sessionmaker                                                                                                                                                                                 
from faker import Faker                                                                                                                                                                                                 
                                                                                                                                                                                                                        
faker = Faker()                                                                                                                                                                                                         
                                                                                                                                                                                                                        
DB_PORT=5432                                                                                                                                                                                                            
DB_USERNAME="postgres"                                                                                                                                                                                                  
DB_PASSWORD="password"                                                                                                                                                                                                  
DB_HOST="127.0.0.1"                                                                                                                                                                                                     
DB_DATABASE="eventtriggertest"                                                                                                                                                                                          
                                                                                                                                                                                                                        
DATABASE_URI = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"                                                                                                                   
                                                                                                                                                                                                                        
engine = create_engine(DATABASE_URI, echo = True)                                                                                                                                                                       
Session = sessionmaker(bind = engine)                                                                                                                                                                                   
Base = declarative_base()                                                                                                                                                                                               
                                                                                                                                                                                                                        
session = Session()                                                                                                                                                                                                     
                                                                                                                                                                                                                        
class Customer(Base):                                                                                                                                                                                                   
    __tablename__ = 'customers'                                                                                                                                                                                         
    customer_id = Column(Integer, primary_key=True)                                                                                                                                                                     
    name = Column(String)                                                                                                                                                                                               
    address = Column(String)                                                                                                                                                                                            
    email = Column(String)                                                                                                                                                                                              

class User(Base):                                                                                                                                                                                                       
    __tablename__ = 'users'                                                                                                                                                                                             
    user_id = Column(Integer, primary_key=True)                                                                                                                                                                         
    name = Column(String)                                                                                                                                                                                               
    address = Column(String)                                                                                                                                                                                            
    email = Column(String)                                                                                                                                                                                              

def update_persons():

    u_u = session.query(User).first()
    c_u = session.query(Customer).first()
    u_u.name = faker.name()
    c_u.name = faker.name()
    session.add(u_u)
    session.add(c_u)

    session.commit()


def delete_persons():

    u_d = session.query(User).first()
    c_d = session.query(Customer).first()

    session.delete(u_d)
    session.delete(c_d)
    session.commit()



def add_persons():

    c = Customer()                                                                                                                                                                                                      
    u = User()                                                                                                                                                                                                          

    u.name = faker.name()                                                                                                                                                                                               
    u.email = faker.email()                                                                                                                                                                                             
    u.address = faker.address()                                                                                                                                                                                         
                                                                                                                                                                                                                    
    c.name = faker.name()                                                                                                                                                                                               
    c.email = faker.email()                                                                                                                                                                                             
    c.address = faker.address()                                                                                                                                                                                         

    session.add(c)
    session.add(u)
    session.commit()


def main():                                                                                                                                                                                                             
    Base.metadata.create_all(engine)                                                                                                                                                                                    
    insp = inspect(engine)                                                                                                                                                                                              
    print(insp.get_table_names())                                                                                                                                                                                       


if __name__ == '__main__':                                                                                                                                                                                              
    main()                                                                                                                                                                                                              
    add_persons()
    update_persons()
    delete_persons()
