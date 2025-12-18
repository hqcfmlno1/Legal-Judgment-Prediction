import psycopg2

class LegalPostgresDb:
    def __init__(self, host, port, dbname, user, password):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
    def top_similar_articles(self, input_reformated_text, input_embedding, limit=30, threshold=0.8):
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    -- rank bm25
                    with rank_in_chunk as(
                    select article_id, ts_rank(tsv,websearch_to_tsquery('simple',%s)) as ts_rank_score
                    from chunk
                    where tsv @@ websearch_to_tsquery('simple',%s)
                    order by ts_rank_score desc
                    limit 200
                    ),
                    final_rank_bm25_cal as(
                    select article_id,max(ts_rank_score) as final_rank_score
                    from rank_in_chunk
                    group by article_id
                    order by final_rank_score desc
                    ),
                    final_rank_bm25 as(
                    select final_rank_bm25_cal.*, 
                    RANK() OVER (ORDER BY final_rank_score DESC) AS rank
                    from final_rank_bm25_cal
                    ),
                    -- rank distance cosine
                    cosine_distance_cal_chunk as(
                    select article_id, (%s::vector <=> c.embedding ) as cosine_distance 
                    from chunk c 
                    where (%s::vector <=> c.embedding )<=%s
                    order by cosine_distance
                    limit 200
                    ),
                    final_cosine_distance_cal_article as(
                    select article_id, min(cosine_distance) as final_cosine_distance_article
                    from cosine_distance_cal_chunk
                    group by article_id
                    order by final_cosine_distance_article asc
                    ),
                    final_rank_cosine_distance as(
                    select final_cosine_distance_cal_article.*,
                    RANK() OVER (ORDER BY final_cosine_distance_article asc) AS rank
                    from final_cosine_distance_cal_article
                    )
                    select coalesce(bm25.article_id,cos.article_id) from final_rank_bm25 bm25 full outer join final_rank_cosine_distance cos
                    using (article_id)
                    order by coalesce(1.0/(60+bm25.rank),0)::numeric + coalesce(1.0/(60+cos.rank),0)::numeric desc
                    limit %s;
                    """,
                    (input_reformated_text, input_reformated_text, input_embedding, input_embedding, threshold, limit))
                rows = cursor.fetchall()
        return rows

    def find_article_content(self, article_id_list):
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    select concat(article_name,' ',full_content) from articles where article_id in %s
                    """,
                    (tuple(article_id_list),))
                rows = cursor.fetchall()
                article_contents = [item[0] for item in rows]
        return article_contents