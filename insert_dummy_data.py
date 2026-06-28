import mysql.connector
from db_config import get_db_connection
import random

def insert_dummy_users_and_clicks():
    print("🔄 Connecting to MySQL to insert dummy data...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Database se existing movie IDs uthana taaki unhi par clicks generate hon
        cursor.execute("SELECT movie_id FROM movies")
        movie_rows = cursor.fetchall()
        movie_ids = [row[0] for row in movie_rows]

        if not movie_ids:
            print("❌ Error: Pehle apni movies table mein data bhariyet (database_setup.py chalakar)!")
            return

        # 2. Dummy Users insert karna (Maano hum 10 users bana rahe hain: User_1 se User_10)
        print("👥 Creating 10 dummy users...")
        users_data = []
        for i in range(1, 11):
            user_id = f"User_{i}"
            # IGNORE use kar rahe hain taaki agar user pehle se ho toh code crash na kare
            users_data.append((user_id,))
        
        cursor.executemany("INSERT IGNORE INTO users (user_id) VALUES (%s)", users_data)
        conn.commit()

        # 3. Dummy Clicks/Interactions insert karna
        # Har user ke liye hum 5 se 10 random movies ke clicks generate karenge
        print("🖱️ Generating random movie clicks for users...")
        click_data = []
        for i in range(1, 11):
            user_id = f"User_{i}"
            # Har user ke liye random 5-10 unique movies select karna
            num_clicks = random.randint(5, 10)
            chosen_movies = random.sample(movie_ids, min(num_clicks, len(movie_ids)))
            
            for movie_id in chosen_movies:
                click_data.append((user_id, movie_id))

        cursor.executemany("INSERT IGNORE INTO user_clicks (user_id, movie_id) VALUES (%s, %s)", click_data)
        conn.commit()

        print("✨ Success! Dummy users aur unke clicks successfully database mein store ho gaye hain.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    insert_dummy_users_and_clicks()