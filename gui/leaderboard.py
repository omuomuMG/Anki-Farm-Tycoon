from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget

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
                f"{entry['player']} - {entry['score']} coins, {entry['day']} days"
            )
        layout.addWidget(self.list_widget)


import urllib.request
import urllib.parse
import json

SUPABASE_URL = "https://cbucgwfitimxvsayzpsa.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidWNnd2ZpdGlteHZzYXl6cHNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc2NTMwODksImV4cCI6MjA2MzIyOTA4OX0.Roosk0WMD2SG27iN-b_Shnge-wPlsgHNRXhflQRw2BQ"

def get_user_data(name = "omuomu", password=1):

    url = f"{SUPABASE_URL}/rest/v1/users?name=eq.{name}"


    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            return json.loads(result)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None


