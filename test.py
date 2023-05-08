# %% [markdown]
# # 추천시스템

# %% [markdown]
# ## 콘텐츠 기반 필터링(Content based filtering) 실습
# - 장르 속성을 이용한 콘텐츠 기반 필터링 만들기

# %% [markdown]
# ### 1. 데이터 로딩 및 가공

# %%
# TMDB 5000영화 데이터 세트
# https://www.kaggle.com/tmdb/tmdb-mivie-metadata

# %%
import pandas as pd
import numpy as np
import warnings; warnings.filterwarnings('ignore')

# %%
movies = pd.read_csv('./data/tmdb_5000_movies.csv')
print(movies.shape)
movies.head()

# %%
# id, 영화제목title, 장르genres, 평균평점vote_average, 평점 투표수vote_count, 영화인기popularuty, 주요키워드문구keywords, 영화개요설명overview
movies_df = movies[['id','title','genres','vote_average','vote_count','popularity','keywords','overview']]

# %%
# 칼럼이 어떤 형태로 돼있는지 확인
pd.set_option('max_colwidth',100) # 보는 옶션 설정
movies_df[['genres','keywords']][:1] 
# 리스트[]안에 {}딕셔너리가 있는 형태의 문자열인것을 확인했다.
# 장르의 명칭은 딕셔너리의 키인 "name"으로 추출가능, keywords도 마찬가지.

# %%
from ast import literal_eval
movies_df['genres'] = movies_df['genres'].apply(literal_eval)
movies_df['keywords'] = movies_df['keywords'].apply(literal_eval)

# %%
# genres컬럼에서 장르명만, keywords컬럼에서 키워드만 리스트로 추출하기
# 리스트 내 여러개의 딕셔너리의 'name'키에 해당하는 값을 찾아 이를 리스트 형태로 변환
movies_df['genres'] = movies_df['genres'].apply(lambda x : [ y['name'] for y in x])
movies_df['keywords'] = movies_df['keywords'].apply(lambda x : [ y['name'] for y in x])
movies_df[['genres','keywords']][:1]

# %%
# 위에 코드를 이중 for문으로 하면?
'''
장르=[]
for x in movies_df['genres'][:1]:
    for y in x:
        장르.append(y['name'])
        print(y['name'])
print(장르)
'''

# %% [markdown]
# ### 2. 장르 콘텐츠 유사도 측정

# %% [markdown]
# - 문자열로 반환된 genres 컬럼을 count기반으로 피처 벡터화 변환
# - genres 문자열을 피처 벡터화 행렬로 변환한 데이터 세트를 코사인 유사도를 통해 비교. 이를 위해 데이터 세트의 레코드별로 타 레코드와 장르에서 코사인 유사도 값을 가지는 객체를 생성
# - 장르 유사도가 높은 영화중에 평점이 높은 순으로 영화를 추천

# %%
from sklearn.feature_extraction.text import CountVectorizer

# CountVectorizer적용을 위해 공백문자로 word 단위가 구분되는 문자열로 변환.
movies_df['genres_literal'] = movies_df['genres'].apply(lambda x : (' ').join(x))
movies_df.head()

# %%
# min_df로 지정한 값보다 작은 경우에는 무시 
count_vect = CountVectorizer(min_df=0, ngram_range=(1,2)) # ngram 단어의 묶음을 1개부터 2개까지 설정(science Fiction같은 2개도 묶음)
genre_mat = count_vect.fit_transform(movies_df['genres_literal'])
print(genre_mat.shape)
#4803개 레코드, 276개 개별단어피처로 구성된 피처벡터행렬 생성

# %%
# 생성한 행렬에 코사인 유사도 계산
from sklearn.metrics.pairwise import cosine_similarity

genre_sim = cosine_similarity(genre_mat, genre_mat)
print(genre_sim.shape)
print(genre_sim[:5]) # genre_sim객체는 movies_df의 genre_literal칼럼을 피처벡터화한 행렬(genre_mat)데이터의 행별 유사도 정보를 갖고있다.
# 장르기준으로 콘텐츠기반필터링을 하려면 genre_sim객체 이용해서 가장 장르 유사도가 높은 순으로 레코드 추출해야함.

# %%
# 유사도가 가장 높은 순으로 정렬
genre_sim_sorted_index = genre_sim.argsort()[:,::-1]
print(genre_sim_sorted_index[:1])
# 0번 레코드는 3494번 레코드가 가장 유사도가 높고, 그다음이 813레코드, 가장 유사도가 낮은 레코드는 2401번이다.

# %% [markdown]
# ### 3. 장르 콘텐츠 필터링을 이용한 영화 추천

# %%
def find_sim_movie(df, sorted_ind, title_name, top_list=10): # title_name : 추천기준 영화이름, top_list : 상위 10개만 추천
    # movies_df 'title'컬럼에 입력된 title_name값인 df출력
    title_movie = df[df['title'] == title_name]
    
    # title_named을 가진 DF의 index 객체를 ndarray로 반환
    title_index = title_movie.index.values
    # genre_sim_sorted_index객체에서 유사도 순으로 top_list개 index추출
    similar_indexes = sorted_ind[title_index, :(top_list)]
    
    # top_list index출력. (2차원->1차원으로)
    print(similar_indexes)
    similar_indexes = similar_indexes.reshape(-1)
    
    return df.iloc[similar_indexes]

# %%
movies_df[movies_df['title'] == 'The Godfather']

# %%
# 만든 함수를 이용해서 영화'대부'와 장르별로 유사한 상위 10개 영화를 추천
similar_movies = find_sim_movie(
    movies_df, genre_sim_sorted_index, 'The Godfather', 10)
similar_movies[['title', 'vote_average']]
# kids등 대부를 좋아하는 사용자에게 추천하기 맞지 않아보이고, 평점이 0인 영화도 있으므로 개선이 필요해보임.

# %%
movies_df[['title', 'vote_average', 'vote_count']].sort_values('vote_average', ascending=False)[:10] # False 내림차순
# 평균평점순으로 정렬했더니 유사성이 낮아보이는 still Upper Lips이 더 높은 평점으로 추천되었다. 투표수를 보니 평가횟수가 1회로 매우적다.
# 왜곡된 평점데이터를 회피하기위해 유명한 영화 평점 사이트인 IMDB에서 가중 평점 방식을 사용.

# %% [markdown]
# - 가중 평점(Weighted Rating) = (v/(v+m)) * R + (m/(v+m)) * C
#     - v : 개별 영화에 평점을 투효한 횟수
#     - m : 평점을 부여하기 위한 최소 투표 횟수
#     - R : 개별 영화에 대한 평균 평점
#     - C : 전체 영화에 대한 평균 평점

# %%
# v = 'vote_count'
# R = 'vote_average'
# C = movies_df['vote_average'].mean()

# m = 값이 높으면 평점 투표 횟수가 많은 영화에 더 많은 가중 평점을 부여. 상위 60%에 해당하는 
# 횟수를 기준(pandas 함수명은 quantile( ), numpy 함수명은 percentile( ))

C = movies_df['vote_average'].mean()
m = movies_df['vote_count'].quantile(0.6)
print('C:', round(C,3), 'm:', round(m,3))

# %%
# 기존 평점을 새로운 가중 평점으로 변경하는 함수 생성하고 새로운 평점 정보는 'weighted_vote'컬럼을 생성해서 출력
percentile = 0.6
m = movies['vote_count'].quantile(percentile)
C = movies['vote_average'].mean()

def weighted_vote_average(record):
    v = record['vote_count']
    R = record['vote_average']
    
    return ((v/(v+m)) * R) + ((m/(v+m)) * C)

movies['weighted_vote'] = movies.apply(weighted_vote_average, axis=1)

# %%
movies[['title', 'vote_average', 'weighted_vote', 'vote_count']].sort_values('weighted_vote',ascending=False)[:10]

# %%
# 새로운 평점 기준에 따라서 영화를 추천해보기
def find_sim_movie(df, sorted_ind, title_name, top_list=10):
    title_movie = df[df['title'] == title_name]
    title_index = title_movie.index.values
    
    # 장르 유사성이 높은 영화 top_list의 2배수만큼 후보선정
    similar_indexes = sorted_ind[title_index, :(top_list*2)]
    similar_indexes = similar_indexes.reshape(-1)
    
    similar_indexes = similar_indexes[similar_indexes != title_index] # 기존 영화 인덱스 제외
    
    # weighted_vote 값이 높은순으로 top_list만큼 추출
    return df.iloc[similar_indexes].sort_values('weighted_vote', ascending=False)[:top_list]

similar_movies = find_sim_movie(movies, genre_sim_sorted_index, 'The Godfather', 10)
similar_movies[['title', 'vote_average', 'weighted_vote']]

# %%
movies_df = movies[['id', 'title']].copy()

# %%
#import pickle
#pickle.dump(genre_sim, open('genre_sim.pickle', 'wb'))
#pickle.dump(movies_df, open('movies_df.pickle', 'wb'))


