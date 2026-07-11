import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nandita",
    database="ascendpilot"
)

cursor = db.cursor(buffered=True)