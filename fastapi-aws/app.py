from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import Field

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/all/")
async def all_movies():
    pass
    return {"result": }

@app.get("/similar_movie/")
async def similar_movie():
    pass
    return {'title': ,'vote_average': ,'weighted_vote': }