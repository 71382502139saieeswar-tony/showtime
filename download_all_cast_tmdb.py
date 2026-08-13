import os
import json
import urllib.request
import urllib.parse
import time

os.makedirs("static/images/cast", exist_ok=True)

api_key = "15d2aea6731d814249344628f4f7335b"

actors = {
    # Leo
    "thalapathy_vijay": "Joseph Vijay",
    "trisha_krishnan": "Trisha Krishnan",
    "sanjay_dutt": "Sanjay Dutt",
    "arjun_sarja": "Arjun Sarja",
    "gautham_vasudev_menon": "Gautham Vasudev Menon",

    # Love Today
    "pradeep_ranganathan": "Pradeep Ranganathan",
    "ivana": "Ivana",
    "sathyaraj": "Sathyaraj",
    "radhika_sarathkumar": "Raadhika Sarathkumar",
    "yogi_babu": "Yogi Babu",

    # Pushpa 2
    "allu_arjun": "Allu Arjun",
    "rashmika_mandanna": "Rashmika Mandanna",
    "fahadh_faasil": "Fahadh Faasil",
    "jagapathi_babu": "Jagapathi Babu",
    "prakash_raj": "Prakash Raj",

    # Kalki 2898 AD
    "prabhas": "Prabhas",
    "amitabh_bachchan": "Amitabh Bachchan",
    "deepika_padukone": "Deepika Padukone",
    "kamal_haasan": "Kamal Haasan",
    "disha_patani": "Disha Patani",

    # Stree 2
    "rajkummar_rao": "Rajkummar Rao",
    "shraddha_kapoor": "Shraddha Kapoor",
    "pankaj_tripathi": "Pankaj Tripathi",
    "abhishek_banerjee": "Abhishek Banerjee",
    "aparshakti_khurana": "Aparshakti Khurana",

    # Jawan
    "shah_rukh_khan": "Shah Rukh Khan",
    "nayanthara": "Nayanthara",
    "vijay_sethupathi": "Vijay Sethupathi",
    "sanya_malhotra": "Sanya Malhotra",

    # Hollywood
    "ryan_reynolds": "Ryan Reynolds",
    "hugh_jackman": "Hugh Jackman",
    "emma_corrin": "Emma Corrin",
    "shameik_moore": "Shameik Moore",
    "hailee_steinfeld": "Hailee Steinfeld",
    "sam_worthington": "Sam Worthington",
    "zoe_saldana": "Zoe Saldana",
    "cillian_murphy": "Cillian Murphy",
    "emily_blunt": "Emily Blunt",
    "matt_damon": "Matt Damon",
    "robert_downey_jr": "Robert Downey Jr.",
    "florence_pugh": "Florence Pugh",
    "timothee_chalamet": "Timothée Chalamet",
    "zendaya": "Zendaya",
    "christian_bale": "Christian Bale",
    "heath_ledger": "Heath Ledger"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}

for key, query in actors.items():
    filepath = f"static/images/cast/{key}.jpg"
    
    # Force redownload if file is smaller than 5KB
    if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
        print(f"[EXISTS VALID] {key} ({os.path.getsize(filepath)} bytes)")
        continue

    url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data.get("results") and data["results"][0].get("profile_path"):
                profile_path = data["results"][0]["profile_path"]
                img_url = f"https://image.tmdb.org/t/p/w300{profile_path}"
                
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req) as img_resp:
                    img_data = img_resp.read()
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                print(f"[TMDB SUCCESS] {key} -> {len(img_data)} bytes")
            else:
                print(f"[TMDB NO RESULT] {key}")
    except Exception as e:
        print(f"[TMDB ERR] {key}: {e}")
    time.sleep(0.15)

print("TMDB cast download completed!")
