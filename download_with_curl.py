import subprocess
import os

os.makedirs("static/images/cast", exist_ok=True)

# Directly mapped Wikipedia/Wikimedia image URLs
cast_urls = {
    "trisha_krishnan": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Trisha_Krishnan_at_South_Indian_International_Movie_Awards_2023.jpg/330px-Trisha_Krishnan_at_South_Indian_International_Movie_Awards_2023.jpg",
    "ivana": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Ivana_at_Love_Today_Thanks_Meet.jpg/330px-Ivana_at_Love_Today_Thanks_Meet.jpg",
    "radhika_sarathkumar": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Radhika_Sarathkumar_at_Siima_2016.jpg/330px-Radhika_Sarathkumar_at_Siima_2016.jpg",
    "allu_arjun": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Allu_Arjun_at_Pushpa_press_meet.jpg/330px-Allu_Arjun_at_Pushpa_press_meet.jpg",
    "rashmika_mandanna": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Rashmika_Mandanna_at_Siima_2021.jpg/330px-Rashmika_Mandanna_at_Siima_2021.jpg",
    "jagapathi_babu": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Jagapathi_Babu_at_legend_press_meet.jpg/330px-Jagapathi_Babu_at_legend_press_meet.jpg",
    "prabhas": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Prabhas_at_Saaho_trailer_launch.jpg/330px-Prabhas_at_Saaho_trailer_launch.jpg",
    "deepika_padukone": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Deepika_Padukone_Cannes_2018_%28cropped%29.jpg/330px-Deepika_Padukone_Cannes_2018_%28cropped%29.jpg",
    "kamal_haasan": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Kamal_Haasan_at_Indian_2_Audio_Launch.jpg/330px-Kamal_Haasan_at_Indian_2_Audio_Launch.jpg",
    "disha_patani": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Disha_Patani_promoting_Ek_Villain_Returns.jpg/330px-Disha_Patani_promoting_Ek_Villain_Returns.jpg",
    "shraddha_kapoor": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Shraddha_Kapoor_promoting_Tu_Jhoothi_Main_Makkaar.jpg/330px-Shraddha_Kapoor_promoting_Tu_Jhoothi_Main_Makkaar.jpg",
    "pankaj_tripathi": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Pankaj_Tripathi_at_IFFI_2019.jpg/330px-Pankaj_Tripathi_at_IFFI_2019.jpg",
    "abhishek_banerjee": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Abhishek_Banerjee_actor.jpg/330px-Abhishek_Banerjee_actor.jpg",
    "aparshakti_khurana": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Aparshakti_Khurana_at_screening.jpg/330px-Aparshakti_Khurana_at_screening.jpg",
    "shah_rukh_khan": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Shah_Rukh_Khan_graces_the_launch_of_the_new_sanitary_brand_%27Hygiene_Plus%27_%28cropped%29.jpg/330px-Shah_Rukh_Khan_graces_the_launch_of_the_new_sanitary_brand_%27Hygiene_Plus%27_%28cropped%29.jpg",
    "nayanthara": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Nayanthara_at_Jawan_Pre-Release_Event.jpg/330px-Nayanthara_at_Jawan_Pre-Release_Event.jpg",
    "vijay_sethupathi": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Vijay_Sethupathi_at_Jawan_Pre-Release_Event.jpg/330px-Vijay_Sethupathi_at_Jawan_Pre-Release_Event.jpg",
    "sanya_malhotra": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Sanya_Malhotra_at_Jawan_Pre-Release.jpg/330px-Sanya_Malhotra_at_Jawan_Pre-Release.jpg",
    "hugh_jackman": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Logan_Japan_Premiere_Red_Carpet_Hugh_Jackman_%28cropped%29.jpg/330px-Logan_Japan_Premiere_Red_Carpet_Hugh_Jackman_%28cropped%29.jpg",
    "cillian_murphy": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Cillian_Murphy_2014.jpg/330px-Cillian_Murphy_2014.jpg",
    "emily_blunt": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Emily_Blunt_2018.jpg/330px-Emily_Blunt_2018.jpg",
    "matt_damon": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Matt_Damon_2014.jpg/330px-Matt_Damon_2014.jpg",
    "florence_pugh": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Florence_Pugh_2019.jpg/330px-Florence_Pugh_2019.jpg",
    "timothee_chalamet": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Timoth%C3%A9e_Chalamet_2019.jpg/330px-Timoth%C3%A9e_Chalamet_2019.jpg",
    "christian_bale": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Christian_Bale-7834.jpg/330px-Christian_Bale-7834.jpg",
    "heath_ledger": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Heath_Ledger_%282007%29.jpg/330px-Heath_Ledger_%282007%29.jpg"
}

for key, url in cast_urls.items():
    filepath = f"static/images/cast/{key}.jpg"
    cmd = ["curl.exe", "-s", "-L", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", url, "-o", filepath]
    try:
        subprocess.run(cmd, check=True)
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        print(f"[CURL OK] {key} -> {size} bytes")
    except Exception as e:
        print(f"[CURL ERR] {key}: {e}")

print("Curl download complete!")
