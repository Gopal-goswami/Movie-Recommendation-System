import streamlit as st
import requests
import mysql.connector
import bcrypt
from db_config import DB_PASSWORD

st.set_page_config(page_title="OTT Stream Engine", layout="wide")
BACKEND_URL = "http://127.0.0.1:8000"

st.markdown(
    """
    <style>
    .stApp { background-color: #111217; color: #ffffff; }
    div.stButton > button:first-child { background-color: #E50914; color: white; border-radius: 6px; font-weight: bold; }
    div.stButton > button:first-child:hover { background-color: #ff1e28; }
    </style>
    """, unsafe_allow_html=True
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password=DB_PASSWORD, database="ott_recommendation_db"
    )

# ─── PERFECT RE-ROUTING STATES ───
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_id" not in st.session_state: st.session_state.user_id = None
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "active_movie" not in st.session_state: st.session_state.active_movie = None

def play_movie_and_switch_page(user_id, movie_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_clicks (user_id, movie_id, clicked_at) VALUES (%s, %s, NOW())", (user_id, movie_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e: print(f"DB Error: {e}")
    
    # ⚡ MAGIC TRICK: Bina URL chhede state badalna taaki login safe rahe
    st.session_state.active_movie = movie_id
    st.rerun()

def search_movies_from_db(query):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies WHERE name LIKE %s", (f"%{query}%",))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_movie_by_id(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res

# ====================================================================
# PHASE 1: LOGIN / SIGNUP GATEWAY
# ====================================================================
if not st.session_state.logged_in:
    st.title("🎬 Welcome to OTT Stream Hub")
    auth_mode = st.radio("Choose Gateway Mode", ["Login", "Signup"], horizontal=True)
    
    email = st.text_input("User Email Address", key="auth_email")
    password = st.text_input("Secure Password", type="password", key="auth_pass")
    
    if auth_mode == "Signup":
        if st.button("Register Account", use_container_width=True):
            if email and password:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                    if cursor.fetchone(): st.error("⚠️ Already registered!")
                    else:
                        salt = bcrypt.gensalt(rounds=12)
                        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                        cursor.execute("INSERT INTO users (email, password_hash, created_at) VALUES (%s, %s, NOW())", (email, hashed))
                        conn.commit()
                        st.success("🎉 Signup Done! Select 'Login' to enter.")
                    cursor.close()
                    conn.close()
                except Exception as e: st.error(f"Error: {e}")
                    
    elif auth_mode == "Login":
        test_bypass = st.checkbox("Developer Bypass Mode (Direct Sign In)")
        if test_bypass:
            dummy_id = st.number_input("Assign Active User ID", min_value=1, value=1)
            if st.button("Direct Inject Sign In", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_id = int(dummy_id)
                st.session_state.user_email = f"dev_user{dummy_id}@ott.local"
                st.rerun()
        else:
            if st.button("Secure Account Authentication", use_container_width=True):
                if email and password:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (email,))
                        user_record = cursor.fetchone()
                        if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record['password_hash'].encode('utf-8')):
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_record['user_id']
                            st.session_state.user_email = email
                            st.rerun()
                        else: st.error("❌ Auth Failed!")
                        cursor.close()
                        conn.close()
                    except Exception as e: st.error(f"Error: {e}")

# ====================================================================
# PHASE 2: CORE PLATFORM
# ====================================================================
else:
    st.sidebar.title("👤 Premium Profile")
    st.sidebar.write(f"📧 `{st.session_state.user_email}`")
    
    if st.sidebar.button("🏠 Browse Home", use_container_width=True):
        st.session_state.active_movie = None
        st.rerun()
        
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.active_movie = None
        st.rerun()

    # ─── VIEW A: PLAYER MODE ───
    if st.session_state.active_movie:
        active = get_movie_by_id(st.session_state.active_movie)
        if active:
            if st.button("⬅️ Back to Search"):
                st.session_state.active_movie = None
                st.rerun()
                
            st.title(f"📺 Now Streaming: {active['name']}")
            
            # 🔥 CRITICAL: Embed wrapper container lagaya taaki video badalne par widget reload ho ske
            with st.container():
                st.video(active['video_url'], autoplay=True)
                
            st.markdown(f"🎭 **Genre:** {active['genre']} | **ID:** `{active['movie_id']}`")
            st.write("---")
            st.subheader("👥 More Like This")
            
            try:
                response = requests.get(f"{BACKEND_URL}/recommend?user_id={st.session_state.user_id}&current_movie_id={active['movie_id']}")
                if response.status_code == 200:
                    recommendations = response.json().get("recommendations", [])
                    if recommendations:
                        cols = st.columns(5)
                        for idx, rec_movie in enumerate(recommendations[:5]):
                            with cols[idx]:
                                st.image(rec_movie['poster_url'], use_container_width=True)
                                st.markdown(f"**{rec_movie['name']}**")
                                # 🔥 BUTTON TRICK: Session dynamic mapping key binded
                                if st.button("🍿 Watch", key=f"rec_v2_{rec_movie['movie_id']}_{idx}"):
                                    play_movie_and_switch_page(st.session_state.user_id, rec_movie['movie_id'])
            except Exception as e:
                st.error(f"🔌 Backend Offline: {e}")

    # ─── VIEW B: CATALOG BROWSE MODE ───
    else:
        st.title("🍿 Discover Blockbuster Catalog")
        search_query = st.text_input("Search movie name...", placeholder="Type name (e.g. RRR, KGF, Inception)...")
        
        if search_query:
            results = search_movies_from_db(search_query)
            if results:
                grid_cols = st.columns(3)
                for idx, movie in enumerate(results):
                    with grid_cols[idx % 3]:
                        st.image(movie['poster_url'], use_container_width=True)
                        st.markdown(f"#### {movie['name']}")
                        st.caption(f"🎭 {movie['genre']}")
                        if st.button("▶️ Play Video", key=f"main_v2_{movie['movie_id']}"):
                            play_movie_and_switch_page(st.session_state.user_id, movie['movie_id'])
            else:
                st.warning("No movies found.")
        else:
            st.info("💡 Enter movie name to start streaming.")