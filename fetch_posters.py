import urllib.request
import urllib.parse
import json

api_key = "15d2aea6731d814249344628f4f7335b"
movies = [
    "Pushpa 2: The Rule",
    "Kalki 2898 AD",
    "Stree 2",
    "Deadpool & Wolverine",
    "Spider-Man: Across the Spider-Verse",
    "Avatar: The Way of Water",
    "Oppenheimer",
    "Dune: Part Two",
    "The Dark Knight",
    "Jawan"
]

results = {}
for m in movies:
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={urllib.parse.quote(m)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            if data.get("results"):
                first = data["results"][0]
                p_path = first.get("poster_path")
                b_path = first.get("backdrop_path")
                results[m] = {
                    "poster_url": f"https://image.tmdb.org/t/p/w500{p_path}" if p_path else "",
                    "backdrop_url": f"https://image.tmdb.org/t/p/original{b_path}" if b_path else ""
                }
                print(f"SUCCESS: {m} -> Poster: {results[m]['poster_url']}")
            else:
                print(f"NO RESULT: {m}")
    except Exception as e:
        print(f"ERROR {m}: {e}")

with open("tmdb_movies.json", "w") as f:
    json.dump(results, f, indent=2)
