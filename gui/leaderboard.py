from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QListWidget, QPushButton, QWidget, QLineEdit,
                            QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt
import json
import os
import datetime
import urllib.request
import urllib.parse
from pathlib import Path
from aqt import mw
from ..constants import INITIAL_MONEY

SUPABASE_URL = "https://cbucgwfitimxvsayzpsa.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidWNnd2ZpdGlteHZzYXl6cHNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc2NTMwODksImV4cCI6MjA2MzIyOTA4OX0.Roosk0WMD2SG27iN-b_Shnge-wPlsgHNRXhflQRw2BQ"


def load_global_stats():
    """Load global stats from file"""
    try:
        profile_dir = Path(mw.pm.profileFolder())
        save_path = profile_dir / "collection.media/_anki_farm_tycoon_global_stats.json"
        
        if os.path.exists(save_path):
            with open(save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif not os.path.exists(save_path):
            profile_dir = Path(mw.pm.profileFolder())
            save_path = profile_dir / "anki_farm_tycoon_global_stats.json"
            if os.path.exists(save_path):
                with open(save_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        else:
            # Return default values if file doesn't exist
            return {
                "total_money_earned": INITIAL_MONEY
            }
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading global stats: {e}")
        # Return default values on error
        return {
            "total_money_earned": INITIAL_MONEY
        }


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anki Farm Tycoon")
        self.setFixedSize(400, 350)
        self.parent_window = parent
        
        layout = QVBoxLayout(self)
        
        # Beta version description
        beta_info = QTextEdit()
        beta_info.setReadOnly(True)
        beta_info.setMaximumHeight(80)
        beta_info.setPlainText(
            "🚧 BETA VERSION 🚧\n"
            "This is a beta version of the game. "
            "Please DO NOT use your real email address as username. "
            "Use a fictional username instead."
        )
        
        layout.addWidget(beta_info)
        
        # Username input
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. player123 (Do not use email address)")
        layout.addWidget(self.username_input)
        
        # Password input
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        layout.addWidget(self.password_input)
        
        # Error message display
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        self.login_button = QPushButton("Create Account & Login")
        self.login_button.clicked.connect(self.create_account)
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.login_button)
        layout.addWidget(QWidget())  # Spacer
        layout.addLayout(button_layout)
        
        # Enter key for login
        self.username_input.returnPressed.connect(self.create_account)
        self.password_input.returnPressed.connect(self.create_account)
    
    def validate_input(self, username, password):
        """Input validation"""
        errors = []
        
        # Username validation
        if not username or len(username.strip()) == 0:
            errors.append("Please enter a username")
        elif len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters")
        elif len(username.strip()) > 20:
            errors.append("Username must be 20 characters or less")
        elif "@" in username:
            errors.append("Please do not use email address as username")
        elif not username.replace("_", "").replace("-", "").isalnum():
            errors.append("Username can only contain letters, numbers, underscores, and hyphens")
        
        # Password validation
        if not password or len(password.strip()) == 0:
            errors.append("Please enter a password")
        elif len(password.strip()) < 6:
            errors.append("Password must be at least 6 characters")
        elif len(password.strip()) > 50:
            errors.append("Password must be 50 characters or less")
        
        return errors
    
    def create_account(self):
        """Account creation process"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Input validation
        validation_errors = self.validate_input(username, password)
        if validation_errors:
            self.error_label.setText("❌ " + "\n".join(validation_errors))
            return
        
        # Disable button and show processing state
        self.login_button.setEnabled(False)
        self.login_button.setText("Creating...")
        self.error_label.setText("Creating account...")
        self.error_label.setStyleSheet("color: blue; font-weight: bold;")
        
        try:
            # Load global stats to get initial settings
            global_stats = load_global_stats()
            
            # Create account with settings from global stats
            user_fields = {
                "name": username,
                "password": password,
                "money": global_stats.get("total_money_earned", INITIAL_MONEY),  # Use value from global stats
                "last_access": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add any additional fields from global stats
            if "default_settings" in global_stats:
                user_fields.update(global_stats["default_settings"])
            
            print(f"Creating user with fields: {user_fields}")  # Debug log
            
            result = create_user_data(user_fields)
            
            if result:
                # Success: Save credentials
                self.save_credentials(username, password)
                
                # Success message
                initial_money = user_fields.get("total_money_earned", INITIAL_MONEY)
                QMessageBox.information(
                    self,
                    "Account Created Successfully",
                    f"Account '{username}' has been created successfully!\nYou have been granted {initial_money:,} coins as starting funds."
                )
                
                # Refresh parent window
                if self.parent_window:
                    self.parent_window.refresh_data()
                
                self.accept()  # Close dialog
            else:
                # Failure (probably duplicate username)
                self.error_label.setText("❌ Username is already taken. Please try a different username.")
                self.error_label.setStyleSheet("color: red; font-weight: bold;")
                
        except Exception as e:
            # Error handling
            error_message = str(e)
            print(f"Account creation error: {error_message}")  # Debug log
            if "duplicate" in error_message.lower() or "unique" in error_message.lower():
                self.error_label.setText("❌ That username is already taken. Please enter a different username.")
            else:
                self.error_label.setText(f"❌ An error occurred while creating account. Please try again.\n({error_message})")
            self.error_label.setStyleSheet("color: red; font-weight: bold;")
        
        finally:
            # Re-enable button
            self.login_button.setEnabled(True)
            self.login_button.setText("Create Account & Login")
    
    def save_credentials(self, username, password):
        """Save authentication credentials"""
        try:
            profile_dir = Path(mw.pm.profileFolder())
            save_path = profile_dir / "collection.media/_anki_farm_tycoon_user_data.json"
            
            credentials = {
                "username": username,
                "password": password
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Credential save error: {e}")


class LeaderBoardWindow(QDialog):
    def __init__(self, leaderboard_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Leaderboard")
        self.setMinimumSize(400, 500)
        self.leaderboard_data = leaderboard_data
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # User info and login/logout section
        self.create_user_section(main_layout)
        
        # Ranking display section
        self.create_ranking_section(main_layout, leaderboard_data)
    
    def create_user_section(self, main_layout):
        """Create user info and login/logout button section"""
        user_section = QWidget()
        user_layout = QHBoxLayout(user_section)
        
        # Get user info
        user_info = self.get_user_credentials()
        
        if user_info and user_info.get("username") and user_info.get("password"):
            # Logged in: show username and logout button
            username_label = QLabel(f"User: {user_info['username']}")
            username_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
            logout_button = QPushButton("Logout")
            logout_button.clicked.connect(self.logout)
            logout_button.setMaximumWidth(100)
            
            user_layout.addWidget(username_label)
            user_layout.addStretch()  # Space between left and right align
            user_layout.addWidget(logout_button)
        else:
            # Not logged in: show login button
            login_button = QPushButton("Login")
            login_button.clicked.connect(self.show_login)
            login_button.setMaximumWidth(100)
            
            user_layout.addStretch()  # Center align
            user_layout.addWidget(login_button)
            user_layout.addStretch()  # Center align
        
        main_layout.addWidget(user_section)
        
        # Separator line
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cccccc; margin: 10px 0;")
        main_layout.addWidget(separator)
    
    def create_ranking_section(self, main_layout, leaderboard_data):
        """Create ranking display section"""
        # Ranking title
        title_label = QLabel("🏆 Leaderboard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Ranking list
        self.ranking_list = QListWidget()
        self.update_ranking_display(leaderboard_data)
        main_layout.addWidget(self.ranking_list)
    
    def update_ranking_display(self, leaderboard_data):
        """Update ranking list"""
        self.ranking_list.clear()
        
        # Sort data by money (descending)
        sorted_data = sorted(leaderboard_data, key=lambda x: x.get('money', 0), reverse=True)
        
        for i, entry in enumerate(sorted_data, 1):
            name = entry.get('name', 'Unknown')
            money = entry.get('money', 0)
            
            # Rank emoji based on position
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"#{i}"
            
            item_text = f"{rank_emoji} {name} - {money:,} coins"
            self.ranking_list.addItem(item_text)
    
    def get_user_credentials(self):
        """Get user authentication credentials"""
        try:
            profile_dir = Path(mw.pm.profileFolder())
            save_path = profile_dir / "collection.media/_anki_farm_tycoon_user_data.json"
            if os.path.exists(save_path):
                with open(save_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def logout(self):
        """Logout process"""
        try:
            profile_dir = Path(mw.pm.profileFolder())
            save_path = profile_dir / "collection.media/_anki_farm_tycoon_user_data.json"
            # Delete or clear credentials file
            if os.path.exists(save_path):
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump({"username": "", "password": ""}, f)
            
            # Refresh window
            self.refresh_data()
            
        except Exception as e:
            print(f"Logout error: {e}")
    
    def show_login(self):
        """Show login screen"""
        login_window = LoginWindow(self)
        login_window.exec()
    
    def refresh_data(self):
        """Re-fetch data and refresh window"""
        try:
            # Get latest user data
            new_data = get_user_data()
            if new_data:
                self.leaderboard_data = new_data
            
            # Rebuild UI
            # Clear existing widgets
            for i in reversed(range(self.layout().count())):
                widget = self.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Rebuild with new layout
            self.create_user_section(self.layout())
            self.create_ranking_section(self.layout(), self.leaderboard_data)
            
        except Exception as e:
            print(f"Data refresh error: {e}")


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

def update_user_data(name: str = "aa", password: str = "margomasdfe", update_fields: dict = {"money": 101000}):
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
        print(f"HTTP Error: {e.code} - {e.reason}") 
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