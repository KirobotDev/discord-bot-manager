def save_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()