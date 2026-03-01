#!/usr/bin/env python3
"""
Simple test script for the workout session API endpoints.
This demonstrates how to save and retrieve workout sessions.
"""

import sqlite3
from datetime import datetime

DB_NAME = 'workouts.db'

def test_direct_db_insert():
    """Test inserting data directly into the database."""
    print("Testing direct database insertion...")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert test session
    trained_at = datetime.now().isoformat()
    total_jumps = 75
    round_count = 3

    cursor.execute('''
        INSERT INTO sessions (trained_at, total_jumps, round_count)
        VALUES (?, ?, ?)
    ''', (trained_at, total_jumps, round_count))

    session_id = cursor.lastrowid
    print(f"✓ Inserted session with ID: {session_id}")

    # Insert rounds
    rounds = [25, 30, 20]
    for index, jumps in enumerate(rounds, start=1):
        cursor.execute('''
            INSERT INTO rounds (session_id, round_index, jumps)
            VALUES (?, ?, ?)
        ''', (session_id, index, jumps))

    print(f"✓ Inserted {len(rounds)} rounds")

    conn.commit()

    # Retrieve and verify
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    print(f"✓ Retrieved session: {session}")

    cursor.execute('SELECT * FROM rounds WHERE session_id = ?', (session_id,))
    rounds_data = cursor.fetchall()
    print(f"✓ Retrieved rounds: {rounds_data}")

    conn.close()
    print("\nDatabase operations successful!\n")

def display_all_sessions():
    """Display all sessions from the database."""
    print("All workout sessions in database:")
    print("=" * 60)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM sessions ORDER BY trained_at DESC')
    sessions = cursor.fetchall()

    if not sessions:
        print("No sessions found.")

    for session in sessions:
        print(f"\nSession ID: {session['id']}")
        print(f"  Date: {session['trained_at']}")
        print(f"  Total Jumps: {session['total_jumps']}")
        print(f"  Rounds: {session['round_count']}")

        cursor.execute('SELECT * FROM rounds WHERE session_id = ? ORDER BY round_index',
                      (session['id'],))
        rounds = cursor.fetchall()

        print("  Round Details:")
        for r in rounds:
            print(f"    Round {r['round_index']}: {r['jumps']} jumps")

    conn.close()
    print("\n" + "=" * 60)

if __name__ == '__main__':
    print("Workout Session Database Test\n")
    test_direct_db_insert()
    display_all_sessions()

    print("\nAPI Testing Instructions:")
    print("-" * 60)
    print("1. Start the Flask server:")
    print("   python web_app.py")
    print("\n2. In another terminal, test POST endpoint:")
    print('   curl -X POST http://127.0.0.1:5000/api/sessions \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"total_jumps": 100, "rounds": [30, 35, 35]}\'')
    print("\n3. Test GET endpoint:")
    print("   curl http://127.0.0.1:5000/api/sessions")
    print("-" * 60)
