import psycopg2
import json
class GraphLookUp:
    def __init__(self,filepath):
        self.filepath = filepath # file path for related_article.json

    # get all related article ids given an article_id return as a list of article ids
    def getAllRelatedArticleId(self,article_id):
        res=[]
        q=[]
        visited = [0]*500
        with open(self.filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        visited[article_id]=1
        q.append(article_id)
        while len(q)!=0:
            current = q.pop(0)
            for i in metadata[str(current)]:
                if visited[i]==0:
                    q.append(i)
                    res.append(i)
                    visited[i]=1
        return res