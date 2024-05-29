from flask import Flask, jsonify, request
from flask_cors import CORS
from helper import Helper
import json
import os
import fdb

app = Flask(__name__)
CORS(app)

def load_config():
    config_filename = 'appconfig.json'
    if not os.path.exists(config_filename):
        config_filename = 'appconfig.example.json'
    
    with open(config_filename, 'r') as file:
        config = json.load(file)
    
    return config

def connect_to_firebirdsql():
    config = load_config()
    return fdb.connect(dsn=config.get('Data Source'), user=config.get('User'), password=config.get('Password'))

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
                query += 'and ('
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
                        'vehicleId': str(row[0]),
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
    
@app.route('/favoriteVehicles', methods=['POST'])
def GetFavoriteVehicles():
    if not request.is_json:
        return jsonify({'error': "No data json" }), 400

    try:
        data = request.get_json()
        userId = data['userId']

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        query = f"""select veh.ID_VEHICLES, mrk."NAME", mdl."NAME", gen."NAME", tpe."NAME", gen.YEAR_BEGIN, gen.YEAR_END, cls."NAME", flt."NAME", egn."NAME", egn.ENGINECAPASITY, egn.HORSEPOWER, tmn."NAME", veh.URLIMAGE, veh.DESCRIPTION from VEHICLES veh
inner join MARK mrk on mrk.ID_MARK = veh.ID_MARK
inner join MODEL mdl on mdl.ID_MODEL = veh.ID_MODEL
inner join GENERATIONS gen on gen.ID_GENERATIONS = veh.ID_GENERATION
inner join CLASS cls on cls.ID_CLASS = veh.ID_CLASS
inner join FUEL_TYPE flt on flt.ID_FUEL_TYPE = veh.ID_FUEL_TYPE
inner join ENGINES egn on egn.ID_ENGINES = veh.ID_ENGINES
inner join "TYPE" tpe on tpe.ID_TYPE = veh.ID_TYPE
inner join TRANSMISSION tmn on tmn.ID_TRANSMISSION = veh.ID_TRANSMISSIONS
inner join FAVORITEVEHICLES fvl on fvl.VEHICLEID = veh.ID_VEHICLES
inner join USERS usr on usr.ID = fvl.USERID
where usr.ID={userId} and fvl.LIKED = true"""

        cursor.execute(query)
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
                        'vehicleId': str(row[0]),
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

            data.append(new)

        json_data = json.dumps(data, ensure_ascii=False)
        return json_data
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()

@app.route('/setLikeVehicle', methods=['POST'])
def SetLikeVehicle():
    if not request.is_json:
        return jsonify({'error': "No data json" }), 400

    try:
        data = request.get_json()
        vehicleId = data.get('vehicleId')
        userId = data.get('userId')
        status = data.get('status')

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute(f"""SELECT r.ID, r.USERID, r.VEHICLEID, r.LIKED
        FROM FAVORITEVEHICLES r
        WHERE r.VEHICLEID = {vehicleId} AND r.USERID = {userId}""")
        rows = cursor.fetchall()

        if len(rows) == 0:
            cursor.execute(f"""INSERT INTO FAVORITEVEHICLES (USERID, VEHICLEID, LIKED)
            VALUES ({userId}, {vehicleId}, true);""")
            connection.commit()
            return jsonify({'result': 'success'}), 200
        elif len(rows) == 1:
            cursor.execute(f"""UPDATE FAVORITEVEHICLES a SET 
                a.LIKED = {status}
            WHERE
                a.ID = {rows[0][0]}""")
            connection.commit()
            return jsonify({'result': 'success'}), 200
        else:
            return jsonify({'error': 'Unexpected error in the database'}), 404
    except Exception as e:
        print(str(e))
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

        cursor.execute(f"""SELECT * FROM USERS r
        WHERE r.EMAIL='{email}' AND r."PASSWORD"='{password}'""")
        rows = cursor.fetchall()

        if len(rows) == 1:
            return jsonify({
                'id': rows[0][0],
                'name': rows[0][1],
                'email': rows[0][3]
                }), 200
        else:
            return jsonify({'error': 'Email or password is incorrent!'}), 404
    except Exception as e:
        print(str(e))
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
        birthOfYear = data.get('birthOfYear')
        country = data.get('country')
        password = data.get('password')

        connection = connect_to_firebirdsql()
        cursor = connection.cursor()

        cursor.execute(f"select * from Users where EMAIL='{email}'")
        rows = cursor.fetchall()

        if len(rows) > 0:
            return jsonify({'error': 'The user already exists with this email address!'}), 200

        cursor.execute(f"""INSERT INTO Users ("NAME", SURNAME, EMAIL, BIRTH_OF_YEAR, COUNTRY, "PASSWORD") VALUES ('{name}', '{surname}', '{email}', {birthOfYear}, '{country}', '{password}')""")
        connection.commit()

        return jsonify({'status': True}), 200
    except Exception as e:
        return jsonify({'error': str(e) }), 200
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)