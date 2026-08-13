import urllib.request
import json
import sqlite3

def fetch_wiki_thumb(wiki_title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(wiki_title)}&prop=pageimages&piprop=thumbnail&pithumbsize=300&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'ShowTimeMovieApp/1.0 (contact@showtime.app)'})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            pages = data['query']['pages']
            for pid in pages:
                thumb = pages[pid].get('thumbnail', {}).get('source')
                if thumb:
                    return thumb
    except Exception as e:
        print(f"Error fetching thumb for {wiki_title}: {e}")
    return None

# Mapping actor name -> Wikipedia Page Title
ACTOR_WIKI_MAP = {
    "Thalapathy Vijay": "Vijay (actor)",
    "Trisha Krishnan": "Trisha Krishnan",
    "Sanjay Dutt": "Sanjay Dutt",
    "Arjun Sarja": "Arjun Sarja",
    "Gautham Vasudev Menon": "Gautham Vasudev Menon",
    "Priya Anand": "Priya Anand",
    "Pradeep Ranganathan": "Pradeep Ranganathan",
    "Mamitha Baiju": "Mamitha Baiju",
    "Krithi Shetty": "Krithi Shetty",
    "Yogi Babu": "Yogi Babu",
    "Allu Arjun": "Allu Arjun",
    "Rashmika Mandanna": "Rashmika Mandanna",
    "Fahadh Faasil": "Fahadh Faasil",
    "Jagapathi Babu": "Jagapathi Babu",
    "Prakash Raj": "Prakash Raj",
    "Prabhas": "Prabhas",
    "Amitabh Bachchan": "Amitabh Bachchan",
    "Deepika Padukone": "Deepika Padukone",
    "Kamal Haasan": "Kamal Haasan",
    "Disha Patani": "Disha Patani",
    "Rajkummar Rao": "Rajkummar Rao",
    "Shraddha Kapoor": "Shraddha Kapoor",
    "Pankaj Tripathi": "Pankaj Tripathi",
    "Abhishek Banerjee": "Abhishek Banerjee (actor)",
    "Aparshakti Khurana": "Aparshakti Khurana",
    "Ryan Reynolds": "Ryan Reynolds",
    "Hugh Jackman": "Hugh Jackman",
    "Emma Corrin": "Emma Corrin",
    "Morena Baccarin": "Morena Baccarin",
    "Rob Delaney": "Rob Delaney",
    "Shameik Moore": "Shameik Moore",
    "Hailee Steinfeld": "Hailee Steinfeld",
    "Oscar Isaac": "Oscar Isaac",
    "Jake Johnson": "Jake Johnson",
    "Daniel Kaluuya": "Daniel Kaluuya",
    "Sam Worthington": "Sam Worthington",
    "Zoe Saldana": "Zoe Saldana",
    "Sigourney Weaver": "Sigourney Weaver",
    "Stephen Lang": "Stephen Lang (actor)",
    "Kate Winslet": "Kate Winslet",
    "Cillian Murphy": "Cillian Murphy",
    "Emily Blunt": "Emily Blunt",
    "Matt Damon": "Matt Damon",
    "Robert Downey Jr.": "Robert Downey Jr.",
    "Florence Pugh": "Florence Pugh",
    "Timothée Chalamet": "Timothée Chalamet",
    "Zendaya": "Zendaya",
    "Rebecca Ferguson": "Rebecca Ferguson",
    "Austin Butler": "Austin Butler",
    "Javier Bardem": "Javier Bardem",
    "Christian Bale": "Christian Bale",
    "Heath Ledger": "Heath Ledger",
    "Aaron Eckhart": "Aaron Eckhart",
    "Michael Caine": "Michael Caine",
    "Gary Oldman": "Gary Oldman",
    "Morgan Freeman": "Morgan Freeman",
    "Shah Rukh Khan": "Shah Rukh Khan",
    "Nayanthara": "Nayanthara",
    "Vijay Sethupathi": "Vijay Sethupathi",
    "Sanya Malhotra": "Sanya Malhotra"
}

def update_photos():
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

        print(f"Fetching real Wikipedia portraits for movie: {title}")
        for member in cast_list:
            name = member["name"]
            role = member["role"]
            wiki_title = ACTOR_WIKI_MAP.get(name, name)
            
            photo_url = fetch_wiki_thumb(wiki_title)
            if not photo_url:
                photo_url = member.get("avatar", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150")

            updated_cast.append({
                "name": name,
                "role": role,
                "avatar": photo_url
            })
            print(f"  - {name} ({role}) -> {photo_url[:60]}...")

        cursor.execute("UPDATE movies SET cast_json = ? WHERE id = ?", (json.dumps(updated_cast), m_id))

    conn.commit()
    conn.close()
    print("FINISHED UPDATING ALL REAL ACTOR WIKIPEDIA PORTRAITS!")

if __name__ == "__main__":
    update_photos()
