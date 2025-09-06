#!/usr/bin/env python3
"""
Utility to clear application logs and start fresh.
"""

import os
from pathlib import Path

def clear_logs():
    """Clear all application logs."""
    log_dir = Path("logs")
    
    if not log_dir.exists():
        print("No logs directory found.")
        return
    
    log_files = list(log_dir.glob("*.log*"))
    
    if not log_files:
        print("No log files found.")
        return
    
    print(f"Found {len(log_files)} log files:")
    for log_file in log_files:
        print(f"  - {log_file}")
    
    confirm = input("Clear all log files? (y/N): ").lower().strip()
    
    if confirm == 'y':
        for log_file in log_files:
            try:
                log_file.unlink()
                print(f"✅ Cleared {log_file}")
            except Exception as e:
                print(f"❌ Failed to clear {log_file}: {e}")
        print("Log clearing complete!")
    else:
        print("Log clearing cancelled.")

if __name__ == "__main__":
    clear_logs()