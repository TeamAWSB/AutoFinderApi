from flask import Flask, jsonify, request
from flask_cors import CORS
from helper import Helper
import json
import fdb

app = Flask(__name__)
CORS(app)

def connect_to_firebirdsql():
    return fdb.connect(dsn='H:/Projects/Python/AutoFinderApi/AUTOFINDER.fdb', user='sysdba', password='admin')

@app.route("/")
def home():
    return "hello, this is api auto finder!"

@app.route('/vehicles', methods=['POST'])
def GetVehicles():
    if not request.is_json:
        return jsonify({'error': "No data json" }), 400

    try:
        data = request.get_json()
        marks = data['marks']
        fuelTypes = data['fuelTypes']

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        query = """select veh.ID_VEHICLES, mrk."NAME", mdl."NAME", gen."NAME", tpe."NAME", gen.YEAR_BEGIN, gen.YEAR_END, cls."NAME", flt."NAME", egn."NAME", egn.ENGINECAPASITY, egn.HORSEPOWER, tmn."NAME", veh.URLIMAGE, veh.DESCRIPTION from VEHICLES veh
inner join MARK mrk on mrk.ID_MARK = veh.ID_MARK
inner join MODEL mdl on mdl.ID_MODEL = veh.ID_MODEL
inner join GENERATIONS gen on gen.ID_GENERATIONS = veh.ID_GENERATION
inner join CLASS cls on cls.ID_CLASS = veh.ID_CLASS
inner join FUEL_TYPE flt on flt.ID_FUEL_TYPE = veh.ID_FUEL_TYPE
inner join ENGINES egn on egn.ID_ENGINES = veh.ID_ENGINES
inner join "TYPE" tpe on tpe.ID_TYPE = veh.ID_TYPE
inner join TRANSMISSION tmn on tmn.ID_TRANSMISSION = veh.ID_TRANSMISSIONS"""

        if len(marks) > 0 or len(fuelTypes) > 0:
            query += ' where '

            if len(marks) > 0:
                query += '('
                for id, mark in enumerate(marks):
                    query += f"""mrk.ID_MARK = {mark}"""

                    if id != (len(marks) - 1):
                        query += ' or '
                query += ')'

            if len(fuelTypes) > 0:
                query += '('
                for id, fuel in enumerate(fuelTypes):
                    query += f"""flt.ID_FUEL_TYPE = {fuel}"""

                    if id != (len(fuelTypes) - 1):
                        query += ' or '
                query += ')'

        cursor.execute(f"""{query} order by ID_VEHICLES desc""")
        rows = cursor.fetchall()

        data = []
        for row in rows:
            description = str(row[14],'windows-1250')
            new = {
                'id': str(row[0]),
                'mark': str(row[1]),
                'model': str(row[2]),
                'class': str(row[7]),
                'type': str(4),
                'description': description,
                'generations':[
                    {
                        'generation': str(row[3]),
                        'yearBegin': str(row[5]),
                        'yearEnd': str(row[6]),
                        'fuelType': str(row[8]),
                        'engineGeneration': str(row[9]),
                        'engineCapacity': str(row[10]),
                        'horsepower': str(row[11]),
                        'transmissionType': str(row[12]),
                        'urlImage': str(row[13])[2:-1],
                    }
                ]
            }

            vehicle = Helper.FindVehicleInList(data, new)
            if vehicle is not None:
                vehicle['generations'].append(new['generations'][0])
            else:
                data.append(new)

        json_data = json.dumps(data, ensure_ascii=False)
        return json_data
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()
    
@app.route('/fuelTypes', methods=['GET'])
def GetFuelTypes():
    try:
        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM FUEL_TYPE")
        rows = cursor.fetchall()

        data = []
        for row in rows:
            new = {
                'id': str(row[0]),
                'name': str(row[1])
            }
            data.append(new)

        json_data = json.dumps(data, ensure_ascii=False)
        return json_data
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()

@app.route('/marks', methods=['GET'])
def GetMarks():
    try:
        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM MARK")
        rows = cursor.fetchall()

        data = []
        for row in rows:
            new = {
                'id': str(row[0]),
                'name': str(row[1])
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