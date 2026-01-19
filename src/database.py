"""
Database operations for user data and itineraries
"""
import sqlite3
import os
from datetime import datetime
import json
from typing import List, Dict, Optional

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path='data/user_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Itineraries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itineraries (
                itinerary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                destination TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                content_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
                # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                messages_json TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def save_conversation(self, user_id: str, messages: list, metadata: dict = None):
        """Save a conversation to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conversation_data = json.dumps(messages)
        # Use 'messages' column instead of 'conversation_data'
        cursor.execute('''
            INSERT INTO conversations (user_id, messages)
            VALUES (?, ?)
        ''', (user_id, conversation_data))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversation_id


    
    def get_user_conversations(self, user_id, limit=10):
        """
        Get recent conversations for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
        """
        import json
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conversation_id, messages_json, metadata, timestamp
            FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'messages': json.loads(row[1]),
                'metadata': json.loads(row[2]) if row[2] else None,
                'timestamp': row[3]
            })
        
        conn.close()
        return conversations
    
    def save_itinerary(self, user_id, destination, start_date, end_date, budget, content):
        """
        Save a travel itinerary
        
        Args:
            user_id: User identifier
            destination: Destination name
            start_date: Start date (string)
            end_date: End date (string)
            budget: Budget amount
            content: Itinerary content (JSON string)
        """
        import json
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        content_json = json.dumps(content) if isinstance(content, dict) else content
        
        cursor.execute('''
            INSERT INTO itineraries (user_id, destination, start_date, end_date, budget, content_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, destination, start_date, end_date, budget, content_json))
        
        itinerary_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return itinerary_id
    
    def get_user_itineraries(self, user_id):
        """
        Get all itineraries for a user
        
        Args:
            user_id: User identifier
        """
        import json
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT itinerary_id, destination, start_date, end_date, budget, content_json, created_at
            FROM itineraries
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        itineraries = []
        for row in cursor.fetchall():
            itineraries.append({
                'id': row[0],
                'destination': row[1],
                'start_date': row[2],
                'end_date': row[3],
                'budget': row[4],
                'content': json.loads(row[5]) if row[5] else None,
                'created_at': row[6]
            })
        
        conn.close()
        return itineraries

