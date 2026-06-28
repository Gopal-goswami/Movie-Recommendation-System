import requests
import mysql.connector
from db_config import get_db_connection,DB_PASSWORD,OMDB_API_KEY

def setup_and_populate_database(api_key=OMDB_API_KEY):
    # ─── STEP 1: FRESH DATABASE CREATE KARNA ───
    try:
        raw_conn = mysql.connector.connect(
            host='localhost',
            user="root",
            password=DB_PASSWORD # Aapka password lagaya hua hai
        )
        raw_cursor = raw_conn.cursor()
        raw_cursor.execute("CREATE DATABASE IF NOT EXISTS ott_recommendation_db;")
        raw_conn.commit()
        raw_cursor.close()
        raw_conn.close()
        print("📁 Database checked/created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
        return

    # ─── STEP 2: TABLES STRUCTURE SET UP ───
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")
    
    # Movies Table (💡 FIXED: Isme ab name aur video_url dono columns shuru se create honge)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        movie_id INT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        genre VARCHAR(100),
        poster_url TEXT,
        name VARCHAR(255),
        video_url VARCHAR(500)
    );
    """)
    
    # User Clicks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_clicks (
        click_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        movie_id INT,
        clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
    );
    """)
    conn.commit()
    print("📋 All tables structured perfectly with new columns.")

    # ─── STEP 3: MOVIE CATALOG INJECTION (Bina LightFM Ke) ───
    # Kyunki LightFM nahi chal raha, humne un 20 popular blockbuster filmon ki list direct bana di hai
    # Baaki ki 21 se 100 movies auto-loop se unique genres ke sath generate ho jayengi
    
    blockbuster_seed = [
        "Inception", "Interstellar", "The Dark Knight", "Avatar", "The Avengers",
        "Titanic", "Gladiator", "The Matrix", "Joker", "Spider-Man",
        "Iron Man", "Shutter Island", "The Notebook", "Jurassic Park", "Pushpa",
        "RRR", "KGF", "Bahubali", "Dangal", "3 Idiots"
    ]
    
    print("⏳ Fetching live metadata from OMDB API and inserting movies...")
    
    # Top 20 Real blockbusters processing
    for idx, movie_name in enumerate(blockbuster_seed):
        movie_id = idx + 1 # ID 1 se shuru hogi, 0 se nahi
        api_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
        
        try:
            response = requests.get(api_url).json()
            poster_url = response.get('Poster', 'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=500')
            genres = response.get('Genre', 'Action').split(',')[0] # Pehla primary genre pick karna
            if poster_url == 'N/A' or not poster_url:
                poster_url = 'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=500'
        except Exception:
            poster_url = 'https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=500'
            genres = 'General'
            
        # Live YouTube universal embed stream URL for top movies
        video_url = 'https://www.youtube.com/watch?v=aqz-KE-bpKQ'
        
        cursor.execute("""
            INSERT INTO movies (movie_id, title, genre, poster_url, name, video_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=%s, genre=%s, poster_url=%s, name=%s, video_url=%s
        """, (movie_id, movie_name, genres, poster_url, movie_name, video_url, 
              movie_name, genres, poster_url, movie_name, video_url))

    # Baaki bachi (21 se 100) movies ko auto-load karna different genres ke sath
    for i in range(21, 101):
        g_list = ['Action', 'Sci-Fi', 'Comedy', 'Drama']
        current_genre = g_list[i % 4]
        dummy_title = f"Movie_{i}"
        dummy_name = f"Blockbuster Hits Volume {i}"
        dummy_poster = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500"
        universal_video = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
        
        cursor.execute("""
            INSERT INTO movies (movie_id, title, genre, poster_url, name, video_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=%s, genre=%s, poster_url=%s, name=%s, video_url=%s
        """, (i, dummy_title, current_genre, dummy_poster, dummy_name, universal_video,
              dummy_title, current_genre, dummy_poster, dummy_name, universal_video))

    conn.commit()
    
    # Total check verification log
    cursor.execute("SELECT COUNT(*) FROM movies;")
    total = cursor.fetchone()[0]
    print(f"🎉 SUCCESS! Total {total} movies perfectly synchronized in Database.")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    setup_and_populate_database()