
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from ast import literal_eval
from sklearn.metrics.pairwise import cosine_similarity


movies = pd.read_csv('./data/tmdb_5000_movies.csv')

movies_df = movies[['id', 'title', 'genres', 'vote_average',
                    'vote_count', 'popularity', 'keywords', 'overview']]


# 장르값이 여러개가 들어있어서 literal_eval로 tuple로 변환

movies_df['genres'] = movies_df['genres'].apply(literal_eval)
movies_df['keywords'] = movies_df['keywords'].apply(literal_eval)


# genres컬럼에서 장르명만, keywords컬럼에서 키워드만 리스트로 넣기
# 리스트 내 여러개의 딕셔너리의 'name'키에 해당하는 값을 찾아서 리스트 형태로 변환
movies_df['genres'] = movies_df['genres'].apply(
    lambda x: [y['name'] for y in x])
movies_df['keywords'] = movies_df['keywords'].apply(
    lambda x: [y['name'] for y in x])


# 장르값들을 벡터화 하기위해 띄어쓰기로 구분되는 문장으로 변환.
movies_df['genres_literal'] = movies_df['genres'].apply(
    lambda x: (' ').join(x))


# min_df로 지정한 값보다 작은 경우에는 무시
# ngram 단어의 묶음을 1개부터 2개까지 설정(science Fiction같은 2개 묶음)
count_vect = CountVectorizer(min_df=0, ngram_range=(1, 2))
genre_mat = count_vect.fit_transform(movies_df['genres_literal'])
# 4803,276 피처벡터행렬


# 생성한 행렬에 코사인 유사도 계산
genre_sim = cosine_similarity(genre_mat, genre_mat)

# 유사도가 가장 높은 순으로 정렬
genre_sim_sorted = genre_sim.argsort()[:, ::-1]

def find_movie(df, sorted_index, title_name, top_list=10):  # top_list : 상위 10개만 추천

    title_movie = df[df['title'] == title_name]
    title_index = title_movie.index.values
    # genre_sim_sorted에서 유사도 순으로 top_list개 index추출
    similar_index = sorted_index[title_index, :(top_list)]

    # top_list index출력. (2차원->1차원으로)
    print(similar_index)
    similar_index = similar_index.reshape(-1)

    return df.iloc[similar_index]


similar_movies = find_movie(
    movies_df, genre_sim_sorted, 'The Godfather', 10)
similar_movies[['title', 'vote_average']]
# kids는 장르가 아예 다름, 평점이 0인 영화도 있음


# 가중평점(Weighted Rating) = (v/(v+m)) * R + (m/(v+m)) * C
# v: 개별 영화에 평점을 투효한 횟수
# m: 평점을 부여하기 위한 최소 투표 횟수
# R: 개별 영화에 대한 평균 평점
# C: 전체 영화에 대한 평균 평점

# v = 'vote_count'
# R = 'vote_average'
# C = movies_df['vote_average'].mean()

# m = 값이 높으면 평점 투표 횟수가 많은 영화에 높은 가중평점을 부여.
# 상위 60%에 해당하는 횟수를 기준

C = movies_df['vote_average'].mean()
m = movies_df['vote_count'].quantile(0.6)

def weighted_vote_average(record):
    v = record['vote_count']
    R = record['vote_average']

    return ((v/(v+m)) * R) + ((m/(v+m)) * C)


movies_df['weighted_vote'] = movies.apply(weighted_vote_average, axis=1)


movies_df[['title', 'vote_average', 'weighted_vote', 'vote_count']].sort_values('weighted_vote', ascending=False)


def find_sim_movie(df, sorted_idx, title_name, top_list=10):
    title_movie = df[df['title'] == title_name]
    title_index = title_movie.index.values

    # 장르 유사성이 높은 영화 top_list의 2배수만큼 후보선정
    similar_index = sorted_idx[title_index, :(top_list*2)]
    similar_index = similar_index.reshape(-1)

    similar_index = similar_index[similar_index != title_index]  # 기존 영화 인덱스 제외

    return df.iloc[similar_index].sort_values('weighted_vote', ascending=False)[:top_list]


similar_movie = find_sim_movie(movies_df, genre_sim_sorted, 'The Godfather', 10)
similar_movie[['title', 'vote_average', 'weighted_vote']]
