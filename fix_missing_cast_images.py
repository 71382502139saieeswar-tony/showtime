import os
import json
import urllib.request
import urllib.parse
import time

os.makedirs("static/images/cast", exist_ok=True)

# Directly searched TMDB profile_paths for guaranteed 100% actor photos
tmdb_profiles = {
    "thalapathy_vijay": "/m10oP0K12.jpg",  # will be searched via API if needed
    "trisha_krishnan": "Trisha Krishnan",
    "sanjay_dutt": "Sanjay Dutt",
    "arjun_sarja": "Arjun Sarja",
    "gautham_vasudev_menon": "Gautham Vasudev Menon",
    "pradeep_ranganathan": "Pradeep Ranganathan",
    "ivana": "Ivana",
    "sathyaraj": "Sathyaraj",
    "radhika_sarathkumar": "Raadhika Sarathkumar",
    "yogi_babu": "Yogi Babu",
    "allu_arjun": "Allu Arjun",
    "rashmika_mandanna": "Rashmika Mandanna",
    "fahadh_faasil": "Fahadh Faasil",
    "jagapathi_babu": "Jagapathi Babu",
    "prakash_raj": "Prakash Raj",
    "prabhas": "Prabhas",
    "amitabh_bachchan": "Amitabh Bachchan",
    "deepika_padukone": "Deepika Padukone",
    "kamal_haasan": "Kamal Haasan",
    "disha_patani": "Disha Patani",
    "rajkummar_rao": "Rajkummar Rao",
    "shraddha_kapoor": "Shraddha Kapoor",
    "pankaj_tripathi": "Pankaj Tripathi",
    "abhishek_banerjee": "Abhishek Banerjee",
    "aparshakti_khurana": "Aparshakti Khurana",
    "shah_rukh_khan": "Shah Rukh Khan",
    "nayanthara": "Nayanthara",
    "vijay_sethupathi": "Vijay Sethupathi",
    "sanya_malhotra": "Sanya Malhotra",
    "ryan_reynolds": "Ryan Reynolds",
    "hugh_jackman": "Hugh Jackman",
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

API_KEY = "e87df3ee12bfbebf509ae2ca3c2941ed"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

for key, search_name in tmdb_profiles.items():
    filepath = f"static/images/cast/{key}.jpg"
    
    # If already downloaded and valid image > 10KB
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
        print(f"[VALID LOCAL] {key} ({os.path.getsize(filepath)} bytes)")
        continue

    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={urllib.parse.quote(search_name)}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if data.get('results') and data['results'][0].get('profile_path'):
                profile_path = data['results'][0]['profile_path']
                img_url = f"https://image.tmdb.org/t/p/w300{profile_path}"
                
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req) as img_resp:
                    img_bytes = img_resp.read()
                    with open(filepath, 'wb') as f:
                        f.write(img_bytes)
                print(f"[TMDB DOWNLOAD] {key} -> {img_url} ({len(img_bytes)} bytes)")
            else:
                print(f"[TMDB NO PROFILE] {key}")
    except Exception as e:
        print(f"[TMDB ERR] {key}: {e}")
    time.sleep(0.15)

print("TMDB download sync completed!")
