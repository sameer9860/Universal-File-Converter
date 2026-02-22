import os

files_to_fix = [
    "py7zr", "django-admin", "pip3", "f2py", "sqlformat", "numpy-config",
    "pasteurize", "activate.csh", "activate", "futurize", "activate.fish",
    "pip3.12", "pip"
]
base_dir = "/home/samir/Universal-File-Converter/venv/bin"

for f in files_to_fix:
    path = os.path.join(base_dir, f)
    with open(path, "r") as file:
        content = file.read()
    content = content.replace("Libre-To-Office-Converter", "Universal-File-Converter")
    with open(path, "w") as file:
        file.write(content)

print("Fixed venv paths successfully.")
