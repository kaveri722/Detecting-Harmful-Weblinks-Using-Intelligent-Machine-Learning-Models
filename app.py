import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

safe_protocols = ["HTTP", "https", "ftp", "sftp"]

DB_NAME = "results.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            protocol TEXT,
            prediction TEXT,
            risk_level TEXT,
            risk_percentage INTEGER,
            suggestion1 TEXT,
            suggestion2 TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/detect')
def detect():
    return render_template("detect.html")


@app.route('/predict', methods=['POST'])
def predict():
    try:


        
        url = request.form['url']
        protocol = request.form['protocol'].lower()

        risk_level = "None"
        risk_percentage = 0
        suggestion1 = ""
        suggestion2 = ""

        if protocol in safe_protocols:
            prediction = "Good link"
            risk_percentage = 5
            risk_level = "Safe"

        else:
            prediction = "Harmful link"

            if protocol.startswith("file"):
                risk_level = "High"
                risk_percentage = 90
                suggestion1 = "Avoid opening the link immediately."
                suggestion2 = "Run a full antivirus scan."

            elif protocol.startswith("javascript"):
                risk_level = "Medium"
                risk_percentage = 60
                suggestion1 = "Do not allow scripts to run."
                suggestion2 = "Check link with an online scanner."

            else:
                risk_level = "Low"
                risk_percentage = 30
                suggestion1 = "Verify the source of the link."
                suggestion2 = "Open only in secure browser."

        # Proper formatted timestamp
        current_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO results
            (url, protocol, prediction, risk_level,
             risk_percentage, suggestion1, suggestion2, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            url,
            protocol,
            prediction,
            risk_level,
            risk_percentage,
            suggestion1,
            suggestion2,
            current_time
        ))

        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            url=url,
            protocol=protocol,
            prediction=prediction,
            risk_level=risk_level,
            risk_percentage=risk_percentage,
            suggestion1=suggestion1,
            suggestion2=suggestion2
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/visualization')
def visualization():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT risk_level, risk_percentage
        FROM results
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    levels = [r[0] for r in rows]
    percentages = [r[1] for r in rows]

    return render_template(
        "visualization.html",
        levels=levels,
        percentages=percentages
    )


@app.route('/previous-results')
def previous_results():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, url, protocol, prediction,
               risk_level, risk_percentage,
               suggestion1, suggestion2, timestamp
        FROM results
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return render_template(
        "view_previous_result.html",
        results=rows
    )


if __name__ == "__main__":
    app.run(debug=True)
