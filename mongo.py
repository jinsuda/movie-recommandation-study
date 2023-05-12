from pymongo import MongoClient
import csv

# MongoDB에 연결
client = MongoClient("mongodb+srv://admin:1q2w3e4r@cluster0.yvz01u3.mongodb.net/?retryWrites=true&w=majority")

# 데이터베이스 선택 (없는 경우 생성됨)
db = client['Movie']

# 컬렉션 선택 (없는 경우 생성됨)
collection = db['movieInfo']

# CSV 파일 경로
csv_file = 'tmdbData.csv'

# CSV 파일 열기
with open(csv_file, 'r',encoding='utf8') as file:
    reader = csv.DictReader(file)

    # 각 행에 대해 MongoDB에 삽입
    for row in reader:
       
        document = {
            'title': row['title'],
            #'field2': row['column2'],
            # 필요한 경우 추가 필드를 지정합니다
            
        }
        collection.insert_one(row)