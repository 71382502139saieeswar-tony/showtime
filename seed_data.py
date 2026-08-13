import sqlite3
import json
import datetime
import random
from database import get_db, init_db

def seed_all():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM seats")
    cursor.execute("DELETE FROM showtimes")
    cursor.execute("DELETE FROM screens")
    cursor.execute("DELETE FROM cinemas")
    cursor.execute("DELETE FROM movies")
    cursor.execute("DELETE FROM cities")
    cursor.execute("DELETE FROM food_beverages")
    cursor.execute("DELETE FROM promos")

    # 1. Cities
    cities = [
        ("Mumbai", "Maharashtra", 1),
        ("Delhi NCR", "Delhi", 1),
        ("Bengaluru", "Karnataka", 1),
        ("Hyderabad", "Telangana", 1),
        ("Chennai", "Tamil Nadu", 1),
        ("Pune", "Maharashtra", 1),
        ("Kolkata", "West Bengal", 0),
        ("Ahmedabad", "Gujarat", 0)
    ]
    cursor.executemany("INSERT INTO cities (name, state, is_popular) VALUES (?, ?, ?)", cities)
    
    city_map = {}
    cursor.execute("SELECT id, name FROM cities")
    for row in cursor.fetchall():
        city_map[row["name"]] = row["id"]

    # 2. Movies Catalog with 100% REAL LOCAL CAST HEADSHOTS
    movies_data = [
        {
            "title": "Leo",
            "language": "Tamil, Telugu, Hindi, Malayalam",
            "genre": "Action, Crime, Thriller",
            "certificate": "UA 16+",
            "duration_mins": 164,
            "release_date": "2023-10-19",
            "rating_percentage": 96,
            "rating_count": 680000,
            "likes_count": 1050000,
            "synopsis": "Parthiban is a mild-mannered cafe owner in Himachal Pradesh who gets thrust into the dark criminal underworld when ruthless gang leaders suspect he is their estranged hitman brother, Leo Das.",
            "director": "Lokesh Kanagaraj",
            "cast_json": json.dumps([
                {"name": "Thalapathy Vijay", "role": "Parthiban / Leo Das", "avatar": "/static/images/cast/thalapathy_vijay.jpg"},
                {"name": "Trisha Krishnan", "role": "Sathya (Wife)", "avatar": "/static/images/cast/trisha_krishnan.jpg"},
                {"name": "Sanjay Dutt", "role": "Antony Das", "avatar": "/static/images/cast/sanjay_dutt.jpg"},
                {"name": "Arjun Sarja", "role": "Harold Das", "avatar": "/static/images/cast/arjun_sarja.jpg"},
                {"name": "Gautham Vasudev Menon", "role": "Joshy Andrews", "avatar": "/static/images/cast/gautham_vasudev_menon.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/75/Leo_%282023_Indian_film%29.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/Po3jStA673E",
            "formats_json": json.dumps(["2D", "IMAX 2D", "Dolby Atmos"]),
            "is_trending": 1
        },
        {
            "title": "Love Today",
            "language": "Tamil, Telugu, Hindi",
            "genre": "Comedy, Romance, Drama",
            "certificate": "UA",
            "duration_mins": 154,
            "release_date": "2022-11-04",
            "rating_percentage": 94,
            "rating_count": 320000,
            "likes_count": 580000,
            "synopsis": "A young couple Uthaman and Nikitha are challenged by her strict father to swap their smartphones for a day before getting married, unleashing hilarious chaotic revelations.",
            "director": "Pradeep Ranganathan",
            "cast_json": json.dumps([
                {"name": "Pradeep Ranganathan", "role": "Uthaman Pradeep", "avatar": "/static/images/cast/pradeep_ranganathan.jpg"},
                {"name": "Ivana", "role": "Nikitha", "avatar": "/static/images/cast/ivana.jpg"},
                {"name": "Sathyaraj", "role": "Venu Shastri (Father)", "avatar": "/static/images/cast/sathyaraj.jpg"},
                {"name": "Radhika Sarathkumar", "role": "Saraswathi (Mother)", "avatar": "/static/images/cast/radhika_sarathkumar.jpg"},
                {"name": "Yogi Babu", "role": "Dr. Yogi", "avatar": "/static/images/cast/yogi_babu.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/3/33/Love_Today_2022_poster.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/FaQe8JFGw4s",
            "formats_json": json.dumps(["2D", "Dolby Atmos"]),
            "is_trending": 1
        },
        {
            "title": "Pushpa 2: The Rule",
            "language": "Telugu, Hindi, Tamil, Malayalam",
            "genre": "Action, Crime, Drama",
            "certificate": "UA 16+",
            "duration_mins": 175,
            "release_date": "2024-12-05",
            "rating_percentage": 96,
            "rating_count": 510000,
            "likes_count": 890000,
            "synopsis": "The clash between Pushpa Raj and SP Bhanwar Singh Shekhawat continues as Pushpa expands his red sandalwood smuggling empire globally.",
            "director": "Sukumar",
            "cast_json": json.dumps([
                {"name": "Allu Arjun", "role": "Pushpa Raj", "avatar": "/static/images/cast/allu_arjun.jpg"},
                {"name": "Rashmika Mandanna", "role": "Srivalli", "avatar": "/static/images/cast/rashmika_mandanna.jpg"},
                {"name": "Fahadh Faasil", "role": "SP Bhanwar Singh Shekhawat", "avatar": "/static/images/cast/fahadh_faasil.jpg"},
                {"name": "Jagapathi Babu", "role": "Dharma", "avatar": "/static/images/cast/jagapathi_babu.jpg"},
                {"name": "Prakash Raj", "role": "Chief Minister", "avatar": "/static/images/cast/prakash_raj.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/11/Pushpa_2-_The_Rule.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/1kvyE3K1rU4",
            "formats_json": json.dumps(["2D", "3D", "IMAX 3D"]),
            "is_trending": 1
        },
        {
            "title": "Kalki 2898 AD",
            "language": "Telugu, Hindi, Tamil, Malayalam",
            "genre": "Sci-Fi, Action, Mythology",
            "certificate": "UA 16+",
            "duration_mins": 180,
            "release_date": "2024-06-27",
            "rating_percentage": 92,
            "rating_count": 245000,
            "likes_count": 480000,
            "synopsis": "A modern avatar of Vishnu descends to Earth to protect the unborn child of Sumati from the dark forces of Supreme Yaskin in a post-apocalyptic world.",
            "director": "Nag Ashwin",
            "cast_json": json.dumps([
                {"name": "Prabhas", "role": "Bhairava / Karna", "avatar": "/static/images/cast/prabhas.jpg"},
                {"name": "Amitabh Bachchan", "role": "Ashwatthama", "avatar": "/static/images/cast/amitabh_bachchan.jpg"},
                {"name": "Deepika Padukone", "role": "Sumati (SU-M80)", "avatar": "/static/images/cast/deepika_padukone.jpg"},
                {"name": "Kamal Haasan", "role": "Supreme Yaskin", "avatar": "/static/images/cast/kamal_haasan.jpg"},
                {"name": "Disha Patani", "role": "Roxie", "avatar": "/static/images/cast/disha_patani.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/4/4c/Kalki_2898_AD.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/k99-vMPh3-M",
            "formats_json": json.dumps(["2D", "3D", "IMAX 3D"]),
            "is_trending": 1
        },
        {
            "title": "Stree 2: Sarkate Ka Aatank",
            "language": "Hindi",
            "genre": "Horror, Comedy",
            "certificate": "UA",
            "duration_mins": 147,
            "release_date": "2024-08-15",
            "rating_percentage": 95,
            "rating_count": 310000,
            "likes_count": 520000,
            "synopsis": "The town of Chanderi is haunted once again, this time by a headless demon 'Sarkata'. Vicky and his eccentric crew reunite with the mysterious woman to save their town.",
            "director": "Amar Kaushik",
            "cast_json": json.dumps([
                {"name": "Rajkummar Rao", "role": "Vicky", "avatar": "/static/images/cast/rajkummar_rao.jpg"},
                {"name": "Shraddha Kapoor", "role": "The Unknown Girl", "avatar": "/static/images/cast/shraddha_kapoor.jpg"},
                {"name": "Pankaj Tripathi", "role": "Rudra", "avatar": "/static/images/cast/pankaj_tripathi.jpg"},
                {"name": "Abhishek Banerjee", "role": "Jana", "avatar": "/static/images/cast/abhishek_banerjee.jpg"},
                {"name": "Aparshakti Khurana", "role": "Bittu", "avatar": "/static/images/cast/aparshakti_khurana.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/a/a1/Stree_2.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/KVnheXywIbU",
            "formats_json": json.dumps(["2D", "Dolby Atmos"]),
            "is_trending": 0
        },
        {
            "title": "Jawan",
            "language": "Hindi, Tamil, Telugu",
            "genre": "Action, Thriller",
            "certificate": "UA",
            "duration_mins": 169,
            "release_date": "2023-09-07",
            "rating_percentage": 89,
            "rating_count": 550000,
            "likes_count": 740000,
            "synopsis": "A high-octane action thriller outlining the emotional journey of a man who is set to rectify the wrongs in society.",
            "director": "Atlee",
            "cast_json": json.dumps([
                {"name": "Shah Rukh Khan", "role": "Vikram Rathore / Azad", "avatar": "/static/images/cast/shah_rukh_khan.jpg"},
                {"name": "Nayanthara", "role": "Narmada Rai", "avatar": "/static/images/cast/nayanthara.jpg"},
                {"name": "Vijay Sethupathi", "role": "Kalee Gaikwad", "avatar": "/static/images/cast/vijay_sethupathi.jpg"},
                {"name": "Deepika Padukone", "role": "Aishwarya Rathore", "avatar": "/static/images/cast/deepika_padukone.jpg"},
                {"name": "Sanya Malhotra", "role": "Eeram", "avatar": "/static/images/cast/sanya_malhotra.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/3/39/Jawan_film_poster.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/MWOlnZSnXhU",
            "formats_json": json.dumps(["2D", "IMAX 2D", "4DX"]),
            "is_trending": 0
        },
        {
            "title": "Deadpool & Wolverine",
            "language": "English, Hindi, Telugu, Tamil",
            "genre": "Action, Comedy, Sci-Fi",
            "certificate": "A",
            "duration_mins": 128,
            "release_date": "2024-07-26",
            "rating_percentage": 91,
            "rating_count": 420000,
            "likes_count": 680000,
            "synopsis": "Wolverine is recovering from his injuries when he crosses paths with the loudmouth Deadpool. They team up to defeat a common enemy threatening the multiverse.",
            "director": "Shawn Levy",
            "cast_json": json.dumps([
                {"name": "Ryan Reynolds", "role": "Wade Wilson / Deadpool", "avatar": "/static/images/cast/ryan_reynolds.jpg"},
                {"name": "Hugh Jackman", "role": "Logan / Wolverine", "avatar": "/static/images/cast/hugh_jackman.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/4/4c/Deadpool_%26_Wolverine_poster.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/73_1biulkYk",
            "formats_json": json.dumps(["2D", "3D", "IMAX 3D", "4DX"]),
            "is_trending": 0
        },
        {
            "title": "Oppenheimer",
            "language": "English, Hindi",
            "genre": "Biography, Drama, History",
            "certificate": "UA",
            "duration_mins": 180,
            "release_date": "2023-07-21",
            "rating_percentage": 95,
            "rating_count": 680000,
            "likes_count": 920000,
            "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
            "director": "Christopher Nolan",
            "cast_json": json.dumps([
                {"name": "Cillian Murphy", "role": "J. Robert Oppenheimer", "avatar": "/static/images/cast/cillian_murphy.jpg"},
                {"name": "Emily Blunt", "role": "Katherine 'Kitty' Oppenheimer", "avatar": "/static/images/cast/emily_blunt.jpg"},
                {"name": "Matt Damon", "role": "Leslie Groves", "avatar": "/static/images/cast/matt_damon.jpg"},
                {"name": "Robert Downey Jr.", "role": "Lewis Strauss", "avatar": "/static/images/cast/robert_downey_jr.jpg"},
                {"name": "Florence Pugh", "role": "Jean Tatlock", "avatar": "/static/images/cast/florence_pugh.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/4/4a/Oppenheimer_%28film%29.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/uYPbbksJxIg",
            "formats_json": json.dumps(["2D", "IMAX 70mm", "IMAX 3D"]),
            "is_trending": 0
        },
        {
            "title": "Dune: Part Two",
            "language": "English, Hindi, Telugu",
            "genre": "Sci-Fi, Adventure, Action",
            "certificate": "UA",
            "duration_mins": 166,
            "release_date": "2024-03-01",
            "rating_percentage": 94,
            "rating_count": 550000,
            "likes_count": 780000,
            "synopsis": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
            "director": "Denis Villeneuve",
            "cast_json": json.dumps([
                {"name": "Timothée Chalamet", "role": "Paul Atreides", "avatar": "/static/images/cast/timothee_chalamet.jpg"},
                {"name": "Zendaya", "role": "Chani", "avatar": "/static/images/cast/zendaya.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/5/52/Dune_Part_Two_poster.jpeg",
            "backdrop_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/Way9Dexny3w",
            "formats_json": json.dumps(["2D", "IMAX 3D", "4DX"]),
            "is_trending": 0
        },
        {
            "title": "The Dark Knight",
            "language": "English, Hindi",
            "genre": "Action, Crime, Drama",
            "certificate": "UA",
            "duration_mins": 152,
            "release_date": "2008-07-18",
            "rating_percentage": 98,
            "rating_count": 2800000,
            "likes_count": 1500000,
            "synopsis": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "director": "Christopher Nolan",
            "cast_json": json.dumps([
                {"name": "Christian Bale", "role": "Bruce Wayne / Batman", "avatar": "/static/images/cast/christian_bale.jpg"},
                {"name": "Heath Ledger", "role": "The Joker", "avatar": "/static/images/cast/heath_ledger.jpg"}
            ]),
            "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/1c/The_Dark_Knight_%282008_film%29.jpg",
            "backdrop_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200&auto=format&fit=crop&q=80",
            "trailer_url": "https://www.youtube.com/embed/EXeTwQWrcwY",
            "formats_json": json.dumps(["2D", "IMAX 2D"]),
            "is_trending": 0
        }
    ]

    for m in movies_data:
        cursor.execute("""
        INSERT INTO movies (
            title, language, genre, certificate, duration_mins, release_date,
            rating_percentage, rating_count, likes_count, synopsis, director,
            cast_json, poster_url, backdrop_url, trailer_url, formats_json, is_trending
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["title"], m["language"], m["genre"], m["certificate"], m["duration_mins"],
            m["release_date"], m["rating_percentage"], m["rating_count"], m["likes_count"],
            m["synopsis"], m["director"], m["cast_json"], m["poster_url"], m["backdrop_url"],
            m["trailer_url"], m["formats_json"], m["is_trending"]
        ))

    # 3. Cinemas
    cinemas_data = [
        {"city": "Mumbai", "name": "PVR ICON Phoenix Palladium", "address": "4th Floor, Phoenix Palladium, Lower Parel, Mumbai", "chain": "PVR", "facilities": ["M-Ticket", "Food & Beverage", "Recliners", "IMAX", "Dolby Atmos"]},
        {"city": "Mumbai", "name": "INOX Megaplex Inorbit Mall", "address": "2nd Floor, Inorbit Mall, Malad West, Mumbai", "chain": "INOX", "facilities": ["M-Ticket", "Food & Beverage", "Wheelchair Accessible", "ScreenX"]},
        {"city": "Delhi NCR", "name": "PVR Director's Cut Vasant Kunj", "address": "Ambience Mall, Vasant Kunj, New Delhi", "chain": "PVR", "facilities": ["M-Ticket", "Fine Dining", "Recliners", "Valet Parking"]},
        {"city": "Bengaluru", "name": "PVR Superplex Orion Mall", "address": "Dr. Rajkumar Road, Rajajinagar, Bengaluru", "chain": "PVR", "facilities": ["M-Ticket", "Food & Beverage", "IMAX 3D", "PXL"]}
    ]

    for c in cinemas_data:
        city_id = city_map[c["city"]]
        cursor.execute("""
        INSERT INTO cinemas (city_id, name, address, chain, facilities_json)
        VALUES (?, ?, ?, ?, ?)
        """, (city_id, c["name"], c["address"], c["chain"], json.dumps(c["facilities"])))
        cid = cursor.lastrowid
        cursor.execute("INSERT INTO screens (cinema_id, name, screen_type) VALUES (?, ?, ?)", (cid, "Screen 1", "IMAX Laser"))
        cursor.execute("INSERT INTO screens (cinema_id, name, screen_type) VALUES (?, ?, ?)", (cid, "Screen 2", "Audi 2 Dolby Atmos"))

    # 4. Showtimes & Seats
    today = datetime.date.today()
    times_list = ["09:30 AM", "12:45 PM", "04:15 PM", "07:45 PM", "10:30 PM"]

    cursor.execute("SELECT id FROM movies")
    all_movie_ids = [r["id"] for r in cursor.fetchall()]

    cursor.execute("SELECT id, cinema_id FROM screens")
    screens_list = cursor.fetchall()

    showtime_count = 0
    for day_offset in range(4):
        show_date = (today + datetime.timedelta(days=day_offset)).strftime("%Y-%m-%d")
        for mid in all_movie_ids:
            for s in screens_list[:4]:
                for t in times_list[:2]:
                    cursor.execute("""
                    INSERT INTO showtimes (movie_id, cinema_id, screen_id, date, time, format, price_recliner, price_prime, price_classic)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (mid, s["cinema_id"], s["id"], show_date, t, "2D", 450.0, 300.0, 180.0))
                    st_id = cursor.lastrowid
                    
                    seats_to_insert = []
                    for row_label, tier, price in [("A", "Recliner", 450.0), ("B", "Prime", 300.0), ("C", "Classic", 180.0)]:
                        for num in range(1, 10):
                            status = "RESERVED" if random.random() < 0.20 else "AVAILABLE"
                            seats_to_insert.append((st_id, f"{row_label}{num}", row_label, num, tier, price, status))
                    cursor.executemany("INSERT INTO seats (showtime_id, seat_code, row_label, seat_number, tier, price, status) VALUES (?, ?, ?, ?, ?, ?, ?)", seats_to_insert)

    # 5. Food & Beverages
    fnb_list = [
        ("Large Salted Popcorn (350g)", "Popcorn", "Classic salted warm popcorn", 290.0, "https://images.unsplash.com/photo-1585647347384-2593bc35786b?w=400"),
        ("Caramel & Cheese Duo Popcorn", "Popcorn", "Gourmet caramel and sharp cheddar cheese popcorn", 340.0, "https://images.unsplash.com/photo-1578849278619-e73505e9610f?w=400"),
        ("Classic Pepsi (800ml)", "Beverage", "Refreshing chilled Pepsi cold drink", 210.0, "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400")
    ]
    cursor.executemany("INSERT INTO food_beverages (name, category, description, price, image_url) VALUES (?, ?, ?, ?, ?)", fnb_list)

    # 6. Promos
    cursor.executemany("INSERT INTO promos (code, discount_percent, flat_discount, max_discount, min_spend) VALUES (?, ?, ?, ?, ?)", [("SHOWTIME20", 20.0, 0, 150.0, 300.0)])

    conn.commit()
    conn.close()
    print("Database successfully seeded with 100% genuine local cast photos!")

if __name__ == "__main__":
    seed_all()
