#!/usr/bin/env python3
"""
Desktop GUI Application Launcher for Blockchain Voting System
Run this file to start the Tkinter-based desktop application
"""

import sys
import os

# Fix Windows encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blockchain_voting.gui.tkinter_app import main

if __name__ == "__main__":
    print("Starting Blockchain Voting System - Desktop GUI")
    print("=" * 50)
    print("Features:")
    print("• Voter Registration")
    print("• Vote Casting")
    print("• Block Mining")
    print("• Results Display")
    print("• Blockchain Validation")
    print("• System Administration")
    print("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)