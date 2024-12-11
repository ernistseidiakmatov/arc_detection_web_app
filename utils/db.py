import sqlite3
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import time

class DatabaseManager:
    def __init__(self, db_path="arc_predictions.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS arc_predictions (
                timestamp TEXT PRIMARY KEY,
                prediction INT
            )
        """)
        self.conn.commit()

    def save_arc_prediction(self, prediction):
        timestamp = datetime.now()
        
        try:
            self.cursor.execute(
                "INSERT INTO arc_predictions (timestamp, prediction) VALUES (?, ?)",
                (timestamp.isoformat(), prediction,)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def get_arc_predictions(self, time_period_minutes):
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_period_minutes)
        
        self.cursor.execute("""
            SELECT timestamp, prediction FROM arc_predictions
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (start_time.isoformat(), end_time.isoformat()))
        rows = self.cursor.fetchall()
        timestamps = [datetime.fromisoformat(row[0]) for row in rows]
        predictions = [row[1] for row in rows]

        return timestamps, predictions
        
    def close(self):
        self.conn.close()