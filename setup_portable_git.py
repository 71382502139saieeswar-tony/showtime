import urllib.request
import zipfile
import os

git_dir = os.path.join(os.path.dirname(__file__), "portable_git")
zip_path = os.path.join(os.path.dirname(__file__), "mingit.zip")

if not os.path.exists(git_dir):
    print("Downloading Portable MinGit binary...")
    url = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/MinGit-2.43.0-64-bit.zip"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as resp:
        with open(zip_path, 'wb') as f:
            f.write(resp.read())
    print("Extracting MinGit...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(git_dir)
    os.remove(zip_path)
    print("Portable MinGit ready at:", git_dir)
else:
    print("Portable MinGit already exists at:", git_dir)

git_cmd = os.path.join(git_dir, "cmd", "git.exe")
print("Git executable path:", git_cmd)
