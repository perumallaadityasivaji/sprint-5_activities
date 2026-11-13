from datetime import datetime,timedelta,timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine, Float
from sqlalchemy.orm import Session, declarative_base
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

#-- Database connection--
ph = PasswordHasher()

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

USERNAME ="Aditya"
PASSWORD = "123456"
ACCESS_TOKEN_EXPIRY = 15 # MINS
REFERESH_TOKEN_EXPIRY = 7 *24 *60 # MINS
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"


class Package(Base):
    __tablename__ = "packages"
    package_id = Column(Integer, primary_key=True)
    package_name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    arrival_date = Column(DateTime, nullable=False, default=datetime.now)
    status = Column(String, nullable=False, default="Pending")
    

class DispatchBatch(Base):
    __tablename__ = "dispatch_batches"

    batch_id = Column(Integer, primary_key=True)
    destination = Column(String, nullable=False)
    vehicle = Column(String, nullable=False)
    status = Column(String, nullable=False)

class BatchPackage(Base):
    __tablename__ = "batch_packages"

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("dispatch_batches.batch_id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.package_id"), nullable=False)


class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer,primary_key=True)
    user_name = Column(String)
    password = Column(String)
    
Base.metadata.create_all(engine)

def add_package(package_name, destination, weight, arrival_date):
    session = Session(engine)
    package = Package(package_name=package_name, destination=destination,weight=weight, arrival_date=arrival_date)
    session.add(package)
    session.commit()
    response = {
        "id": package.package_id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": str(package.arrival_date),
        "status": package.status
    }
    session.close()
    return response




def get_package(package_id):
    session = Session(engine)

    package = session.query(Package).filter(
        Package.package_id == package_id
    ).first()

    if package is None:
        session.close()
        return None

    response = {
        "package_id": package.package_id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": str(package.arrival_date),
        "status": package.status
    }

    session.close()
    return response

def update_package_status(package_id, status):
    session = Session(engine)

    package = session.query(Package).filter(
        Package.package_id == package_id
    ).first()

    if package is None:
        session.close()
        return None

    package.status = status
    session.commit()

    response = {
        "package_id": package.package_id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": str(package.arrival_date),
        "status": package.status
    }

    session.close()
    return response


def delete_package(package_id):
    session = Session(engine)
    
    package = session.query(Package).filter(
        Package.package_id==package_id).first()
    
    if package is None:
        session.close()
        return None
    
    if package.status == "dispatched" :
        session.close()
        return "dispatched"
    session.query(BatchPackage).filter(BatchPackage.package_id == package_id).delete()
    session.delete(package) 
    session.commit()
    session.close()
    return { "message" : "package deleted"}
    
    
def get_all_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    query = session.query(Package)
    if destination is not None:
        query = query.filter(Package.destination==destination)
    if status is not None:
        query = query.filter(Package.status == status)
    if arrival_date is not None:
        query = query.filter(Package.arrival_date == arrival_date)
    response = {
                "id": Package.id,
                "package_name": Package.package_name,
                "destination": Package.destination,
                "weight": Package.weight,
                "arrival_date": Package.arrival_date,
                "status": Package.status
    }
    session.close()
    return response

def search_dispatch_batches(destination=None, status=None, vehicle=None):
    session = Session(engine)
    query = session.query(DispatchBatch)
    if destination:
        query = query.filter(DispatchBatch.destination == destination)
    if vehicle:
        query = query.filter(DispatchBatch.vehicle == vehicle)
    if status:
        query = query.filter(DispatchBatch.status == status)
    batches = query.all()
    results = []
    for batch in batches:
        results.append({
            "batch_id": batch.batch_id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "status": batch.status
        })
    session.close()
    return results


def get_warehouse_statistics():
    session = Session(engine)

    packages = session.query(Package).all()

    total_received = len(packages)
    pending = 0
    dispatched = 0
    destination_count = {}

    for package in packages:

        if package.status == "pending":
            pending += 1

        if package.status == "dispatched":
            dispatched += 1

        if package.destination in destination_count:
            destination_count[package.destination] += 1
        else:
            destination_count[package.destination] = 1
    session.close()
    return {
        "total_received": total_received,
        "pending": pending,
        "dispatched": dispatched,
        "destination_wise_count": destination_count
    }




def create_dispatch_batch(destination, vehicle, package_id):
    session = Session(engine)

    if len(package_id) == 0:
        session.close()
        return "No packages provided"
    for pid in package_id:
        package = session.query(Package).filter( Package.package_id == pid).first()
        if package is None:
            session.close()
            return "Package not found"
        if package.destination != destination:
            session.close()
            return "Destination mismatch"
        if package.status.lower() in ["assigned", "dispatched"]:
            session.close()
            return "Package already assigned or dispatched"
    batch = DispatchBatch(destination=destination,vehicle=vehicle,status="planned")

    session.add(batch)
    session.commit()
    for pid in package_id:
        batch_package = BatchPackage(batch_id=batch.batch_id,package_id=pid)
        session.add(batch_package)

        package = session.query(Package).filter(Package.package_id == pid).first()
        package.status = "assigned"
        
    session.commit()
    response = {
        "batch_id": batch.batch_id,
        "destination": batch.destination,
        "vehicle": batch.vehicle,
        "status": batch.status,
        "package_id": package_id
    }
    session.close()
    return response


def verify_login(username,password):
    session =Session(engine)
    user = session.query(User).filter_by(user_name = username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password,password)
    except VerifyMismatchError:
        return False
    session.close()
    access_token = create_token(username=username,token_type= "access")
    refresh_token = create_token(username=username,token_type="refresh")
    return {"acceess_token" : access_token,"refresh_token" : refresh_token}



#--Users --

def register_user(user_name:str,password:str):
    session = Session(engine)
    user_exist = session.query(User).filter_by(user_name = user_name).first()
    if user_exist is not None :
        session.close()
        return False
    session.add(User(user_name=user_name,password=ph.hash(password)))
    session.commit()
    session.close()
    return True

def create_token(username,token_type):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFERESH_TOKEN_EXPIRY    
    payload = {
       "username": username,
       "token_type": token_type,
        "exp": datetime.now(timezone.utc)+timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token,token_type):
    try :
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except :
        return False
    
    if payload["token_type"]== token_type:
        return payload["username"]  
    return False
    
    