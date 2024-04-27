'''
Here core functions are defined for different operations.
'''
from typing import Dict

from fastapi import Depends, FastAPI, Request, Form, Body
from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import datetime
import numpy as np
import GPy
from sklearn import preprocessing
import json

from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
            CORSMiddleware,
                allow_origins=["*"],
                    allow_credentials=True,
                        allow_methods=["*"],
                            allow_headers=["*"],
                            )



templates = Jinja2Templates(directory="templates")

def samplePrior(k, xmin=1, xmax=8, normalize = True):
    xx, yy = np.mgrid[xmin:xmax+1, xmin:xmax+1]
    X = np.vstack((xx.flatten(), yy.flatten())).T 
    K = k.K(X) #compute covariance matrix of x X
    s = np.random.multivariate_normal(np.zeros(X.shape[0]), K) #GP prior distribution
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
    #scale to range
    if normalize==True:
        s = min_max_scaler.fit_transform(s.reshape(-1,1))
    return s

def getmap(type='rough', reward_list=None):
    if type == 'rough':
        k = 1
    elif type == 'smooth':
        k = 2
    kernel1 = GPy.kern.RBF(input_dim=2, variance=1, lengthscale=k)
    out = samplePrior(kernel1, xmin=1, xmax=8)
    out = out.reshape(-1)
    out[out.argsort()] = np.array(reward_list)
    return out.astype(int)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def read_form():
    return 'hello world'

@app.post('/get_map')
@app.get('/get_map')
def Map_Get(user_id=Form(None), level_id=Form(None),sum_count=Form(None),reward_list=Form(None),map_type=Form(None), db: Session = Depends(get_db)):
    # user_id = data['user_id']
    # level_id = data['level_id']
    # sum_count = data['sum_count']
    # reward_list = data['reward_list']
    # map_type = data["map_type"]
    reward_list = json.loads(reward_list)
    if(db.query(models.User).filter(models.User.id == user_id).first() is None):
        return JSONResponse(content={"msg": "user not found","data":"","status_code": 204}, status_code=204)
    # 生成一张地图排列
    map = getmap(type=map_type, reward_list=np.sort(reward_list))
    map_json = json.dumps({"map": map.tolist()})
    # 存储到对应用户的数据库中
    db_map = models.MapInfo(owner_id=user_id,level_id=level_id,sum_count=sum_count,map=map_json, map_type=map_type)
    db.add(db_map)
    db.commit()
    db.refresh(db_map)
    result = {
        "map": map.tolist(),
        "map_id": db_map.id
    }
    return JSONResponse(content={"msg":"succeed","data": result, "status_code": 200}, status_code=200)

@app.post('/add_user')
def Add_User_Post(name=Form(None), birthdate=Form(None), gender=Form(None), db: Session = Depends(get_db)): 
    # check if the user is already in the database
    # if db.query(models.User).filter(models.User.name == name).first() is not None:
        # return JSONResponse(content={"msg":"user already exists","data":"","status_code": 204}, status_code=204)
    # add user to the database
    db_user = models.User(name=name, birthdate=birthdate, gender=gender)
    db.add(db_user)
    db.commit()      
    db.refresh(db_user)
    # check if the user is successfully added
    user_id = db_user.id # getting the last newly inserted primary key
    result = jsonable_encoder(db.query(models.User).filter(models.User.id == user_id).first())
    if(result is None):
        return JSONResponse(content={"msg": "creating user failed","data":"","status_code": 204}, status_code=204)
    return JSONResponse(content={"msg": "succeed","data": result, "status_code": 200}, status_code=200)


@app.post('/add_info')
def Add_Info_Post(user_id=Form(None),map_id=Form(None),block_index=Form(None),block_value=Form(None),block_clicked=Form(None),
                  remain_count=Form(None), level_score=Form(None), sum_score=Form(None), reaction_time=Form(None),
                  is_finish=Form(None),db: Session = Depends(get_db)): 
    user_id = int(user_id)
    map_id = int(map_id)
    block_index = int(block_index)
    block_value = int(block_value)
    block_clicked = int(block_clicked)
    remain_count = int(remain_count)
    level_score = int(level_score)
    sum_score = int(sum_score)
    reaction_time = float(reaction_time)
    is_finish = int(is_finish)
    # check if user exists
    if(db.query(models.User).filter(models.User.id == user_id).first() is None):
        return JSONResponse(content={"msg": "user not found","data":"","status_code": 204}, status_code=204)
    # check if map exists
    if(db.query(models.MapInfo).filter(models.MapInfo.id == map_id).first() is None):
        return JSONResponse(content={"msg": "map not found","data":"","status_code": 204}, status_code=204)
    # check if the map is the same as the user
    if(db.query(models.MapInfo).filter(models.MapInfo.id == map_id).first().owner_id != user_id):

        return JSONResponse(content={"msg": "map not match user","data":"","status_code": 204}, status_code=204)
    db_info = models.PlayInfo(owner_id=user_id, map_id = map_id, block_index=block_index, block_value=block_value, 
                            block_clicked=block_clicked, remain_count=remain_count,  
                            level_score=level_score, sum_score=sum_score, 
                            reaction_time=reaction_time, 
                            is_finish=is_finish)
    db.add(db_info)
    db.commit()      
    db.refresh(db_info)
    info_id = db_info.id # getting the last newly inserted primary key
    result = jsonable_encoder(db.query(models.PlayInfo).filter(models.PlayInfo.id == info_id).first())
    return JSONResponse(content={"msg": "succeed","data": result, "status_code": 200}, status_code=200)
