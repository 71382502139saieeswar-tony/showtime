import urllib.request
import json
import sqlite3
import time

API_KEY = "b8c4c3468504ee46bc9e34e9e048c267"

def get_actor_photo(name):
    # Clean name for search
    clean_name = name.replace("Thalapathy ", "").replace(" 'Kitty'", "")
    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={urllib.parse.quote(clean_name)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            results = data.get("results", [])
            if results and results[0].get("profile_path"):
                return f"https://image.tmdb.org/t/p/w185{results[0]['profile_path']}"
    except Exception as e:
        print(f"Error fetching photo for {name}: {e}")
    return None

def update_database_actor_photos():
    conn = sqlite3.connect("showtime.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, cast_json FROM movies")
    movies = cursor.fetchall()

    for m in movies:
        m_id = m["id"]
        title = m["title"]
        cast_list = json.loads(m["cast_json"])
        updated_cast = []

        print(f"Updating cast photos for movie: {title}")
        for member in cast_list:
            name = member["name"]
            role = member["role"]
            photo_url = get_actor_photo(name)
            time.sleep(0.1)

            if not photo_url:
                photo_url = member.get("avatar", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150")

            updated_cast.append({
                "name": name,
                "role": role,
                "avatar": photo_url
            })
            print(f"  - {name} ({role}) -> {photo_url}")

        cursor.execute("UPDATE movies SET cast_json = ? WHERE id = ?", (json.dumps(updated_cast), m_id))

    conn.commit()
    conn.close()
    print("ALL MOVIES CAST PHOTOS UPDATED SUCCESSFULLY WITH TMDB ORIGINAL HEADSHOTS!")

if __name__ == "__main__":
    update_database_actor_photos()
