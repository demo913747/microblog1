import os
import subprocess
import sqlite3
from typing import Dict, List, Any, Tuple, Union

from flask import Blueprint, jsonify, request, Response

bp = Blueprint("search_api", __name__, url_prefix="/api")

# Using environment variables for secrets
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")

 

 

def raw_connection() -> sqlite3.Connection:

    return sqlite3.connect("app.db")

 

 

@bp.route("/user/<user_id>")

def get_user(user_id: str) -> Union[Response, Tuple[Response, int]]:

    conn = raw_connection()
    try:
        cursor = conn.cursor()

        query = "SELECT id, username, email FROM user WHERE id = ?"

        cursor.execute(query, (user_id,))

        rows = cursor.fetchall()

        if not rows:
            return jsonify({"error": "User not found"}), 404

        user = rows[0]

        return jsonify({"id": user[0], "username": user[1], "email": user[2]})
    finally:
        conn.close()

 

 

@bp.route("/search")

def search() -> Response:

    term = request.args.get("q", "")

    conn = raw_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE username LIKE ?", (f"%{term}%",))

        results = cursor.fetchall()

        return jsonify(results)
    finally:
        conn.close()

 

 

@bp.route("/ping")

def ping() -> Response:

    host = request.args.get("host", "127.0.0.1")

    try:
        result = subprocess.run(["ping", "-n", "1", host], 
                                capture_output=True, text=True, check=False)
        exit_code = result.returncode
    except subprocess.SubprocessError:
        exit_code = -1

    return jsonify({"host": host, "exit_code": exit_code})
