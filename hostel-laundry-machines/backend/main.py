from fastapi import FastAPI, HTTPException,Header,Body,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import functions


class MachineCreate(BaseModel):
    name: str
    block: str
    kind: str
    cycles_minutes: int = Field(gt=0)
    in_service: bool


class MachineUpdate(BaseModel):
    machine_id: int
    in_service: bool


class MachineRun(BaseModel):
    roll_no: str
    machine_id: int


class MachineCollect(BaseModel):
    roll_no: str
    machine_id: int


class MachineNotCollected(BaseModel):
    roll_no: str
    machine_id: int

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Laundry-Hostel-Machines running successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def get_current_user(token: str = Header(None)):
    user = functions.verify_token(token=token, token_type="access")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def staff_only(user=Depends(get_current_user)):
    role = functions.get_user_role(user)
    if role != "staff":
        raise HTTPException(status_code=403, detail="Only laundry staff can do this")
    return user


# ---for register and login 

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

#-----


@app.post("/add_machine")
def add_machine(machine: MachineCreate, user=Depends(staff_only)):

    return functions.add_machines(machine.name, machine.block, machine.kind,machine.cycles_minutes, machine.in_service)

@app.get("/get_machines by id/{machine_id}")
def get_machines_by_id(machine_id: int, user=Depends(get_current_user)):
    return functions.get_machines_by_id(machine_id)


@app.get("/get_all_machines/")
def get_all_machines(block=False, kind=False, user=Depends(get_current_user)):
    return functions.get_machines(block, kind)

@app.patch("/update_machine/")
def update_machine(machine: MachineUpdate, user=Depends(staff_only)):

    return functions.update_machines(machine.in_service, machine.machine_id)

@app.post("/machine/roll_no")
def start_with_roll_no(machine: MachineRun, user=Depends(get_current_user)):
    return functions.start_with_roll_no(machine.roll_no, machine.machine_id)


@app.post("/machine/collect_roll_no")
def collect_by_roll_no(machine: MachineCollect, user=Depends(get_current_user)):
    return functions.collect_by_roll_no(machine.roll_no, machine.machine_id)

@app.patch("/machine/not_collected_roll_no")
def not_collected(machine: MachineNotCollected, user=Depends(staff_only)):

    return functions.clothes_not_collected(machine.roll_no, machine.machine_id)


