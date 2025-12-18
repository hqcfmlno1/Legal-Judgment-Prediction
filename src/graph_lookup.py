import psycopg2
import json
class GraphLookUp:
    def __init__(self, host, port, dbname, user, password, filepath):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        self.filepath = filepath # file path for related_article.json


    # get all related articles give a list of article ids
    def getRelatedArticle(self,article_id_list):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        all_related_article_list = [item2 for item1 in article_id_list for item2 in metadata[str(item1)]]
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    select concat('Điều ',article_id,' ',full_content) from articles where article_id in %s;
                    """,
                    (tuple(all_related_article_list),))
                rows = cursor.fetchall()
        return rows