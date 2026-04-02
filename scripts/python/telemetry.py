# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Warden Telemetry Dashboard.

Reads and reports compression telemetry metrics from the
local SQLite database (~/.rura/telemetry.db).

Deployment Profile: Profile A (Edge / Mission Compute)
"""
import sys
import sqlite3
import json
from pathlib import Path

def get_db_path() -> Path:
    return Path.home() / ".rura" / "telemetry.db"

def main():
    db_path = get_db_path()
    if not db_path.exists():
        # Output clean JSON for the agent indicating no data yet
        print(json.dumps({"status": "empty", "message": "No telemetry database found. Compress contexts using /warden.compress first!"}, indent=2))
        sys.exit(0)
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ensure the table actually exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='compression_logs'")
        if not cursor.fetchone():
            print(json.dumps({"status": "empty", "message": "Telemetry database found, but no compression logs exist yet."}, indent=2))
            conn.close()
            sys.exit(0)
            
        # Global Totals
        cursor.execute('''
            SELECT 
                COUNT(*) as total_runs, 
                SUM(original_tokens) as total_orig, 
                SUM(compressed_tokens) as total_comp, 
                SUM(tokens_saved) as total_saved 
            FROM compression_logs
        ''')
        row = cursor.fetchone()
        
        total_runs = row[0] or 0
        total_original = row[1] or 0
        total_compressed = row[2] or 0
        total_saved = row[3] or 0
        
        avg_savings_pct = 0.0
        if total_original > 0:
            avg_savings_pct = 100.0 * (total_saved / total_original)
            
        # Top 5 most massive compressions
        cursor.execute('''
            SELECT target_file, original_tokens, tokens_saved, timestamp
            FROM compression_logs
            ORDER BY tokens_saved DESC
            LIMIT 5
        ''')
        top_saves = cursor.fetchall()
        
        # Most recent 5 compressions
        cursor.execute('''
            SELECT target_file, original_tokens, compressed_tokens, tokens_saved, timestamp
            FROM compression_logs
            ORDER BY id DESC
            LIMIT 5
        ''')
        recent_logs = cursor.fetchall()
        
        conn.close()
        
        output = {
            "status": "success",
            "global_metrics": {
                "total_compressions": total_runs,
                "total_original_tokens": total_original,
                "total_compressed_tokens": total_compressed,
                "total_tokens_saved": total_saved,
                "average_compression_ratio_pct": round(avg_savings_pct, 1)
            },
            "top_5_compressions": [
                {
                    "target_file": t[0],
                    "original_tokens": t[1],
                    "tokens_saved": t[2],
                    "timestamp": t[3]
                } for t in top_saves
            ],
            "recent_activity": [
                {
                    "target_file": r[0],
                    "original_tokens": r[1],
                    "compressed_tokens": r[2],
                    "tokens_saved": r[3],
                    "timestamp": r[4]
                } for r in recent_logs
            ]
        }
        
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"Failed to read telemetry: {str(e)}"}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
