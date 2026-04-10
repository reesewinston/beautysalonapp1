import mysql.connector


def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="appuser",
        password="AppPass123!",
        database="beauty_booking_system"
    )