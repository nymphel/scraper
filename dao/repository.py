import mysql.connector


def insert_records(authors_filtered):
    db = mysql.connector.connect(
        host="localhost",
        user="ruya",
        password="testtest",
        database="scraper"
    )

    cursor = db.cursor()

    row_count = 0
    for author, titles in authors_filtered.items():
        for title in titles:
            sql = "INSERT INTO agenda_author_track (author, title) VALUES (%s, %s)"
            val = (author, title)
            cursor.execute(sql, val)
            row_count = row_count + 1

    db.commit()
    db.close()

    print(row_count, "record(s) inserted.")
