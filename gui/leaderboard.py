from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget
import json
import datetime
import urllib.request
import urllib.parse

SUPABASE_URL = "https://cbucgwfitimxvsayzpsa.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidWNnd2ZpdGlteHZzYXl6cHNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc2NTMwODksImV4cCI6MjA2MzIyOTA4OX0.Roosk0WMD2SG27iN-b_Shnge-wPlsgHNRXhflQRw2BQ"


class LeaderBoardWindow(QDialog):
    def __init__(self, leaderboard_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Leader Board")
        self.setMinimumSize(300, 400)
        layout = QVBoxLayout(self)

        label = QLabel("Top Players", self)
        layout.addWidget(label)

        self.list_widget = QListWidget(self)
        for entry in leaderboard_data:
            self.list_widget.addItem(
                f"{entry['name']} - {entry['money']} coins"
            )
        layout.addWidget(self.list_widget)


def get_user_data():
    url = f"{SUPABASE_URL}/rest/v1/users?select=name,money,last_access"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as response:
        result = response.read().decode()
        return json.loads(result)

def update_user_data( name: str = "aa", password: str = "margomasdfe", update_fields: dict = {"money": 101000}):
    print("update_user_data------")
    url = (
        f"{SUPABASE_URL}/rest/v1/users"
        f"?name=eq.{urllib.parse.quote(name)}"
        "&select=name,money,last_access" 
    )
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
        "x-user-name": name,
        "x-user-password": password,
    }


    data = json.dumps(update_fields).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            return json.loads(result)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}") # エラーコードと理由を確認
        return None


def create_user_data(user_fields = {"name":"aa", "password":"margomasdfe", "money":100,"last_access":datetime.datetime.now().strftime("%Y-%m-%d")}):
    print("create User data-------")
    url = f"{SUPABASE_URL}/rest/v1/users?select=name,money,last_access"

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    data = json.dumps(user_fields).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            return json.loads(result)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None
    

def delete_user_data(user_name = "2213"):
    print("delete_user_data------")
    url = f"{SUPABASE_URL}/rest/v1/users?name=eq.{user_name}"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Accept": "application/json",
        "Prefer": "return=representation"
    }

    req = urllib.request.Request(url, headers=headers, method="DELETE")

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            return json.loads(result) if result else None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None