from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import Field

app = FastAPI()


@app.get("/r_movie/",{user_id})
async def find_sim_movie():
    pass
    return {'title': ,'vote_average': ,'weighted_vote': }