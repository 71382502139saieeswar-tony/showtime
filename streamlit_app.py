import streamlit as st
import sqlite3
import json
import os
import datetime
import random

# Set page config with custom title, favicon & wide layout
st.set_page_config(
    page_title="ShowTime - Movie Tickets & Entertainment",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "showtime.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure DB initialized & seeded if missing
if not os.path.exists(DB_PATH):
    from seed_data import seed_all
    seed_all()

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "booking_step" not in st.session_state:
    st.session_state.booking_step = "catalog" # catalog, detail, showtimes, seats, fnb, payment, ticket
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "selected_showtime" not in st.session_state:
    st.session_state.selected_showtime = None
if "selected_seats" not in st.session_state:
    st.session_state.selected_seats = []
if "selected_fnb" not in st.session_state:
    st.session_state.selected_fnb = {}
if "last_booking" not in st.session_state:
    st.session_state.last_booking = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your ShowTime AI Movie Assistant. Ask me for recommendations or trending movies!"}
    ]

# Custom Modern Glassmorphic CSS Styling
st.markdown("""
<style>
    /* Global Styling */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 40%, #090d16 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Gradient Banner */
    .showtime-header {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.9) 0%, rgba(168, 85, 247, 0.9) 100%);
        padding: 1.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(244, 63, 94, 0.3);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .showtime-title {
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: -1px;
        color: #ffffff;
        margin: 0;
    }

    /* Movie Cards */
    .movie-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1.5rem;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(244, 63, 94, 0.25);
        border-color: rgba(244, 63, 94, 0.5);
    }
    
    /* Cast Avatar Circles */
    .cast-img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #f43f5e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    /* Ticket Card Styling */
    .ticket-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px dashed #f43f5e;
        border-radius: 24px;
        padding: 2rem;
        color: #fff;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }

    /* Streamlit Buttons Override */
    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def fetch_cities():
    conn = get_db_connection()
    cities = conn.execute("SELECT * FROM cities").fetchall()
    conn.close()
    return cities

def fetch_movies(city_id=1, search="", language="All", genre="All"):
    conn = get_db_connection()
    query = "SELECT * FROM movies WHERE 1=1"
    params = []
    if search:
        query += " AND (title LIKE ? OR genre LIKE ? OR director LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if language != "All":
        query += " AND language LIKE ?"
        params.append(f"%{language}%")
    if genre != "All":
        query += " AND genre LIKE ?"
        params.append(f"%{genre}%")
    
    movies = conn.execute(query, params).fetchall()
    conn.close()
    return movies

def fetch_showtimes(movie_id, city_id=1, date_str=None):
    conn = get_db_connection()
    if not date_str:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    
    query = """
    SELECT st.id as showtime_id, st.time, st.format, st.price_recliner, st.price_prime, st.price_classic,
           c.name as cinema_name, c.address as cinema_address, c.facilities_json
    FROM showtimes st
    JOIN cinemas c ON st.cinema_id = c.id
    WHERE st.movie_id = ? AND st.date = ?
    """
    showtimes = conn.execute(query, (movie_id, date_str)).fetchall()
    conn.close()
    return showtimes

def fetch_seats(showtime_id):
    conn = get_db_connection()
    seats = conn.execute("SELECT * FROM seats WHERE showtime_id = ?", (showtime_id,)).fetchall()
    conn.close()
    return seats

# --- SIDEBAR & USER AUTH --- #
with st.sidebar:
    st.image("https://img.icons8.com/color/96/movie-projector.png", width=70)
    st.title("🍿 ShowTime Navigation")

    # City Selector
    cities = fetch_cities()
    city_names = [c["name"] for c in cities]
    selected_city_name = st.selectbox("📍 Select City", city_names, index=0)
    selected_city_id = next((c["id"] for c in cities if c["name"] == selected_city_name), 1)

    st.divider()

    # User Auth Section
    st.subheader("👤 User Account")
    if st.session_state.user:
        st.success(f"Logged in as **{st.session_state.user['name']}**")
        st.caption(f"Email: {st.session_state.user['email']}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        auth_mode = st.radio("Account Mode", ["Sign In", "Create Account"], horizontal=True)
        auth_email = st.text_input("Email", value="user@showtime.com", key="auth_email_input")
        auth_pass = st.text_input("Password", value="••••••••", type="password", key="auth_pass_input")
        
        if auth_mode == "Create Account":
            auth_name = st.text_input("Full Name", value="Alex Johnson")
        
        if st.button("🔐 Proceed", use_container_width=True):
            user_name = auth_name if auth_mode == "Create Account" else auth_email.split("@")[0].capitalize()
            st.session_state.user = {"name": user_name, "email": auth_email}
            st.toast(f"Welcome back, {user_name}!", icon="✨")
            st.rerun()

    st.divider()
    
    # Filter Controls
    st.subheader("🔍 Filter Movies")
    filter_lang = st.selectbox("Language", ["All", "Tamil", "Telugu", "Hindi", "English"])
    filter_genre = st.selectbox("Genre", ["All", "Action", "Comedy", "Sci-Fi", "Horror", "Drama", "Crime"])
    search_query = st.text_input("🔎 Search Title/Director", placeholder="Type movie name...")

# --- MAIN APP BODY --- #

# Header Banner
st.markdown("""
<div class="showtime-header">
    <div>
        <h1 class="showtime-title">🎬 ShowTime</h1>
        <p style="margin:0; opacity:0.9; font-weight:500;">Book Movie Tickets • Real Cast & Crew • Live Seating Matrix</p>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 12px; font-weight:700;">
            🔥 Trending Movies 2026
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# NAVIGATION STEPS LOGIC
if st.session_state.booking_step == "catalog":
    # Trending Hero Banner
    trending_movies = fetch_movies(city_id=selected_city_id)
    
    if trending_movies:
        featured = trending_movies[0]
        col_banner1, col_banner2 = st.columns([1, 2.5])
        with col_banner1:
            st.image(featured["poster_url"], use_container_width=True)
        with col_banner2:
            st.badge(f"🔥 TRENDING BLOCKBUSTER • {featured['certificate']}")
            st.title(featured["title"])
            st.markdown(f"**Language:** {featured['language']} | **Duration:** {featured['duration_mins']} mins")
            st.markdown(f"⭐ **{featured['rating_percentage']}% Rating** ({(featured['rating_count']/1000):.0f}K votes)")
            st.write(featured["synopsis"])
            if st.button("🎟️ Book Now for " + featured["title"], type="primary"):
                st.session_state.selected_movie = dict(featured)
                st.session_state.booking_step = "detail"
                st.rerun()

    st.divider()

    # Movies Catalog Grid
    st.subheader(f"🍿 Movies in {selected_city_name}")
    movies = fetch_movies(city_id=selected_city_id, search=search_query, language=filter_lang, genre=filter_genre)

    if not movies:
        st.info("No movies match your selected filters.")
    else:
        cols = st.columns(3)
        for idx, m in enumerate(movies):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{m['poster_url']}" style="width:100%; height:320px; object-fit:cover; border-radius:14px; margin-bottom:0.75rem;">
                    <h3 style="margin:0 0 0.25rem 0; font-size:1.2rem; font-weight:800;">{m['title']}</h3>
                    <p style="color: #94a3b8; font-size:0.85rem; margin-bottom:0.5rem;">{m['certificate']} • {m['language'].split(',')[0]} • <span style="color:#f59e0b;">{m['genre'].split(',')[0]}</span></p>
                    <p style="font-weight:700; color:#4ade80;">⭐ {m['rating_percentage']}% Rating</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Book Tickets", key=f"btn_book_{m['id']}", type="primary", use_container_width=True):
                    st.session_state.selected_movie = dict(m)
                    st.session_state.booking_step = "detail"
                    st.rerun()

elif st.session_state.booking_step == "detail":
    m = st.session_state.selected_movie
    if st.button("⬅️ Back to Catalog"):
        st.session_state.booking_step = "catalog"
        st.rerun()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(m["poster_url"], use_container_width=True)
        st.caption(f"Director: {m['director']}")
        st.caption(f"Release Date: {m['release_date']}")
    
    with col2:
        st.title(m["title"])
        st.markdown(f"**Language:** {m['language']} | **Certificate:** {m['certificate']} | **Duration:** {m['duration_mins']} mins")
        st.markdown(f"⭐ **{m['rating_percentage']}% User Rating** ({(m['rating_count']/1000):.0f}K votes)")
        
        st.subheader("About the Movie")
        st.write(m["synopsis"])
        
        st.subheader("🎬 Official Cast & Crew")
        cast_list = json.loads(m["cast_json"])
        
        # Display cast headshots
        cast_cols = st.columns(min(5, len(cast_list)))
        for c_idx, c in enumerate(cast_list[:5]):
            with cast_cols[c_idx]:
                st.markdown(f"""
                <div style="text-align:center;">
                    <img src="{c['avatar']}" class="cast-img" onerror="this.src='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';"><br>
                    <strong style="font-size:0.85rem;">{c['name']}</strong><br>
                    <span style="font-size:0.75rem; color:#94a3b8;">{c['role']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📺 Watch Trailer")
        st.video(m["trailer_url"])
        
        st.divider()
        if st.button("🎟️ Proceed to Showtimes & Cinema Selection", type="primary", use_container_width=True):
            st.session_state.booking_step = "showtimes"
            st.rerun()

elif st.session_state.booking_step == "showtimes":
    m = st.session_state.selected_movie
    if st.button("⬅️ Back to Movie Detail"):
        st.session_state.booking_step = "detail"
        st.rerun()

    st.title(f"Select Cinema & Showtime for {m['title']}")
    
    selected_date = st.date_input("📅 Date", datetime.date.today())
    date_str = selected_date.strftime("%Y-%m-%d")

    showtimes = fetch_showtimes(m["id"], city_id=selected_city_id, date_str=date_str)
    
    if not showtimes:
        st.warning("No showtimes found for selected date. Please pick another date.")
    else:
        for st_item in showtimes:
            with st.container():
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding:1rem; border-radius:14px; margin-bottom:1rem; border:1px solid rgba(255,255,255,0.08);">
                    <h4 style="margin:0; color:#f43f5e;">🏛️ {st_item['cinema_name']}</h4>
                    <p style="margin:0 0 0.5rem 0; color:#94a3b8; font-size:0.85rem;">{st_item['cinema_address']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_t1, col_t2 = st.columns([1, 4])
                with col_t1:
                    st.write(f"Format: **{st_item['format']}**")
                with col_t2:
                    if st.button(f"⏰ {st_item['time']} ({st_item['format']})", key=f"st_{st_item['showtime_id']}", type="primary"):
                        st.session_state.selected_showtime = dict(st_item)
                        st.session_state.booking_step = "seats"
                        st.rerun()

elif st.session_state.booking_step == "seats":
    st_item = st.session_state.selected_showtime
    m = st.session_state.selected_movie
    
    if st.button("⬅️ Back to Showtimes"):
        st.session_state.booking_step = "showtimes"
        st.rerun()

    st.title(f"🎟️ Pick Seats - {m['title']}")
    st.caption(f"{st_item['cinema_name']} | {st_item['time']} ({st_item['format']})")

    seats = fetch_seats(st_item["showtime_id"])
    
    st.info("Screen is this way 👇")
    st.markdown("""<div style="height:6px; background:linear-gradient(90deg, #f43f5e, #38bdf8); border-radius:4px; margin-bottom:2rem;"></div>""", unsafe_allow_html=True)

    # Smart Auto Picker
    st.subheader("⚡ Quick Seat Auto Picker")
    auto_count = st.slider("Number of Seats", 1, 6, 2)
    
    # Organize seats by row
    rows = {}
    for s in seats:
        row = s["row_label"]
        if row not in rows:
            rows[row] = []
        rows[row].append(s)

    st.subheader("Seat Matrix")
    selected_codes = []
    
    for row_label, row_seats in rows.items():
        st.write(f"**Row {row_label}** ({row_seats[0]['tier']} - ₹{row_seats[0]['price']})")
        cols = st.columns(len(row_seats))
        for idx, s_obj in enumerate(row_seats):
            with cols[idx]:
                is_reserved = s_obj["status"] in ["RESERVED", "BOOKED"]
                seat_label = f"{s_obj['seat_number']}"
                if is_reserved:
                    st.button(seat_label, key=f"seat_{s_obj['id']}", disabled=True)
                else:
                    if st.checkbox(seat_label, key=f"chk_{s_obj['id']}"):
                        selected_codes.append(dict(s_obj))

    st.divider()
    if selected_codes:
        st.success(f"Selected {len(selected_codes)} Seats: " + ", ".join([s['seat_code'] for s in selected_codes]))
        total_seat_price = sum(s['price'] for s in selected_codes)
        st.markdown(f"**Total Seats Price:** ₹{total_seat_price:.2f}")

        if st.button("🍿 Proceed to Snacks & Checkout", type="primary", use_container_width=True):
            st.session_state.selected_seats = selected_codes
            st.session_state.booking_step = "payment"
            st.rerun()
    else:
        st.warning("Please select at least 1 seat to continue.")

elif st.session_state.booking_step == "payment":
    m = st.session_state.selected_movie
    st_item = st.session_state.selected_showtime
    seats = st.session_state.selected_seats

    if st.button("⬅️ Back to Seat Selection"):
        st.session_state.booking_step = "seats"
        st.rerun()

    st.title("💳 Booking Checkout & Summary")

    col_pay1, col_pay2 = st.columns([1.5, 1])

    with col_pay1:
        st.subheader("Contact Information")
        user_name = st.text_input("Name", value=st.session_state.user["name"] if st.session_state.user else "Rahul Sharma")
        user_email = st.text_input("Email Address", value=st.session_state.user["email"] if st.session_state.user else "rahul@example.com")
        user_phone = st.text_input("Phone Number", value="9876543210")

        st.subheader("Discount Promos")
        promo_code = st.text_input("Promo Code", value="SHOWTIME20", placeholder="e.g. SHOWTIME20")
        discount = 0.0
        if promo_code.upper() == "SHOWTIME20":
            discount = 150.0
            st.success("🎉 Promo Code SHOWTIME20 Applied! ₹150 OFF")

    with col_pay2:
        st.markdown(f"""
        <div class="ticket-card">
            <h3>🎟️ Ticket Summary</h3>
            <p><strong>{m['title']}</strong> ({st_item['format']})</p>
            <p style="color:#94a3b8;">{st_item['cinema_name']}</p>
            <hr style="border-color:rgba(255,255,255,0.1);">
            <p>Seats: <strong style="color:#f43f5e;">{', '.join([s['seat_code'] for s in seats])}</strong></p>
            <p>Tickets Subtotal: ₹{sum(s['price'] for s in seats):.2f}</p>
            <p>Convenience Fee: ₹{(35.0 * len(seats) * 1.18):.2f}</p>
            <p>Discount: -₹{discount:.2f}</p>
            <hr style="border-color:rgba(255,255,255,0.1);">
            <h2 style="color:#4ade80;">Total Payable: ₹{max(0, sum(s['price'] for s in seats) + (35.0 * len(seats) * 1.18) - discount):.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("🚀 Pay & Generate Digital E-Ticket", type="primary", use_container_width=True):
            booking_id = f"ST-{random.randint(100000, 999999)}"
            st.session_state.last_booking = {
                "booking_id": booking_id,
                "movie_title": m["title"],
                "cinema_name": st_item["cinema_name"],
                "cinema_address": st_item["cinema_address"],
                "time": st_item["time"],
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "format": st_item["format"],
                "seats": [s["seat_code"] for s in seats],
                "poster_url": m["poster_url"],
                "total_amount": max(0, sum(s["price"] for s in seats) + (35.0 * len(seats) * 1.18) - discount)
            }
            st.session_state.booking_step = "ticket"
            st.rerun()

elif st.session_state.booking_step == "ticket":
    tb = st.session_state.last_booking
    st.balloons()
    st.title("🎉 Booking Confirmed!")
    
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        st.image(tb["poster_url"], use_container_width=True)
    with col_t2:
        st.markdown(f"""
        <div class="ticket-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#f43f5e;">ShowTime E-Ticket</h2>
                <span style="background:#22c55e; color:#fff; padding:0.25rem 0.75rem; border-radius:12px; font-weight:700;">CONFIRMED</span>
            </div>
            <hr>
            <h3>{tb['movie_title']} ({tb['format']})</h3>
            <p>🏛️ <strong>{tb['cinema_name']}</strong></p>
            <p>📍 {tb['cinema_address']}</p>
            <p>📅 Date: <strong>{tb['date']}</strong> | ⏰ Time: <strong>{tb['time']}</strong></p>
            <h2 style="color:#38bdf8;">BOOKING ID: {tb['booking_id']}</h2>
            <h3>SEATS: <span style="color:#f43f5e;">{', '.join(tb['seats'])}</span></h3>
            <hr>
            <h4>Total Paid: ₹{tb['total_amount']:.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button("🏠 Return to Homepage"):
        st.session_state.booking_step = "catalog"
        st.rerun()

# --- AI ASSISTANT CHATBOT IN SIDEBAR / BOTTOM --- #
with st.expander("🤖 ShowTime AI Assistant (Ask for Recommendations)"):
    for msg in st.session_state.chat_messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    if user_prompt := st.chat_input("Ask AI: Recommend a blockbuster action movie..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        st.chat_message("user").write(user_prompt)
        
        reply = "🍿 I recommend watching **Leo** starring Thalapathy Vijay or **Pushpa 2** starring Allu Arjun! Both are trending high-octane blockbusters!"
        if "funny" in user_prompt.lower() or "comedy" in user_prompt.lower():
            reply = "😂 For comedy, you MUST check out **Love Today** directed by & starring Pradeep Ranganathan, or **Stree 2** starring Rajkummar Rao!"
        
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
