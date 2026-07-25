import sqlite3
from datetime import datetime

DB_NAME = "backlinks.db"

def init_db():
    """Creates the backlinks and clients tables if they don't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_site TEXT NOT NULL,
            target_site TEXT NOT NULL,
            platform TEXT NOT NULL,
            published_url TEXT NOT NULL,
            anchor_text TEXT,
            article_content TEXT,
            date_published TEXT NOT NULL,
            status TEXT DEFAULT 'live'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            site_url TEXT NOT NULL UNIQUE,
            niche TEXT,
            date_added TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_backlink(client_site, target_site, platform, published_url, anchor_text, article_content=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO backlinks (client_site, target_site, platform, published_url, anchor_text, article_content, date_published)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client_site, target_site, platform, published_url, anchor_text, article_content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_backlinks():
    """Returns all saved backlinks."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backlinks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_backlink_status(backlink_id, status):
    """Updates the status of a specific backlink."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE backlinks SET status = ? WHERE id = ?
    """, (status, backlink_id))
    conn.commit()
    conn.close()

def get_backlink_by_id(backlink_id):
    """Fetches a single backlink record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backlinks WHERE id = ?", (backlink_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def count_todays_backlinks(client_site):
    """Counts how many backlinks were published today for a given client."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM backlinks 
        WHERE client_site = ? 
        AND date(date_published) = date('now')
    """, (client_site,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_anchor_history(client_site):
    """Returns all anchor texts previously used for a given client."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT anchor_text, published_url, date_published 
        FROM backlinks 
        WHERE client_site = ?
        ORDER BY date_published DESC
    """, (client_site,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def check_anchor_diversity(client_site, proposed_anchor_text):
    """Checks if the proposed anchor text was already used for this client."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM backlinks 
        WHERE client_site = ? AND anchor_text = ?
    """, (client_site, proposed_anchor_text))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def add_client(name, site_url, niche):
    """Adds a new client to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO clients (name, site_url, niche, date_added)
            VALUES (?, ?, ?, ?)
        """, (name, site_url, niche, datetime.now().isoformat()))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # site_url already exists (UNIQUE constraint)
    conn.close()
    return success

def get_all_clients():
    """Returns all saved clients."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    rows = cursor.fetchall()
    conn.close()
    return rows

def generate_client_report(client_site):
    """Generates a summary report for a given client's backlinks."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT published_url, target_site, anchor_text, date_published, status
        FROM backlinks
        WHERE client_site = ?
        ORDER BY date_published DESC
    """, (client_site,))
    links = cursor.fetchall()
    
    cursor.execute("""
        SELECT COUNT(*) FROM backlinks WHERE client_site = ? AND status = 'live'
    """, (client_site,))
    live_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM backlinks WHERE client_site = ?
    """, (client_site,))
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "client_site": client_site,
        "total_backlinks": total_count,
        "live_backlinks": live_count,
        "links": links
    }


def get_previous_articles(client_site):
    """Returns all previously saved article texts for a given client."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT article_content FROM backlinks 
        WHERE client_site = ? AND article_content != ''
    """, (client_site,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]