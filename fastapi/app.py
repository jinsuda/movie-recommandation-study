from fastapi import FastAPI
from pymongo import MongoClient
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from ast import literal_eval
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origins = [
#     "http://localhost:3000",
#     "localhost:3000"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )



movies = pd.read_csv('../data/tmdbData.csv')

movies_df = movies[['title','genres','id','release_date','overview','original_title','vote_average','vote_count','poster_path']]

movies_df['genres'] = movies_df['genres'].apply(literal_eval)

# 영화 장르들을 띄어쓰기로 구분해서 한줄로 넣음
movies_df['genres_literal'] = movies_df['genres'].apply(lambda x: (' ').join(x))

count_vect = CountVectorizer(min_df=0, ngram_range=(1, 2))
genre_mat = count_vect.fit_transform(movies_df['genres_literal'])
genre_sim = cosine_similarity(genre_mat, genre_mat)

# 유사도가 가장 높은 순으로 정렬
genre_sim_sorted = genre_sim.argsort()[:, ::-1]

    
# 몽고db 연결    
client = MongoClient("mongodb+srv://admin:1q2w3e4r@cluster0.yvz01u3.mongodb.net/?retryWrites=true&w=majority")

db = client['Movie'] 
movieInfo = db.movieInfo
movieInfo = db["movieInfo"]

    
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

# @app.get("/recommand_movie/{title}")
# async def find_sim_movie_api(title):
#     df = movies_df
#     sorted_idx = genre_sim_sorted
#     top_list = 10
#     title_movie = df[df['title'] == title]
#     title_index = title_movie.index.values

#     # 장르 유사성이 높은 영화 top_list의 2배수만큼 후보선정
#     similar_index = sorted_idx[title_index, :(top_list*2)]
#     similar_index = similar_index.reshape(-1)

#     similar_index = similar_index[similar_index != title_index]  # 기존 영화 인덱스 제외

#     movie_recommand = df.iloc[similar_index].sort_values('weighted_vote', ascending=False)[:top_list]
#     print(movie_recommand['title'].to_list())
    
#     ######### 데이터베이스에 접근해서 해당되는 영화들의 정보를 하나의 Json 형태로 만들어서 Return 
#     return movie_recommand['title'].to_list()


@app.get("/recommand_movie_list/{title}")
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
    
    mr_list =movie_recommand['title'].to_list()
    
    #results_dict = dict()
    recommand_results = list()
    for i in range(len(mr_list)):
        mlist = movieInfo.find({'title': mr_list[i]})
        
        for info in mlist:
            info.pop('_id', None)
            recommand_results.append(info)
    
    results_dict = {"Results": recommand_results}  
    #print(results_dict)  
    #print(len(results_dict['Results']))    
    results_dict = jsonable_encoder(results_dict)
    return results_dict