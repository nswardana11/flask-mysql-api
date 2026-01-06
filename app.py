from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}

API_KEY = os.getenv('API_KEY', 'your-secret-key')

@app.before_request
def check_api_key():
    if API_KEY:
        key = request.args.get('key')
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

@app.route('/')
def home():
    return jsonify({"status": "API ready"})

@app.route('/report-mutations')
def report_mutations():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
        SELECT 
            tm.transaction_id,
            tm.created_at AS paid_at,
            tu2.name AS Call_Center,
            tu.name AS PIC_Invoice,
            COALESCE(tt2.name,"Others") AS divisi,
            GROUP_CONCAT(tc.fullname SEPARATOR ',') AS nama_jamaah,
            COUNT(tc.fullname) AS total_person,
            tc.nik,
            tc.phone,
            tm.amount AS amount,
            tm.mutation_type AS type,
            CASE 
                WHEN tp.package_type IS NULL THEN 'null'
                WHEN tp.package_type LIKE "%haji%" THEN 'haji'
                WHEN tp.package_type LIKE "%umroh%" THEN 'umroh'
                ELSE tp.package_type
            END AS package_type,
            ti.payment_method AS payment_method,	
            ti.invoice_code
        FROM 
            tb_mutations tm
        LEFT JOIN tb_invoices ti ON ti.id = tm.invoice_id
        LEFT JOIN tb_transactions tt ON tt.id = tm.transaction_id
        JOIN tb_transaction_contacts ttc ON ttc.transaction_id = tt.id
        LEFT JOIN tb_users tu ON tu.id = tm.created_by
        LEFT JOIN tb_contacts tc ON tc.id = ttc.contact_id
        LEFT JOIN tb_users tu2 ON tu2.id = tc.created_by
        LEFT JOIN tb_product tp ON tt.product_id = tp.id
        LEFT JOIN tb_departure_contact tdc ON tdc.transaction_id = tt.id
        LEFT JOIN tb_team tt2 ON tt2.id = tu.team_id
        WHERE 
            tm.created_at >= "2025-08-01 00:00:00"
        GROUP BY tm.id
        ORDER BY tm.created_at ASC;
        """

        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return jsonify({"data": data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
