from dotenv import load_dotenv
import os
import json
import psycopg2


base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
article_json_file_path = os.path.join(base_directory,'data','processed','luat_hinh_su_metadata.json')
chunk_embedding_json_file_path = os.path.join(base_directory,'data','processed','chunks_embed.json')
dotenv_path = os.path.join(base_directory,'.env')  
load_dotenv(dotenv_path=dotenv_path)

# database config
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
name = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')


# get article infos
with open(article_json_file_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# get chunks embeddings
with open(chunk_embedding_json_file_path, 'r', encoding='utf-8') as f:
    chunk_embeddings = json.load(f)

# connect to database
conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=name,
    user=user,
    password=password
)

# func to insert a article to db
def insert_article(article):
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("insert into articles (article_id,article_name,full_content) values (%s,%s,%s)",[article['id'],article['title'],article['content']])

# func to insert chunk to db
def insert_chunk(article_id, chunk):
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("insert into chunk (article_id,chunk_content,embedding) values (%s,%s,%s)",[article_id,chunk,chunk_embeddings[chunk]])


# insert articles to db
for article in metadata:
    insert_article(article)

# insert chunks to db
for article in metadata:
    for chunk in article['chunks']:
        insert_chunk(article['id'], chunk)

conn.close()