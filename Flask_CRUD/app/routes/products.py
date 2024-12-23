from flask import Flask , jsonify , request
from app.database import get_mysql_connection

def product_controller(app):
        
    @app.route("/aerele/products",methods=['GET'])
    def products():
        page = request.args.get('page',1,type=int)
        size = request.args.get('size',10,type=int)

        offset = (page -1)*size

        connection = get_mysql_connection(app)
        cursor = connection.cursor()
        try:
            sql = "SELECT * FROM PRODUCTS LIMIT %s OFFSET %s"
            cursor.execute(sql,(size,offset))
            result = cursor.fetchall()
            if not result:
                return jsonify({
                    "message":"No product available at the moment!!"
                }),404
            response = {
                "products":result,
                "pagination":{
                    "current_page":page,
                    "page_size":size
                }
            }
        except Exception as ex:
            return jsonify({"error" : str(ex)}),500
        finally:
            cursor.close()
            connection.close()
        return jsonify(response)
    
    @app.route("/aerele/add/product",methods=['POST'])
    def addProduct():
        data = request.get_json()
        name = data.get('name')
        category = data.get('category')
        qty = data.get('qty')
        price = data.get('price')
        desc = data.get('description')
        if not name or not category or not qty or not price or not desc :
            return jsonify({
                "message":"All fields are required"
            }),400
        try:
            qty = int(qty)
            price = float(price)
            if qty<=0 or price<=0:
                return jsonify({
                    "message":"Quantity and Price should be a positive value"
                }),400
        except ValueError:
            return jsonify({
                "message":"Invalid format - Quantity and Price should not be null or negative value "
            }),500
        try:
            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            sql = """INSERT INTO PRODUCTS (NAME , CATEGORY , QTY , PRICE ,DESCRIPTION) 
            VALUES(%s,%s,%s,%s,%s)"""
            cursor.execute(sql,(name,category,qty,price,desc))
            connection.commit()
        except Exception as ex:
            return jsonify({
                "error":str(ex)
            }),500
        finally:
            cursor.close()
            connection.close()
        return jsonify({
            "message":"Produt added successfully!!"
        }),201 

    @app.route("/aerele/get/product/",methods=['GET'])
    def getByProductId():
        try:
            productId = int(request.args.get('id',0))
        except ValueError:
            return jsonify({
                "message": "Product ID must be a valid positive integer."
            }), 400
        if not productId or productId<1:
            return jsonify({
                "message":"Product ID should not be null or negative "
            }),400
        try:
            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM PRODUCTS WHERE ID = %s",(productId))
            product = cursor.fetchone()
            if not product:
                return jsonify({
                    "message":(f"No Product found with the ID :{productId}")
                }),404
        except Exception as ex:
            return jsonify({
                "error":str(ex)
            }),500
        finally:
            cursor.close()
            connection.close()
        return jsonify({
                "message":"Fetched Successful",
                "product":product
        }),200
    
    @app.route("/aerele/edit/product", methods=['PUT'])
    def editProduct():
        data = request.get_json()
        product_id = data.get('id')
        name = data.get('name')
        category = data.get('category')
        qty = data.get('qty')
        price = data.get('price')
        desc = data.get('description')

        if not product_id:
            return jsonify({
                "message": "Product ID is required"
            }), 400

        updates = []
        values = []

        if name:
            updates.append("NAME = %s")
            values.append(name)
        if category:
            updates.append("CATEGORY = %s")
            values.append(category)
        if qty:
            try:
                qty = int(qty)
                if qty <= 0:
                    return jsonify({"message": "Quantity must be a positive integer"}), 400
                updates.append("QTY = %s")
                values.append(qty)
            except ValueError:
                return jsonify({"message": "Invalid quantity format"}), 400
        if price:
            try:
                price = float(price)
                if price <= 0:
                    return jsonify({"message": "Price must be a positive number"}), 400
                updates.append("PRICE = %s")
                values.append(price)
            except ValueError:
                return jsonify({"message": "Invalid price format"}), 400
        if desc:
            updates.append("DESCRIPTION = %s")
            values.append(desc)

        if not updates:
            return jsonify({"message": "At least one field must be provided to update"}), 400

        values.append(product_id)

        try:
            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            sql = f"UPDATE PRODUCTS SET {', '.join(updates)} WHERE ID = %s"
            cursor.execute(sql, values)
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({
                    "message": f"No product found with ID: {product_id}"
                }), 404
        except Exception as ex:
            return jsonify({
                "error": str(ex)
            }), 500
        finally:
            cursor.close()
            connection.close()

        return jsonify({
            "message": "Product updated successfully!"
        }), 200

