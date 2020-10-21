import mysql.connector


def insert_records(authors_filtered):
    db = mysql.connector.connect(
        host="localhost",
        user="ruya",
        password="testtest",
        database="scraper"
    )

    cursor = db.cursor()

    for author, titles in authors_filtered.items():
        for title in titles:
            sql = "INSERT INTO agenda_author_track (author, title) VALUES (%s, %s)"
            val = (author, title)
            cursor.execute(sql, val, multi=True)

    db.commit()
    db.close()
