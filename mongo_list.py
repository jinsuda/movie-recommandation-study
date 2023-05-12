## db에서 추천된 영화 목록을 가져와서 json형태로 가져오기
from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
client = MongoClient("mongodb+srv://admin:1q2w3e4r@cluster0.yvz01u3.mongodb.net/?retryWrites=true&w=majority")

# db = client.test_database
db = client['Movie'] # test-db라는 이름의 데이터베이스에 접속
movieInfo = db.movieInfo
movieInfo = db["movieInfo"]
movieInfo
# print(client.list_database_names('movieInfo'))

# for d in db['movieInfo'].find():
#     print(d['title'], d['genres'], d['vote_average'])

# 'author':'hun'인 데이터 조회
#print(db.posts.find_one({'author':'hun'})['text'])