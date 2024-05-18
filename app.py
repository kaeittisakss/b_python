from flask import Flask, render_template, request, jsonify, send_file ,make_response
import mysql.connector
from docxtpl import DocxTemplate
from datetime import date
from flask_cors import CORS
from dotenv import load_dotenv
import os
from io import BytesIO
import tempfile

# โหลดค่าจากไฟล์ .env
load_dotenv()
# อ่านค่าพอร์ต
port = os.getenv("PORT")

app = Flask(__name__)
# CORS(app, origins="http://localhost:3000") # port ของฝั่งfront
# allow all origins ใช้ได้ทุกโดเมน
CORS(app, origins="*")


@app.route('/')
def index():
    return {'message': 'deploy by joe'}


@app.route('/employee_list', methods=['GET'])
def get_employee_list():
    connection = mysql.connector.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        password=os.getenv("mysql_password"),
        database=os.getenv("mysql_database")
    )
    cursor = connection.cursor()
    query = "SELECT employee_ID, fullNameEng FROM employee"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    employee_list = [{'employee_ID': row[0], 'fullNameEng': row[1]} for row in data]
    return jsonify(employee_list)


@app.route('/generate_contract', methods=['POST'])
def generate_contract():
    selected_employee = int(request.json['selected_employee'])
    print("selected_employee: ", selected_employee)
    connection = mysql.connector.connect(
        host=os.getenv("mysql_host"),
        user=os.getenv("mysql_user"),
        password=os.getenv("mysql_password"),
        database=os.getenv("mysql_database")
    )
    cursor = connection.cursor()
    query = "SELECT fullNameEng, currentAddress, personal_id, Positon, Contract_Consultant_Name, Contract_Duration, client, Work_address, Salary, Agreement_expiration_period, Leave_eligibility FROM employee WHERE employee_ID = %s"
    cursor.execute(query, (selected_employee,))
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    print("data: ", data)
    if data:
        doc = DocxTemplate("template.docx")
        context = {
            'fullNameEng': data[0],
            'currentAddress': data[1],
            'personal_id': data[2],
            'Positon': data[3],
            'Contract_Consultant_Name': data[4],
            'Contract_Duration': data[5],
            'client': data[6],
            'Work_address': data[7],
            'Salary': data[8],
            'Agreement_expiration_period': data[9],
            'Leave_eligibility': data[10]
        }
        doc.render(context)
        today = date.today().strftime("%Y-%m-%d")
        selected_name = data[0].replace(" ", "_")
        output_file = f"contract_{today}_{selected_name}.docx"
        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, output_file)
        doc.save(output_file)
        download_link = f"{os.getenv('back_url')}/download?output_file={output_file}"
        
        # download_link = f"{os.getenv('back_url')}/download?output_file={output_file}"

        return jsonify(download_link)
    else:
        return jsonify("ไม่พบข้อมูลพนักงานในฐานข้อมูล")

@app.route('/download')
def download_file():
    # Replace 'path/to/file.pdf' with the actual file path
    output_file = request.args.get('output_file')
    return send_file(output_file, as_attachment=True)



if __name__ == "__main__":
    app.run(debug = False, host='0.0.0.0', port=port)
