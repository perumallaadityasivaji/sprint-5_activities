from datetime import datetime,timezone,timedelta
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base
from fastapi import  HTTPException,Header
import jwt 
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher()

DB_PATH = "hostel-laundry.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

USERNAME = "Aditya"
PASSWORD = "1234"
ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7*24*60
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

class machines(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    block = Column(String) #a,b,c,d
    kind = Column(String) #Washer, Dryer
    cycles_minutes = Column(Integer)
    in_service = Column(Integer)

class runs(Base):
    __tablename__ = "runs"
    run_id = Column(Integer, primary_key = True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    roll_no = Column(String)
    started_at = Column(DateTime, default = datetime.now) #YYYY-MM-DD HH:MM
    ends_at = Column(DateTime)
    collected_at = Column(DateTime) #Empty until collected
    status = Column(String) #Running, Completed, Collected


class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer,primary_key = True)
    user_name = Column(String)
    password = Column(String)
    role = Column(String, default="student")
    
    
Base.metadata.create_all(engine)

def add_machines(name, block, kind, cycles_minutes, in_service):
    
    session = Session(engine)
    new_machine = machines(
        name = name,
        block = block,
        kind = kind,
        cycles_minutes = cycles_minutes,
        in_service = in_service
    )
    session.add(new_machine)
    session.commit()

    response = {
        "id": new_machine.id,
        "name": new_machine.name,
        "block": new_machine.block,
        "kind": new_machine.kind,
        "cycles_minutes": new_machine.cycles_minutes,
        "in_service": new_machine.in_service
    }
    session.close()
    return response

def get_machines_by_id(machine_id):
   
    session = Session(engine)
    machine = session.get(machines, machine_id)
    if machine is None:
        raise HTTPException(status_code = 404, detail = "Can't find machine with the given ID")
    response = {
        "id": machine.id,
        "name": machine.name,
        "block": machine.block,
        "kind": machine.kind,
        "cycles_minutes": machine.cycles_minutes,
        "in_service": machine.in_service
    }
    session.close()
    return response

def get_machines(block = False, kind = False):
    
       
    session = Session(engine)
    Machines = session.query(machines).all()
    response = []
    for Machine in Machines:
        temp_Machine = {
            "id": Machine.id,
            "name": Machine.name,
            "block": Machine.block,
            "kind": Machine.kind,
            "cycles_minutes": Machine.cycles_minutes,
            "in_service": Machine.in_service
        }
        response.append(temp_Machine)
    session.close()
    return response

def update_machines(in_service, machine_id):
   
    session = Session(engine)
    machine = session.query(machines).filter(machines.id == machine_id).first()
    if machine is None:
        raise HTTPException(status_code = 404, detail = "Can't find machine with the given ID")
    machine.in_service = in_service
    session.commit()
    response = {
        "Machine status updated successfully"
    }
    session.close()
    return response
def start_with_roll_no(roll_no, machine_id): #Start a machine with a roll number. It starts now and ends after the machine's cycle minutes.
    
    session = Session(engine)
    run = runs(roll_no=roll_no,machine_id=machine_id)
    session.add(run)
    session.commit()
    
    response = {
        "id": run.machine_id,
        "started_at" : run.started_at,
        "ends_at" : run.ends_at
    }
    session.close()
    return response

def collect_by_roll_no(roll_no,machine_id):
            
    session =Session(engine)
    
    run = runs(roll_no=roll_no,machine_id=machine_id)
    session.add(run)
    session.commit()
    
    response = {
        "started_id":run.started_at,
       "collected_at":run.collected_at,
    }
    session.close()
    return response
    
def clothes_not_collected(roll_no,machine_id):
  
            
    session=Session(engine)
    
    run = session.query(runs).filter(runs.roll_no == roll_no,runs.machine_id == machine_id).first()
    if run.status != "Completed":
        raise HTTPException(status_code=400,detail="Only completed runs can be cleared")
    
    session.commit()
    response ={
        "roll_no": run.roll_no,
        "machine_id":run.machine_id,
        "collected_at" : run.collected_at,
        "status":run.status,     
    }
    session.close()
    return response
    
    
def verify_login(username,password):
    session = Session(engine)
    user = session.query(User).filter(user_name = username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password,password)
    except VerifyMismatchError:
        return False
    session.close()
    access_token = create_token(username=username,token_type = "access")
    refresh_token = create_token(username=username,tokey_type="refresh")
    return {"access_token" : access_token,"refresh_token" : refresh_token}

#Users ---

def register_user(user_name:str,password:str):
    session = Session(engine)
    user_exist = session.query(User).filter(user_name = user_name).first()
    if user_exist is None:
        session.close()
        return False
    session.add(User(user_name=user_name,password=ph.hash(password)))
    session.commit()
    session.close()
    return True

def create_token(username,token_type):
    time  = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "username" : username,
        "token_type" : token_type,
        "exp" : datetime.now(timezone.utc) + timedelta(minutes = time)
        
    }
    token = jwt.encode(payload = payload , key=SECRET_KEY , algorithm = ALGORITHM)
    return token

def verify_token(token,token_type):
    try :
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload["token_type"] == token_type:
            return payload["username"]

        return False

    except jwt.InvalidTokenError:
        return False
    

