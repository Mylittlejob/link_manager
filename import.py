import sys
import sqlite3
import csv


def init_database():
    conn = sqlite3.connect('sqlite.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS link (
            id INTEGER PRIMARY KEY,
            link TEXT UNIQUE,
            is_clicked INTEGER DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS link_log (
            link_id INTEGER,
            action TEXT,
            user_agent TEXT,
            ip_address TEXT,
            logged_at TEXT,
            FOREIGN KEY(link_id) REFERENCES link(id)
        )
    ''')
    conn.commit()
    conn.close()


def save_to_database(rows):
    init_database()
    conn = sqlite3.connect('sqlite.db')
    conn.executemany('INSERT INTO link (link) VALUES (?)', rows)
    conn.commit()
    conn.close()


def import_from_csv(file_path):
    with open(file_path) as csv_file:
        line_reader = csv.reader(csv_file)
        save_to_database([row for row in line_reader])


if __name__ == '__main__':
    import_from_csv(file_path=sys.argv[1])
