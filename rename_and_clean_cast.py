import os
import shutil

cast_dir = "static/images/cast"

copies = {
    "allu.jpg": "allu_arjun.jpg",
    "deepika.jpg": "deepika_padukone.jpg",
    "disha.jpg": "disha_patani.jpg",
    "fahadh.jpg": "fahadh_faasil.jpg",
    "hugh.jpg": "hugh_jackman.jpg",
    "jagapathi.jpg": "jagapathi_babu.jpg",
    "kamal.jpg": "kamal_haasan.jpg",
    "pankaj.jpg": "pankaj_tripathi.jpg",
    "rashmika.jpg": "rashmika_mandanna.jpg",
    "sanya.jpg": "sanya_malhotra.jpg",
    "shah.jpg": "shah_rukh_khan.jpg",
    "shraddha.jpg": "shraddha_kapoor.jpg",
    "vijay.jpg": "vijay_sethupathi.jpg"
}

for src_name, dst_name in copies.items():
    src_path = os.path.join(cast_dir, src_name)
    dst_path = os.path.join(cast_dir, dst_name)
    if os.path.exists(src_path) and os.path.getsize(src_path) > 5000:
        if src_path != dst_path:
            shutil.copyfile(src_path, dst_path)
            print(f"Copied {src_name} -> {dst_name} ({os.path.getsize(dst_path)} bytes)")

print("Cast file clean complete!")
