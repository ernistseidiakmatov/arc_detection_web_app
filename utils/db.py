import sqlite3
from datetime import datetime, timedelta
import random
import time

class DatabaseManager:
    def __init__(self, db_path="arc_predictions.db"):
        """Initialize the database connection and create the table."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Create the table for storing Arc predictions."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS arc_predictions (
                timestamp TEXT PRIMARY KEY,
                prediction INT
            )
        """)
        self.conn.commit()

    def save_arc_prediction(self, prediction):
        """Save an Arc prediction (class 1) with its timestamp."""
        timestamp = datetime.now()  # Use current timestamp if not provided
        
        try:
            self.cursor.execute(
                "INSERT INTO arc_predictions (timestamp, prediction) VALUES (?, ?)",
                (timestamp.isoformat(), prediction,)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Ignore duplicate entries
            pass

    def get_arc_predictions(self, time_period_minutes):
        """Retrieve Arc predictions within a specified time range."""
        end_time = datetime.now()  # Current time
        start_time = end_time - timedelta(minutes=time_period_minutes)  # Start time based on the duration
        
        self.cursor.execute("""
            SELECT timestamp, prediction FROM arc_predictions
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (start_time.isoformat(), end_time.isoformat()))
        rows = self.cursor.fetchall()
        
        # res = [(datetime.fromisoformat(row[0]), row[1]) for row in rows]
        # timestamps, predictions = zip(*res) 
        # return timestamps, predictions
        timestamps = [datetime.fromisoformat(row[0]) for row in rows]
        predictions = [row[1] for row in rows]

        return timestamps, predictions
        
    def close(self):
        """Close the database connection."""
        self.conn.close()