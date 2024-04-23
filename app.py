from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import fdb

app = Flask(__name__)
CORS(app)

def connect_to_firebirdsql():
    return fdb.connect(dsn='H:/Projects/Python/AutoFinderApi/AUTOFINDER.fdb', user='sysdba', password='admin')

@app.route("/")
def home():
    return "hello, this is api auto finder!"

@app.route('/vehicles', methods=['GET'])
def GetVehicles():
    try:
        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute("SELECT FIRST 20 * FROM VEHICLES ORDER BY ID DESC")
        rows = cursor.fetchall()

        data = []
        for row in rows:
            description = str(row[7],'windows-1250')
            new = {
                'id': str(row[0]),
                'mark': str(row[1]),
                'model': str(row[2]),
                'engineCapacity': str(row[3]),
                'year': str(row[4]),
                'class': str(row[5]),
                'urlImage': str(row[6])[2:-1],
                'description': description,
                'generation': str(row[8]),
                'horsepower': str(row[9])
            }
            data.append(new)

        json_data = json.dumps(data, ensure_ascii=False)
        return json_data
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()
    
@app.route('/login', methods=['POST'])
def Login():
    if not request.is_json:
        return jsonify({'error': "No data json" }), 400

    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM USERS where EMAIL='{email}' and PASSWORD='{password}'")
        rows = cursor.fetchall()

        if len(rows) == 0:
            return jsonify({'error': 'User not found'}), 404
        else:
            return jsonify({'user': rows[0][1]}), 200
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()
    
@app.route('/user', methods=['POST'])
def GetUser():
    if not request.is_json:
        return jsonify({'error': "No data json" }), 400

    try:
        data = request.get_json()
        email = data.get('email')

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM users where EMAIL='{email}'")
        rows = cursor.fetchall()

        if len(rows) == 0:
            return jsonify({'error': 'User not found'}), 404

        row = rows[0]
        user = {
            'id': str(row[0]),
            'name': str(row[1]),
            'surname': str(row[2]),
            'email': str(row[3]),
            'age': str(row[4]),
            'country': str(row[5])
        }

        cursor.close()
        connection.close()

        json_data = json.dumps(user)
        return json_data
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    
@app.route('/register', methods=['POST'])
def Register():
    if not request.is_json:
        return jsonify({'error': "No data json" }), 400

    try:
        data = request.get_json()
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')
        age = data.get('age')
        country = data.get('country')
        password = data.get('password')

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute(f"select * from Users where EMAIL='{email}'")
        rows = cursor.fetchall()

        if len(rows) > 0:
            return jsonify({'error': 'The user already exists with this email address!'}), 200

        cursor.execute(f"""INSERT INTO Users ("NAME", SURNAME, EMAIL, AGE, COUNTRY, "PASSWORD") VALUES ('{name}', '{surname}', '{email}', {age}, '{country}', '{password}')""")
        connection.commit()

        return jsonify({'status': 'Succes'}), 200
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)