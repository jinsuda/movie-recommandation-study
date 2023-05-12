from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import Field
from database import engineconn
from models import Movie_df

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from ast import literal_eval
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
engine = engineconn()
session = engine.sessionmaker()

movies = pd.read_csv('../tmdbData.csv')

movies_df = movies[['title','genres','id','release_date','overview','original_title','vote_average','vote_count','poster_path']]

movies_df['genres'] = movies_df['genres'].apply(literal_eval)

# 영화 장르들을 띄어쓰기로 구분해서 한줄로 넣음
movies_df['genres_literal'] = movies_df['genres'].apply(lambda x: (' ').join(x))

count_vect = CountVectorizer(min_df=0, ngram_range=(1, 2))
genre_mat = count_vect.fit_transform(movies_df['genres_literal'])
genre_sim = cosine_similarity(genre_mat, genre_mat)

# 유사도가 가장 높은 순으로 정렬
genre_sim_sorted = genre_sim.argsort()[:, ::-1]

# 가중평점 공식
C = movies_df['vote_average'].mean()
m = movies_df['vote_count'].quantile(0.6)
def weighted_vote_average(record):
    v = record['vote_count']
    R = record['vote_average']

    return ((v/(v+m)) * R) + ((m/(v+m)) * C)

movies_df['weighted_vote'] = movies.apply(weighted_vote_average, axis=1)

def find_sim_movie(df, sorted_idx, title_name, top_list=10):
    title_movie = df[df['title'] == title_name]
    title_index = title_movie.index.values
    #print(title_movie)
    # 장르 유사성이 높은 영화 top_list의 2배수만큼 후보선정
    similar_index = sorted_idx[title_index, :(top_list*2)]
    similar_index = similar_index.reshape(-1)
    
    similar_index = similar_index[similar_index != title_index] # 기존 영화 인덱스 제외
    
    return df.iloc[similar_index].sort_values('weighted_vote', ascending=False)[:top_list]

@app.get("/recommand_movie/{title}")
async def find_sim_movie_api(title):
    df = movies_df
    sorted_idx = genre_sim_sorted
    top_list = 10
    title_movie = df[df['title'] == title]
    title_index = title_movie.index.values

    # 장르 유사성이 높은 영화 top_list의 2배수만큼 후보선정
    similar_index = sorted_idx[title_index, :(top_list*2)]
    similar_index = similar_index.reshape(-1)

    similar_index = similar_index[similar_index != title_index]  # 기존 영화 인덱스 제외

    movie_recommand = df.iloc[similar_index].sort_values('weighted_vote', ascending=False)[:top_list]
    print(movie_recommand['title'].to_list())
    
    ######### 데이터베이스에 접근해서 해당되는 영화들의 정보를 하나의 Json 형태로 만들어서 Return 
    return movie_recommand['title'].to_list()
    #return {'title': ,'vote_average': ,'weighted_vote': }

def recommand_movie_list():
    pass
