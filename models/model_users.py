import sys
import os

from utils import db

class User:
    def __init__(self, user_id, username, first_name, last_name, language_code):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language_code = language_code
        
    def save(self):
        db.save_user(self.user_id, self.username, self.first_name, self.last_name, self.language_code)
        