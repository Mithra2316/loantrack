import logging
import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

POD_NAME = os.environ.get("HOSTNAME", "local-backend")
db_pool = None


def init_db_pool():
    global db_pool
    max_retries = 10
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            db_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.environ.get("DB_HOST", "db"),
                port=os.environ.get("DB_PORT", "5432"),
                dbname=os.environ.get("DB_NAME", "loantrack"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", ""),
            )
            logger.info("Database connection pool initialized on attempt %d.", attempt)
            return
        except OperationalError as exc:
            logger.warning(
                "Database not ready (attempt %d/%d): %s. Retrying in %ds...",
                attempt, max_retries, exc, delay,
            )
            time.sleep(delay)
            delay = min(delay * 2, 16)
    logger.error("Could not connect to database after %d attempts.", max_retries)


@app.after_request
def add_pod_header(response):
    response.headers["X-Pod-Name"] = POD_NAME
    return response


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "alive", "pod": POD_NAME}), 200


@app.route("/readyz", methods=["GET"])
def readyz():
    if db_pool is None:
        return jsonify({"status": "not ready", "reason": "pool not initialized"}), 503
    conn = None
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        return jsonify({"status": "ready", "pod": POD_NAME}), 200
    except Exception as exc:
        logger.error("Readiness check failed: %s", exc)
        return jsonify({"status": "not ready", "error": str(exc)}), 503
    finally:
        if conn:
            db_pool.putconn(conn)


@app.route("/api/loans", methods=["GET"])
def get_loans():
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, borrower_name, loan_amount, property_city, status, created_at "
                "FROM loans ORDER BY id DESC;"
            )
            loans = cur.fetchall()
        return jsonify(loans), 200
    finally:
        db_pool.putconn(conn)


@app.route("/api/loans", methods=["POST"])
def create_loan():
    data = request.get_json()
    borrower_name = data.get("borrower_name")
    loan_amount = data.get("loan_amount")
    property_city = data.get("property_city", "")
    status = data.get("status", "PENDING")

    if not borrower_name or loan_amount is None:
        return jsonify({"error": "borrower_name and loan_amount are required"}), 400

    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO loans (borrower_name, loan_amount, property_city, status) "
                "VALUES (%s, %s, %s, %s) "
                "RETURNING id, borrower_name, loan_amount, property_city, status, created_at;",
                (borrower_name, loan_amount, property_city, status),
            )
            new_loan = cur.fetchone()
        conn.commit()
        return jsonify(new_loan), 201
    finally:
        db_pool.putconn(conn)


init_db_pool()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)