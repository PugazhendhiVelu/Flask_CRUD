from flask import Flask , jsonify , request
from app.database import get_mysql_connection

def user_controller(app):
    @app.route("/aerele/register",methods=['POST'])
    def register():
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        print(name,email,password)
        if not name or not email or not password :
            return jsonify({"Error ": "All fields are required "}),400
        try:
            connection  = get_mysql_connection(app)
            cursor = connection.cursor()
            cursor.execute("SELECT NAME FROM USERS WHERE EMAIL =%s",(email))
            existngUser = cursor.fetchone()
            if existngUser :
                return jsonify({"Message" : "User already existed with this email Id"}),400
            cursor.execute("INSERT INTO USERS(NAME , EMAIL ,PASSWORD ) VALUES (%s , %s ,%s)",(name ,email,password))
            connection.commit()
        except Exception as ex:
            return jsonify({"Error" : str(ex)}),500
        finally:
            cursor.close()
            connection.close()
        
        return jsonify({"Message":"User Created Successfully !"})

    @app.route("/aerele/login",methods=['POST'])
    def login():
        data= request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"Message":"Email and Password are required (:"}),400
        try:
            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM USERS WHERE EMAIL = %s AND PASSWORD = %s",(email,password))
            user = cursor.fetchone()
            if user:
                return jsonify({"Message":"Logged in Successfully!!"}),200
        except Exception as ex:
            return jsonify({"error":str(ex)}),500
        finally:
            cursor.close()
            connection.close()    
        return jsonify({"Message":"User not existed , Please Register "}),404


