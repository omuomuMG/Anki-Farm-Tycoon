import datetime
from aqt import mw
import json
from pathlib import Path
import os

from ..constants import INITIAL_MONEY
from ..gui.leaderboard import get_user_credentials, load_global_stats, update_user_data

def on_sync_complete():
    """Sync completion handler - update user data if logged in"""
    try:
        # Check if user data file exists and has valid credentials
        user_info = get_user_credentials()
        
        if user_info and user_info.get("username") and user_info.get("password"):
            username = user_info["username"]
            password = user_info["password"]
            
            print(f"Sync completed - updating data for user: {username}")
            
            # Load global stats to get current progress
            global_stats = load_global_stats()
            
            # Prepare update fields based on current progress
            update_fields = {
                "money": global_stats.get("total_money_earned", INITIAL_MONEY),
                "last_access": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Call update_user_data
            result = update_user_data(username, password, update_fields)
            
            if result:
                print(f"Successfully updated user data for {username}")
            else:
                print(f"Failed to update user data for {username}")
                
        else:
            print("No valid user credentials found - skipping sync update")
            
    except Exception as e:
        print(f"Error in sync completion handler: {e}")

