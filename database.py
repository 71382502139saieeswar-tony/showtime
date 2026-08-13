import sqlite3
import json
import os
import random
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "showtime.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Enable FKs
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Cities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        state TEXT NOT NULL,
        is_popular INTEGER DEFAULT 0
    );
    """)

    # Movies Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        language TEXT NOT NULL,
        genre TEXT NOT NULL,
        certificate TEXT NOT NULL,
        duration_mins INTEGER NOT NULL,
        release_date TEXT NOT NULL,
        rating_percentage INTEGER NOT NULL,
        rating_count INTEGER NOT NULL,
        likes_count INTEGER NOT NULL,
        synopsis TEXT NOT NULL,
        director TEXT NOT NULL,
        cast_json TEXT NOT NULL,
        poster_url TEXT NOT NULL,
        backdrop_url TEXT NOT NULL,
        trailer_url TEXT NOT NULL,
        formats_json TEXT NOT NULL,
        is_trending INTEGER DEFAULT 0
    );
    """)

    # Cinemas Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cinemas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        chain TEXT NOT NULL,
        facilities_json TEXT NOT NULL,
        FOREIGN KEY (city_id) REFERENCES cities (id)
    );
    """)

    # Screens Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS screens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cinema_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        screen_type TEXT NOT NULL,
        FOREIGN KEY (cinema_id) REFERENCES cinemas (id)
    );
    """)

    # Showtimes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS showtimes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        cinema_id INTEGER NOT NULL,
        screen_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        format TEXT NOT NULL,
        price_recliner REAL NOT NULL,
        price_prime REAL NOT NULL,
        price_classic REAL NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        FOREIGN KEY (cinema_id) REFERENCES cinemas (id),
        FOREIGN KEY (screen_id) REFERENCES screens (id)
    );
    """)

    # Seats Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        showtime_id INTEGER NOT NULL,
        seat_code TEXT NOT NULL,
        row_label TEXT NOT NULL,
        seat_number INTEGER NOT NULL,
        tier TEXT NOT NULL,
        price REAL NOT NULL,
        status TEXT DEFAULT 'AVAILABLE', -- AVAILABLE, RESERVED, BOOKED
        FOREIGN KEY (showtime_id) REFERENCES showtimes (id),
        UNIQUE(showtime_id, seat_code)
    );
    """)

    # Food & Beverages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_beverages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        image_url TEXT NOT NULL
    );
    """)

    # Promos Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promos (
        code TEXT PRIMARY KEY,
        discount_percent REAL DEFAULT 0,
        flat_discount REAL DEFAULT 0,
        max_discount REAL DEFAULT 1000,
        min_spend REAL DEFAULT 0
    );
    """)

    # Bookings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        showtime_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        user_email TEXT NOT NULL,
        user_phone TEXT NOT NULL,
        seats_json TEXT NOT NULL,
        fnb_json TEXT NOT NULL,
        subtotal REAL NOT NULL,
        convenience_fee REAL NOT NULL,
        discount_amount REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        booking_time TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED',
        FOREIGN KEY (showtime_id) REFERENCES showtimes (id)
    );
    """)

    # Reviews Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    );
    """)

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
