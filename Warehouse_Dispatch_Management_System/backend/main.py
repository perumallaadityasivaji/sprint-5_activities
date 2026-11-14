from fastapi import FastAPI, HTTPException,Header,Body
import functions
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "Warehouse-Dispatch-Management running successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods = ["*"],
    allow_headers = ["*"],

)


@app.post("/login")
def login(username = Body(), password = Body()):
    token = functions.verify_login(username=username,password=password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": token}


@app.post("/refresh")
def refresh(refresh_token =Header(None)):
    username = functions.verify_token(token=refresh_token,token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    access_token = functions.create_token(username=username,token_type="access")
    return {"access_token": access_token}


@app.post("/register")
def register(user_name=Body(),password = Body()):
    if functions.register_user(user_name,password):
        return {"message":"user register successfully"}
    raise HTTPException(status_code=400,detail = "User already exist")



@app.post("/packages", status_code=201)
def register_package(package_name: str, destination: str, weight: float, arrival_date:datetime):
    if weight <= 0:
        raise HTTPException(status_code=422, detail="Weight must be greater than 0")
    return functions.add_package(package_name, destination, weight, arrival_date)


@app.get("/packages/{package_id}")
def get_package_details(package_id = None,token=Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    response = functions.get_package(package_id=package_id)
    if response is None:
        raise HTTPException(status_code=404,detail="Package not found")
    return response


@app.patch("/update_package")
def update_package(package_id,status):
    return functions.update_package_status(package_id,status)

@app.delete("/delete_packages")
def deleting_packages(package_id):
    return functions.delete_package(package_id)



@app.get("/search_dispatch_batches")
def search_batches(destination=None, status=None, vehicle=None):
    response = functions.search_dispatch_batches( destination,status,vehicle)
    if response is None:
        raise HTTPException(status_code=404,detail="Dispatch batches not found")
    return response

@app.get("/packages/search")
def search_packages(destination: str, status: str, arrival_date: datetime, token = Header(None)):
    username = functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return functions.get_all_packages(destination=destination, status=status, arrival_date=arrival_date)

@app.get("/warehouse/statistics")
def warehouse_statistics(token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or Expired token")
    statistics = functions.get_warehouse_statistics()
    return statistics

@app.post("/dispatch_batches")
def create_batch(destination: str, vehicle: str, package_id: list[int]):
    response = functions.create_dispatch_batch(destination, vehicle, package_id)
    if response == "No packages provided":
        raise HTTPException(status_code=400, detail="No packages provided")
    if response == "Package not found":
        raise HTTPException(status_code=404, detail="Package not found")
    if response == "Destination mismatch":
        raise HTTPException(status_code=400, detail="Destination mismatch")
    if response == "Package already assigned or dispatched":
        raise HTTPException(status_code=400, detail="Package already assigned or dispatched")

    return response
    
