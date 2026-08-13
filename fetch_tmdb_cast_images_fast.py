import os
import json
import urllib.request
import urllib.parse

os.makedirs("static/images/cast", exist_ok=True)

actors_db = {
    # Leo
    "Thalapathy Vijay": "Vijay",
    "Trisha Krishnan": "Trisha Krishnan",
    "Sanjay Dutt": "Sanjay Dutt",
    "Arjun Sarja": "Arjun",
    "Gautham Vasudev Menon": "Gautham Vasudev Menon",

    # Love Today
    "Pradeep Ranganathan": "Pradeep Ranganathan",
    "Ivana": "Ivana",
    "Sathyaraj": "Sathyaraj",
    "Radhika Sarathkumar": "Radhika Sarathkumar",
    "Yogi Babu": "Yogi Babu",

    # Pushpa 2
    "Allu Arjun": "Allu Arjun",
    "Rashmika Mandanna": "Rashmika Mandanna",
    "Fahadh Faasil": "Fahadh Faasil",
    "Jagapathi Babu": "Jagapathi Babu",
    "Prakash Raj": "Prakash Raj",

    # Kalki 2898 AD
    "Prabhas": "Prabhas",
    "Amitabh Bachchan": "Amitabh Bachchan",
    "Deepika Padukone": "Deepika Padukone",
    "Kamal Haasan": "Kamal Haasan",
    "Disha Patani": "Disha Patani",

    # Stree 2
    "Rajkummar Rao": "Rajkummar Rao",
    "Shraddha Kapoor": "Shraddha Kapoor",
    "Pankaj Tripathi": "Pankaj Tripathi",
    "Abhishek Banerjee": "Abhishek Banerjee",
    "Aparshakti Khurana": "Aparshakti Khurana",

    # Jawan
    "Shah Rukh Khan": "Shah Rukh Khan",
    "Nayanthara": "Nayanthara",
    "Vijay Sethupathi": "Vijay Sethupathi",
    "Sanya Malhotra": "Sanya Malhotra",

    # Deadpool & Wolverine
    "Ryan Reynolds": "Ryan Reynolds",
    "Hugh Jackman": "Hugh Jackman",
    "Emma Corrin": "Emma Corrin",
    "Morena Baccarin": "Morena Baccarin",
    "Rob Delaney": "Rob Delaney",

    # Spider-Man
    "Shameik Moore": "Shameik Moore",
    "Hailee Steinfeld": "Hailee Steinfeld",
    "Oscar Isaac": "Oscar Isaac",
    "Jake Johnson": "Jake Johnson",
    "Daniel Kaluuya": "Daniel Kaluuya",

    # Avatar 2
    "Sam Worthington": "Sam Worthington",
    "Zoe Saldana": "Zoe Saldana",
    "Sigourney Weaver": "Sigourney Weaver",
    "Stephen Lang": "Stephen Lang",
    "Kate Winslet": "Kate Winslet",

    # Oppenheimer
    "Cillian Murphy": "Cillian Murphy",
    "Emily Blunt": "Emily Blunt",
    "Matt Damon": "Matt Damon",
    "Robert Downey Jr.": "Robert Downey Jr.",
    "Florence Pugh": "Florence Pugh",

    # Dune 2
    "Timothée Chalamet": "Timothée Chalamet",
    "Zendaya": "Zendaya",
    "Rebecca Ferguson": "Rebecca Ferguson",
    "Austin Butler": "Austin Butler",
    "Javier Bardem": "Javier Bardem",

    # The Dark Knight
    "Christian Bale": "Christian Bale",
    "Heath Ledger": "Heath Ledger",
    "Aaron Eckhart": "Aaron Eckhart",
    "Michael Caine": "Michael Caine",
    "Gary Oldman": "Gary Oldman",
    "Morgan Freeman": "Morgan Freeman"
}

API_KEY = "e87df3ee12bfbebf509ae2ca3c2941ed"
results = {}

for name, query in actors_db.items():
    filename = name.lower().replace(' ', '_').replace('.', '').replace('é', 'e') + ".jpg"
    filepath = os.path.join("static/images/cast", filename)
    
    if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
        results[name] = f"/static/images/cast/{filename}"
        continue

    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data.get("results") and data["results"][0].get("profile_path"):
                img_url = "https://image.tmdb.org/t/p/w300" + data["results"][0]["profile_path"]
                img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(img_req) as img_resp:
                    with open(filepath, "wb") as f:
                        f.write(img_resp.read())
                results[name] = f"/static/images/cast/{filename}"
                print(f"[OK] Downloaded {name} -> {filepath}")
            else:
                print(f"[FAIL] No profile found for {name}")
    except Exception as e:
        print(f"[ERR] {name}: {e}")

print("Total cast mapped:", len(results))
with open("final_cast_mapping.json", "w") as f:
    json.dump(results, f, indent=2)
