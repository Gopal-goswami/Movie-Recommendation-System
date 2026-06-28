from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import mysql.connector
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from db_config import DB_PASSWORD

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PASSWORD, 
        database="ott_recommendation_db"
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Backend Synced perfectly with frontend triggers.")
    yield

app = FastAPI(title="OTT Recommendation System", lifespan=lifespan)

@app.get("/recommend")
def get_recommendations(user_id: int, current_movie_id: int = None):
    try:
        conn = get_db_connection()
        query_movies = "SELECT movie_id, title, genre, poster_url, name, video_url FROM movies"
        df_movies = pd.read_sql(query_movies, conn)
        movies_dict = {m['movie_id']: m for m in df_movies.to_dict(orient='records')}
        
        query_clicks = "SELECT user_id, movie_id FROM user_clicks"
        df_clicks = pd.read_sql(query_clicks, conn)
        conn.close()

        # 🔥 MATRIX ENGINE: Agar koi history nahi hai, toh current movie ke genre se milti julti movies do (No more Harry Potter loop!)
        if df_clicks.empty or current_movie_id:
            if current_movie_id and current_movie_id in movies_dict:
                ref_genre = movies_dict[current_movie_id]['genre']
                same_genre_movies = [m for m in movies_dict.values() if m['genre'] == ref_genre and m['movie_id'] != current_movie_id]
                if len(same_genre_movies) >= 5:
                    return {"user_id": user_id, "recommendations": same_genre_movies[:5], "type": "genre_fallback"}

        user_clicks_live = df_clicks[df_clicks['user_id'] == user_id]['movie_id'].tolist()
        
        if not user_clicks_live:
            return {"user_id": user_id, "recommendations": list(movies_dict.values())[:5], "type": "fallback"}

        df_clicks['interaction'] = 1
        user_movie_matrix = df_clicks.pivot_table(index='user_id', columns='movie_id', values='interaction', fill_value=0)
        
        for m_id in movies_dict.keys():
            if m_id not in user_movie_matrix.columns:
                user_movie_matrix[m_id] = 0
        user_movie_matrix = user_movie_matrix.reindex(columns=sorted(user_movie_matrix.columns))

        movie_similarity = cosine_similarity(user_movie_matrix.T)
        movie_similarity_df = pd.DataFrame(movie_similarity, index=user_movie_matrix.columns, columns=user_movie_matrix.columns)

        similar_scores = movie_similarity_df[user_clicks_live].sum(axis=1)
        similar_scores = similar_scores.drop(user_clicks_live, errors='ignore')
        if current_movie_id:
            similar_scores = similar_scores.drop(current_movie_id, errors='ignore')
            
        top_movie_ids = similar_scores.sort_values(ascending=False).head(5).index.tolist()
        
        recommendations = [movies_dict[m_id] for m_id in top_movie_ids if m_id in movies_dict]
        
        # Padding safety fill
        for m_id, m_data in movies_dict.items():
            if len(recommendations) >= 5: break
            if m_id not in user_clicks_live and m_id != current_movie_id and m_data not in recommendations:
                recommendations.append(m_data)
                
        return {"user_id": user_id, "recommendations": recommendations[:5], "type": "live_matrix"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))