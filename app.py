import os
import json
import uuid
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import get_db

app = FastAPI(
    title="ShowTime API",
    description="Master Class Backend API for ShowTime Movie & Event Ticket Booking Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class PromoValidateRequest(BaseModel):
    code: str
    amount: float

class SeatItem(BaseModel):
    seat_code: str
    tier: str
    price: float

class FnBItem(BaseModel):
    id: int
    name: str
    qty: int
    price: float

class BookingCreateRequest(BaseModel):
    showtime_id: int
    user_name: str
    user_email: str
    user_phone: str
    seats: List[SeatItem]
    fnb: List[FnBItem]
    promo_code: Optional[str] = None
    payment_method: str = "UPI"

class ReviewCreateRequest(BaseModel):
    movie_id: int
    user_name: str
    rating: int
    comment: str

class MovieCreateUpdateRequest(BaseModel):
    title: str
    language: str
    genre: str
    certificate: str
    duration_mins: int
    release_date: str
    rating_percentage: int
    rating_count: int
    likes_count: int
    synopsis: str
    director: str
    cast: List[dict]
    poster_url: str
    backdrop_url: str
    trailer_url: str
    formats: List[str]
    is_trending: bool = False

class PromoCreateRequest(BaseModel):
    code: str
    discount_percent: float = 0
    flat_discount: float = 0
    max_discount: float = 1000
    min_spend: float = 0

# Helper JSON parser
def parse_json_field(val, default=None):
    if not val:
        return default or []
    try:
        return json.loads(val)
    except Exception:
        return default or []

# ----------------- PUBLIC API ROUTES ----------------- #

@app.get("/api/cities")
def get_cities():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cities ORDER BY is_popular DESC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/movies")
def get_movies(
    city_id: Optional[int] = None,
    search: Optional[str] = None,
    language: Optional[str] = None,
    genre: Optional[str] = None,
    format: Optional[str] = None,
    trending_only: bool = False
):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM movies WHERE 1=1"
    params = []
    
    if trending_only:
        query += " AND is_trending = 1"
        
    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(genre) LIKE ? OR LOWER(cast_json) LIKE ?)"
        term = f"%{search.lower()}%"
        params.extend([term, term, term])
        
    if language and language != "All":
        query += " AND LOWER(language) LIKE ?"
        params.append(f"%{language.lower()}%")
        
    if genre and genre != "All":
        query += " AND LOWER(genre) LIKE ?"
        params.append(f"%{genre.lower()}%")

    query += " ORDER BY is_trending DESC, rating_percentage DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        m = dict(r)
        m["cast"] = parse_json_field(m["cast_json"])
        m["formats"] = parse_json_field(m["formats_json"])
        del m["cast_json"]
        del m["formats_json"]
        
        if format and format != "All" and format not in m["formats"]:
            continue
            
        result.append(m)
        
    conn.close()
    return result

@app.get("/api/movies/{movie_id}")
def get_movie_detail(movie_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")
        
    m = dict(row)
    m["cast"] = parse_json_field(m["cast_json"])
    m["formats"] = parse_json_field(m["formats_json"])
    del m["cast_json"]
    del m["formats_json"]
    
    cursor.execute("SELECT * FROM reviews WHERE movie_id = ? ORDER BY id DESC", (movie_id,))
    reviews = [dict(r) for r in cursor.fetchall()]
    m["reviews"] = reviews
    
    conn.close()
    return m

@app.get("/api/showtimes")
def get_showtimes(
    movie_id: int,
    city_id: Optional[int] = None,
    date: Optional[str] = None
):
    if not date:
        date = datetime.date.today().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            s.id as showtime_id, s.date, s.time, s.format,
            s.price_recliner, s.price_prime, s.price_classic,
            c.id as cinema_id, c.name as cinema_name, c.address as cinema_address,
            c.chain as cinema_chain, c.facilities_json,
            sc.name as screen_name
        FROM showtimes s
        JOIN cinemas c ON s.cinema_id = c.id
        JOIN screens sc ON s.screen_id = sc.id
        WHERE s.movie_id = ? AND s.date = ?
    """
    params = [movie_id, date]

    if city_id:
        query += " AND c.city_id = ?"
        params.append(city_id)

    query += " ORDER BY c.name ASC, s.time ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    cinemas_dict = {}
    for r in rows:
        cid = r["cinema_id"]
        if cid not in cinemas_dict:
            cinemas_dict[cid] = {
                "cinema_id": cid,
                "cinema_name": r["cinema_name"],
                "cinema_address": r["cinema_address"],
                "cinema_chain": r["cinema_chain"],
                "facilities": parse_json_field(r["facilities_json"]),
                "showtimes": []
            }
            
        cursor.execute("SELECT COUNT(*) as avail FROM seats WHERE showtime_id = ? AND status = 'AVAILABLE'", (r["showtime_id"],))
        avail_seats = cursor.fetchone()["avail"]
        
        status_label = "Available"
        if avail_seats < 15:
            status_label = "Almost Full"
        elif avail_seats < 40:
            status_label = "Filling Fast"
            
        cinemas_dict[cid]["showtimes"].append({
            "showtime_id": r["showtime_id"],
            "time": r["time"],
            "format": r["format"],
            "screen": r["screen_name"],
            "price_recliner": r["price_recliner"],
            "price_prime": r["price_prime"],
            "price_classic": r["price_classic"],
            "available_seats": avail_seats,
            "status_label": status_label
        })
        
    conn.close()
    return list(cinemas_dict.values())

@app.get("/api/showtimes/{showtime_id}/seats")
def get_seats(showtime_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.id, s.date, s.time, s.format, m.title as movie_title, c.name as cinema_name
        FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        WHERE s.id = ?
    """, (showtime_id,))
    st_info = cursor.fetchone()
    if not st_info:
        conn.close()
        raise HTTPException(status_code=404, detail="Showtime not found")
        
    cursor.execute("SELECT * FROM seats WHERE showtime_id = ? ORDER BY row_label ASC, seat_number ASC", (showtime_id,))
    rows = cursor.fetchall()
    
    seats_list = [dict(r) for r in rows]
    conn.close()
    
    return {
        "showtime": dict(st_info),
        "seats": seats_list
    }

@app.get("/api/food-beverages")
def get_food_beverages():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM food_beverages ORDER BY category ASC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/promos/validate")
def validate_promo(req: PromoValidateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promos WHERE UPPER(code) = ?", (req.code.upper(),))
    promo = cursor.fetchone()
    conn.close()
    
    if not promo:
        raise HTTPException(status_code=400, detail="Invalid promo code")
        
    p = dict(promo)
    if req.amount < p["min_spend"]:
        raise HTTPException(status_code=400, detail=f"Minimum spend of ₹{p['min_spend']:.0f} required for this code")
        
    discount = 0.0
    if p["flat_discount"] > 0:
        discount = p["flat_discount"]
    elif p["discount_percent"] > 0:
        discount = (req.amount * p["discount_percent"]) / 100.0
        if discount > p["max_discount"]:
            discount = p["max_discount"]
            
    return {
        "valid": True,
        "code": p["code"],
        "discount_amount": round(discount, 2),
        "message": f"Promo '{p['code']}' applied! Saved ₹{discount:.2f}"
    }

@app.post("/api/bookings")
def create_booking(req: BookingCreateRequest):
    if not req.seats:
        raise HTTPException(status_code=400, detail="Please select at least one seat")
        
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, m.title as movie_title, m.poster_url, c.name as cinema_name, c.address as cinema_address, sc.name as screen_name
        FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        JOIN screens sc ON s.screen_id = sc.id
        WHERE s.id = ?
    """, (req.showtime_id,))
    st = cursor.fetchone()
    if not st:
        conn.close()
        raise HTTPException(status_code=404, detail="Showtime not found")
        
    seat_codes = [s.seat_code for s in req.seats]
    placeholders = ",".join(["?"] * len(seat_codes))
    cursor.execute(f"SELECT seat_code, status FROM seats WHERE showtime_id = ? AND seat_code IN ({placeholders})", [req.showtime_id] + seat_codes)
    existing_seats = cursor.fetchall()
    
    for s_row in existing_seats:
        if s_row["status"] != "AVAILABLE":
            conn.close()
            raise HTTPException(status_code=400, detail=f"Seat {s_row['seat_code']} is no longer available.")
            
    cursor.execute(f"UPDATE seats SET status = 'BOOKED' WHERE showtime_id = ? AND seat_code IN ({placeholders})", [req.showtime_id] + seat_codes)
    
    seat_subtotal = sum(s.price for s in req.seats)
    fnb_subtotal = sum(f.price * f.qty for f in req.fnb)
    subtotal = seat_subtotal + fnb_subtotal
    convenience_fee = (35.0 * len(req.seats)) * 1.18
    
    discount = 0.0
    if req.promo_code:
        cursor.execute("SELECT * FROM promos WHERE UPPER(code) = ?", (req.promo_code.upper(),))
        promo = cursor.fetchone()
        if promo:
            p = dict(promo)
            if subtotal >= p["min_spend"]:
                if p["flat_discount"] > 0:
                    discount = p["flat_discount"]
                elif p["discount_percent"] > 0:
                    discount = (subtotal * p["discount_percent"]) / 100.0
                    if discount > p["max_discount"]:
                        discount = p["max_discount"]
                        
    total_amount = max(0.0, subtotal + convenience_fee - discount)
    booking_id = f"ST-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO bookings (
            booking_id, showtime_id, user_name, user_email, user_phone,
            seats_json, fnb_json, subtotal, convenience_fee, discount_amount,
            total_amount, booking_time, payment_method, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED')
    """, (
        booking_id, req.showtime_id, req.user_name, req.user_email, req.user_phone,
        json.dumps([s.dict() for s in req.seats]), json.dumps([f.dict() for f in req.fnb]),
        subtotal, round(convenience_fee, 2), round(discount, 2), round(total_amount, 2),
        now_str, req.payment_method
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "booking_id": booking_id,
        "movie_title": st["movie_title"],
        "poster_url": st["poster_url"],
        "cinema_name": st["cinema_name"],
        "cinema_address": st["cinema_address"],
        "screen_name": st["screen_name"],
        "date": st["date"],
        "time": st["time"],
        "format": st["format"],
        "seats": [s.seat_code for s in req.seats],
        "total_amount": round(total_amount, 2),
        "booking_time": now_str,
        "qr_payload": f"SHOWTIME-TICKET:{booking_id}|{st['movie_title']}|SEATS:{','.join(seat_codes)}"
    }

@app.get("/api/bookings/{booking_id}")
def get_booking(booking_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, s.date, s.time, s.format, m.title as movie_title, m.poster_url, m.certificate,
               c.name as cinema_name, c.address as cinema_address, sc.name as screen_name
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        JOIN screens sc ON s.screen_id = sc.id
        WHERE b.booking_id = ?
    """, (booking_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    b = dict(row)
    b["seats"] = parse_json_field(b["seats_json"])
    b["fnb"] = parse_json_field(b["fnb_json"])
    del b["seats_json"]
    del b["fnb_json"]
    b["qr_payload"] = f"SHOWTIME-TICKET:{booking_id}|{b['movie_title']}"
    return b

@app.get("/api/my-bookings")
def get_my_bookings(email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, s.date, s.time, s.format, m.title as movie_title, m.poster_url,
               c.name as cinema_name
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        WHERE LOWER(b.user_email) = ?
        ORDER BY b.booking_time DESC
    """, (email.lower().strip(),))
    rows = cursor.fetchall()
    conn.close()
    
    res = []
    for r in rows:
        b = dict(r)
        b["seats"] = parse_json_field(b["seats_json"])
        b["fnb"] = parse_json_field(b["fnb_json"])
        del b["seats_json"]
        del b["fnb_json"]
        res.append(b)
    return res

# ----------------- ADMIN / EDIT MODE API ROUTES ----------------- #

@app.post("/api/admin/movies")
def create_movie(m: MovieCreateUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movies (
            title, language, genre, certificate, duration_mins, release_date,
            rating_percentage, rating_count, likes_count, synopsis, director,
            cast_json, poster_url, backdrop_url, trailer_url, formats_json, is_trending
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        m.title, m.language, m.genre, m.certificate, m.duration_mins, m.release_date,
        m.rating_percentage, m.rating_count, m.likes_count, m.synopsis, m.director,
        json.dumps(m.cast), m.poster_url, m.backdrop_url, m.trailer_url,
        json.dumps(m.formats), 1 if m.is_trending else 0
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"success": True, "movie_id": new_id, "message": f"Movie '{m.title}' created successfully!"}

@app.put("/api/admin/movies/{movie_id}")
def update_movie(movie_id: int, m: MovieCreateUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE movies SET
            title = ?, language = ?, genre = ?, certificate = ?, duration_mins = ?,
            release_date = ?, rating_percentage = ?, synopsis = ?, director = ?,
            poster_url = ?, backdrop_url = ?, trailer_url = ?, is_trending = ?
        WHERE id = ?
    """, (
        m.title, m.language, m.genre, m.certificate, m.duration_mins,
        m.release_date, m.rating_percentage, m.synopsis, m.director,
        m.poster_url, m.backdrop_url, m.trailer_url, 1 if m.is_trending else 0,
        movie_id
    ))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Movie '{m.title}' updated successfully!"}

@app.delete("/api/admin/movies/{movie_id}")
def delete_movie(movie_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Movie deleted successfully!"}

@app.post("/api/admin/promos")
def create_promo(p: PromoCreateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO promos (code, discount_percent, flat_discount, max_discount, min_spend)
        VALUES (?, ?, ?, ?, ?)
    """, (p.code.upper(), p.discount_percent, p.flat_discount, p.max_discount, p.min_spend))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Promo code '{p.code.upper()}' created successfully!"}

# ----------------- AUTHENTICATION & USER ROUTES ----------------- #

class AuthRegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class AuthLoginRequest(BaseModel):
    email: str
    password: str

class AiRecommendRequest(BaseModel):
    prompt: str

@app.post("/api/auth/register")
def register_user(req: AuthRegisterRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (req.email.lower(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email is already registered. Please sign in.")
    
    import hashlib
    pwd_hash = hashlib.sha256(req.password.encode()).hexdigest()
    created_at = datetime.date.today().strftime("%Y-%m-%d")
    
    cursor.execute("INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                   (req.name, req.email.lower(), pwd_hash, created_at))
    uid = cursor.lastrowid
    conn.commit()
    conn.close()
    
    token = f"st_user_{uid}_{uuid.uuid4().hex[:8]}"
    return {
        "success": True,
        "message": f"Welcome to ShowTime, {req.name}!",
        "token": token,
        "user": {"id": uid, "name": req.name, "email": req.email.lower()}
    }

@app.post("/api/auth/login")
def login_user(req: AuthLoginRequest):
    import hashlib
    pwd_hash = hashlib.sha256(req.password.encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (req.email.lower(), pwd_hash))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    u = dict(row)
    token = f"st_user_{u['id']}_{uuid.uuid4().hex[:8]}"
    return {
        "success": True,
        "message": f"Welcome back, {u['name']}!",
        "token": token,
        "user": {"id": u["id"], "name": u["name"], "email": u["email"]}
    }

@app.post("/api/ai/recommend")
def ai_recommend(req: AiRecommendRequest):
    prompt_lower = req.prompt.lower()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    all_movies = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    matched = []
    if "action" in prompt_lower or "fight" in prompt_lower or "jananayagan" in prompt_lower:
        matched = [m for m in all_movies if "Action" in m["genre"] or "Jananayagan" in m["title"]]
    elif "comedy" in prompt_lower or "fun" in prompt_lower or "dude" in prompt_lower:
        matched = [m for m in all_movies if "Comedy" in m["genre"] or "Dude" in m["title"]]
    elif "sci-fi" in prompt_lower or "future" in prompt_lower or "kalki" in prompt_lower:
        matched = [m for m in all_movies if "Sci-Fi" in m["genre"] or "Kalki" in m["title"]]
    else:
        matched = sorted(all_movies, key=lambda x: x["rating_percentage"], reverse=True)[:3]
        
    if not matched:
        matched = all_movies[:3]
        
    m = matched[0]
    reply = f"🍿 **ShowTime AI Recommendation**: Based on your preference, we highly recommend **{m['title']}**! Rated **{m['rating_percentage']}%** with genre *{m['genre']}*. {m['synopsis'][:140]}..."
    
    return {
        "reply": reply,
        "movie": {
            "id": m["id"],
            "title": m["title"],
            "rating_percentage": m["rating_percentage"],
            "poster_url": m["poster_url"]
        }
    }

# Serve Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "ShowTime API Backend is running!"}
