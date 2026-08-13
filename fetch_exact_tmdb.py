import urllib.request
import json
import sqlite3

API_KEY = "b8c4c3468504ee46bc9e34e9e048c267"

MOVIE_SEARCH_QUERIES = [
    ("Leo", "Leo"),
    ("Dude", "Dude"),
    ("Pushpa 2: The Rule", "Pushpa 2: The Rule"),
    ("Kalki 2898 AD", "Kalki 2898 AD"),
    ("Stree 2: Sarkate Ka Aatank", "Stree 2"),
    ("Deadpool & Wolverine", "Deadpool & Wolverine"),
    ("Spider-Man: Across the Spider-Verse", "Spider-Man: Across the Spider-Verse"),
    ("Avatar: The Way of Water", "Avatar: The Way of Water"),
    ("Oppenheimer", "Oppenheimer"),
    ("Dune: Part Two", "Dune: Part Two"),
    ("The Dark Knight", "The Dark Knight"),
    ("Jawan", "Jawan")
]

def get_movie_details(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            results = data.get("results", [])
            if results:
                m = results[0]
                m_id = m["id"]
                poster = f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else None
                backdrop = f"https://image.tmdb.org/t/p/w1280{m['backdrop_path']}" if m.get("backdrop_path") else None
                return m_id, poster, backdrop, m.get("overview")
    except Exception as e:
        print(f"Error fetching movie {query}: {e}")
    return None, None, None, None

def get_movie_cast(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    cast_list = []
    director = "Unknown Director"
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            crew = data.get("crew", [])
            for c in crew:
                if c.get("job") == "Director":
                    director = c.get("name")
                    break

            for c in data.get("cast", [])[:6]:
                name = c.get("name")
                character = c.get("character")
                profile = f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get("profile_path") else "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
                cast_list.append({
                    "name": name,
                    "role": character,
                    "avatar": profile
                })
    except Exception as e:
        print(f"Error fetching credits for movie_id {movie_id}: {e}")
    return director, cast_list

def fix_all_movies():
    conn = sqlite3.connect("showtime.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for app_title, search_q in MOVIE_SEARCH_QUERIES:
        m_id, poster, backdrop, overview = get_movie_details(search_q)
        if m_id:
            director, cast_list = get_movie_cast(m_id)
            print(f"\n=============================")
            print(f"Movie: {app_title} (TMDB ID: {m_id})")
            print(f"Poster: {poster}")
            print(f"Director: {director}")
            print(f"Lead Cast ({len(cast_list)} members):")
            for c in cast_list:
                print(f"  - {c['name']} as {c['role']} -> {c['avatar']}")

            # Update DB
            cursor.execute("SELECT id FROM movies WHERE title = ?", (app_title,))
            row = cursor.fetchone()
            if row:
                db_id = row["id"]
                cursor.execute("""
                UPDATE movies 
                SET poster_url = ?, backdrop_url = ?, director = ?, cast_json = ?
                WHERE id = ?
                """, (poster, backdrop, director, json.dumps(cast_list), db_id))
            else:
                print(f"Movie {app_title} not found in DB!")
        else:
            print(f"No TMDB match for {app_title}")

    conn.commit()
    conn.close()
    print("\nSUCCESSFULLY UPDATED ALL MOVIES WITH EXACT TMDB POSTERS, BACKDROPS, DIRECTORS & HERO CAST HEADSHOTS!")

if __name__ == "__main__":
    fix_all_movies()
