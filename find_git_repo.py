import os
import subprocess

git_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"

curr = r"c:\Users\Adan\Documents\Anti-POS_Project"
while curr and len(curr) > 3:
    dot_git = os.path.join(curr, ".git")
    if os.path.exists(dot_git):
        print("Found .git at:", dot_git)
        res = subprocess.run([git_path, "status"], cwd=curr, capture_output=True, text=True)
        print("git status output:\n", res.stdout)
        break
    curr = os.path.dirname(curr)
