import subprocess
import sys
import os

git_path = os.path.join(os.path.dirname(__file__), "portable_git", "cmd", "git.exe")

print("="*60)
print("🎬 SHOWTIME GITHUB PUSH HELPER")
print("Repository: https://github.com/71382502139saieeswar-tony/showtime")
print("="*60)

token = os.environ.get("GITHUB_TOKEN", "")

if not token and len(sys.argv) > 1:
    token = sys.argv[1]

if token:
    remote_url = f"https://{token}@github.com/71382502139saieeswar-tony/showtime.git"
    print("Pushing using provided GitHub Access Token...")
    res = subprocess.run([git_path, "push", "-u", remote_url, "main", "--force"], capture_output=True, text=True)
    print(res.stdout)
    print(res.stderr)
    if res.returncode == 0:
        print("\n✅ SUCCESS! Project successfully pushed to GitHub!")
    else:
        print("\n❌ Push failed. Please check token permissions.")
else:
    print("\nTo push instantly with a GitHub Personal Access Token (PAT), run:")
    print("   python push_repo.py <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>")
    print("\nOr run portable_git\\cmd\\git.exe push -u origin main directly in terminal.")
