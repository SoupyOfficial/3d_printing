#!/usr/bin/env python3
# dual_logger.py -- Utility for logging to both console and files

import sys
import time
from pathlib import Path

class DualLogger:
    """Logger that writes to both console and file"""
    
    def __init__(self, log_file_path=None):
        self.log_file = log_file_path
        
    def log(self, message, prefix="INFO"):
        """Log message to both console and file"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {prefix}: {message}"
        
        # Console output
        try:
            print(log_line)
            sys.stdout.flush()
        except Exception:
            pass
        
        # File output
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_line + "\n")
            except Exception:
                pass
                
    def info(self, message):
        """Log info message"""
        self.log(message, "INFO")
        
    def error(self, message):
        """Log error message"""
        self.log(message, "ERROR")
        
    def debug(self, message):
        """Log debug message"""
        self.log(message, "DEBUG")

def get_logger(script_name):
    """Get a dual logger for a script"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f"{script_name}.log"
    return DualLogger(log_file)

if __name__ == "__main__":
    # Test the dual logger
    logger = get_logger("test")
    logger.info("Testing dual logging functionality")
    logger.error("This is a test error message")
    logger.debug("This is a test debug message")
    print("Dual logger test complete!")