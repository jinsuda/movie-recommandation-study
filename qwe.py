from fastapi import FastAPI
from tensorflow import keras
import numpy as np
import pandas as pd
from pydantic import BaseModel
from model import ingredient


app = FastAPI()

# 모델 파일 경로
MODEL_FILE_PATH = "aa.h5"

# 모델 로드
model = keras.models.load_model(MODEL_FILE_PATH)
data = pd.read_csv("tmdbData.csv")


class Item(BaseModel):
    ingredient: str
    amount: int


@app.post("/recommand_movie_list")
async def predict(item: Item):
    input_data = dict({item.ingredient: item.amount})
    # 모델 예측
    print(input_data)
    try:
        df = pd.DataFrame(columns=data.columns)
        df = pd.concat([df, pd.DataFrame([input_data])], ignore_index=True)
        df.fillna(0, inplace=True)
        df = df.iloc[:, 2:]
        print(df)
        df1 = df.values
        df2 = df1.astype(float)
        predictions = model.predict(df2)
        result = np.argmax(predictions)

        res = data.loc[data["요리타겟"] == result]["요리"].unique()
    except Exception as e:  # 예외 처리
        print("에러 발생:", e)
    print(res)
    # 예측 결과 반환
    return res[0]