import os
import json
import urllib.request
import urllib.parse

os.makedirs("static/images/cast", exist_ok=True)

actors = {
    "Vijay": "Vijay (actor)",
    "Trisha Krishnan": "Trisha (actress)",
    "Sanjay Dutt": "Sanjay Dutt",
    "Arjun Sarja": "Arjun Sarja",
    "Gautham Vasudev Menon": "Gautham Vasudev Menon",
    "Pradeep Ranganathan": "Pradeep Ranganathan",
    "Ivana": "Ivana (actress)",
    "Sathyaraj": "Sathyaraj",
    "Radhika Sarathkumar": "Raadhika Sarathkumar",
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
    "Shah Rukh Khan": "Shah Rukh Khan",
    "Nayanthara": "Nayanthara",
    "Vijay Sethupathi": "Vijay Sethupathi",
    "Sanya Malhotra": "Sanya Malhotra",
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
    "Stephen Lang": "Stephen Lang",
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
    "Morgan Freeman": "Morgan Freeman"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ShowTimeApp/1.0'}

results = {}

for name, wiki_title in actors.items():
    safe_filename = name.lower().replace(' ', '_').replace('.', '').replace('é', 'e') + ".jpg"
    filepath = os.path.join("static/images/cast", safe_filename)
    
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(wiki_title)}&prop=pageimages&format=json&pithumbsize=400"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data['query']['pages']
            img_url = None
            for p_id in pages:
                if 'thumbnail' in pages[p_id]:
                    img_url = pages[p_id]['thumbnail']['source']
                    break
            
            if img_url:
                # Download to local file
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req) as img_resp:
                    with open(filepath, 'wb') as f:
                        f.write(img_resp.read())
                results[name] = f"/static/images/cast/{safe_filename}"
                print(f"[OK] Downloaded {name} -> /static/images/cast/{safe_filename}")
            else:
                print(f"[WARN] No thumbnail found for {name}")
    except Exception as e:
        print(f"[ERROR] {name}: {e}")

print("Done! Total downloaded:", len(results))

with open("cast_mapping.json", "w") as f:
    json.dump(results, f, indent=2)
