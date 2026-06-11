import os
import shutil
import sys

def check_env():
    print("[SETUP] Checking environment configurations...")
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("[SETUP] .env file not found. Copying from .env.example...")
            shutil.copy(".env.example", ".env")
            print("[SETUP] Created .env template. Please review and update database credentials in .env!")
        else:
            print("[SETUP] WARNING: Neither .env nor .env.example exist in the workspace root.")
    else:
        print("[SETUP] Environment .env file verified.")

def check_dependencies():
    print("[SETUP] Verifying Python package installations...")
    try:
        import flask
        import dotenv
        import mysql.connector
        print("[SETUP] Packages verified (Flask, dotenv, mysql.connector).")
    except ImportError as e:
        print(f"[SETUP] Missing packages: {e}")
        print("[SETUP] Please run: pip install -r requirements.txt")

def main():
    print("=============================================")
    print("ChemLove Environment Setup & Bootstrap Tool")
    print("=============================================")
    check_env()
    check_dependencies()
    print("[SETUP] Setup diagnostics completed. Run 'python app.py' to launch.")

if __name__ == "__main__":
    main()
