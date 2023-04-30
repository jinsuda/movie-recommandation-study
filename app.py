import pickle
import streamlit as st
from tmdbv3api import Movie, TMDb

movie = Movie()
tmdb = TMDb()
tmdb.api_key = '7a1258842909fa315bd1a319017098ca'
tmdb.language = 'ko-KR'


def get_recommendations(title):
    # 영화 제목을 통해서 전체 데이터 기준 그 영화의 index 값을 얻기
    idx = movies[movies['title'] == title].index[0]

    # 코사인 유사도 매트릭스 (cosine_sim) 에서 idx 에 해당하는 데이터를 (idx, 유사도) 형태로 얻기
    sim_scores = list(enumerate(cosine_sim[idx]))

    # 코사인 유사도 기준으로 내림차순 정렬
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 자기 자신을 제외한 10개의 추천 영화를 추출
    sim_scores = sim_scores[1:11]

    # 추천 영화 목록 10개의 인덱스 정보 추출
    movie_indices = [i[0] for i in sim_scores]

    # 인덱스 정보를 통해 영화 제목 추출
    images = []
    titles = []
    for i in movie_indices:
        id = movies['id'].iloc[i]
        # tmdb 라이브러리에서 movie.details 로 api 데이터 받아오기
        details = movie.details(id)

        # 포스터 파일이 없는 경우 제외 시키기
        image_path = details['poster_path']
        if image_path:
            image_path = 'https://image.tmdb.org/t/p/w500' + image_path
        else:
            image_path = 'no_image.jpg'

        images.append(image_path)
        # images.append('https://image.tmdb.org/t/p/w500' + details['poster_path'])

        titles.append(details['title'])

    return images, titles


movies = pickle.load(open('movies.pickle', 'rb'))
cosine_sim = pickle.load(open('cosine_sim.pickle', 'rb'))

st.set_page_config(layout='wide')
st.header('영화 추천')

movie_list = movies['title'].values
title = st.selectbox('영화를 선택해주세요', movie_list)
if st.button('Recommand'):
    with st.spinner('Please wait..'):
        images, titles = get_recommendations(title)


# 영화목록 10개 2줄로 5개씩 보여주는 코드
    # 처음데이터는 인덱스0 으로 초기화
    idx = 0
    for i in range(0, 2):
        cols = st.columns(5)
        for col in cols:
            col.image(images[idx])
            col.write(titles[idx])
            idx += 1
