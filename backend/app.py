import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "loantrack"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "")
    )

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/loans", methods=["GET"])
def get_loans():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, borrower_name, loan_amount, property_city, status, created_at FROM loans ORDER BY id DESC;")
    loans = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(loans), 200

@app.route("/api/loans", methods=["POST"])
def create_loan():
    data = request.get_json()
    borrower_name = data.get("borrower_name")
    loan_amount = data.get("loan_amount")
    property_city = data.get("property_city", "")
    status = data.get("status", "PENDING")

    if not borrower_name or loan_amount is None:
        return jsonify({"error": "borrower_name and loan_amount are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO loans (borrower_name, loan_amount, property_city, status) VALUES (%s, %s, %s, %s) RETURNING id, borrower_name, loan_amount, property_city, status, created_at;",
        (borrower_name, loan_amount, property_city, status)
    )
    new_loan = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_loan), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
