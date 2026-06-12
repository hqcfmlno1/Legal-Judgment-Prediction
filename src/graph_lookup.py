import psycopg2
import json
class GraphLookUp:
    def __init__(self,filepath):
        self.filepath = filepath # file path for related_article.json

    # get all related article ids given an article_id return as a list of article ids
    def getAllRelatedArticleId(self,article_id):
        res=[]
        q=[]
        visited = set()
        with open(self.filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        visited.add(article_id)
        q.append(article_id)
        while len(q)!=0:
            current = q.pop(0)
            related = metadata.get(str(current), [])
            for i in related:
                if i not in visited:
                    q.append(i)
                    res.append(i)
                    visited.add(i)
        return res