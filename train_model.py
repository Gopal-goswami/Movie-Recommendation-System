import mysql.connector
from db_config import get_db_connection
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

def train_and_save_model():
    print("🔄 Connecting to Database to fetch user interactions...")
    conn = get_db_connection()
    
    # 1. User Clicks (Interactions) Fetch Karna
    query_clicks = "SELECT user_id, movie_id FROM user_clicks"
    df_clicks = pd.read_sql(query_clicks, conn)
    
    # 2. Saari Movies Fetch Karna (Taaki empty matrix handle ho sake)
    query_movies = "SELECT movie_id FROM movies"
    df_movies = pd.read_sql(query_movies, conn)
    
    conn.close()
    
    if df_clicks.empty:
        print("⚠️ Warning: Database mein interactions nahi hain!")
        return

    # Hum har click ko 1 score (interaction indicator) maan lete hain
    df_clicks['interaction'] = 1
    
    print(f"📊 Found {df_clicks['user_id'].nunique()} active users and {len(df_clicks)} interactions.")

    # 3. Pivot Table Banana (User-Item Matrix)
    # Rows = Users, Columns = Movie IDs
    user_movie_matrix = df_clicks.pivot_table(
        index='user_id', 
        columns='movie_id', 
        values='interaction', 
        fill_value=0
    )
    
    # ensure saari database wali movies matrix columns mein hon
    for m_id in df_movies['movie_id']:
        if m_id not in user_movie_matrix.columns:
            user_movie_matrix[m_id] = 0
            
    # Columns ko sort kar lete hain taaki sequence sahi rahe
    user_movie_matrix = user_movie_matrix.reindex(columns=sorted(user_movie_matrix.columns))

    print("🤖 Calculating Cosine Similarity Matrix...")
    # Movies ke beech ki similarity nikalne ke liye matrix ko transpose (.T) karke similarity nikalenge
    movie_similarity = cosine_similarity(user_movie_matrix.T)
    
    # DataFrame mein convert karna taaki easy lookup ho sake
    movie_similarity_df = pd.DataFrame(
        movie_similarity, 
        index=user_movie_matrix.columns, 
        columns=user_movie_matrix.columns
    )

    print("💾 Files save ho rahi hain...")
    
    # Bina kisi folder ke, direct main folder mein save hoga
    # Hum matrix aur user history dono ko save karenge taaki backend use kar sake
    with open('user_movie_matrix.pkl', 'wb') as f:
        pickle.dump(user_movie_matrix, f)
        
    with open('movie_similarity.pkl', 'wb') as f:
        pickle.dump(movie_similarity_df, f)
        
    print("🎉 Done! 'user_movie_matrix.pkl' aur 'movie_similarity.pkl' direct aapke main folder mein save ho gayi hain!")

if __name__ == "__main__":
    train_and_save_model()