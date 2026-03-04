from flask import Flask, request, jsonify, abort, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

products = dict()
id = 1

@app.route('/product', methods=['POST'])
def add_product():
    global id
    data = request.get_json()
    if (not data) or ('name' not in data) or ('description' not in data):
        abort(400, 'missing arguments')
    
    new_product = {
        'id': id,
        'name': data['name'],
        'description': data['description'],
        'icon': None
    }

    products[id] = new_product
    id += 1

    return jsonify(new_product), 201

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id)
    if product is None:
        abort(404, 'Not found')

    return jsonify(product), 200

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    if data is None:
        abort(400, 'missing arguments')
    product = products.get(product_id)
    if product is None:
        abort(404, 'Not found')

    if 'name' in data:
        product['name'] = data['name']
    if 'description' in data:
        product['description'] = data['description']
    
    return jsonify(product), 200

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = products.get(product_id)
    if product is None:
        abort(404, 'Not found')
    
    del products[product_id]
    
    return jsonify(product), 200

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(list(products.values())), 200

@app.route('/product/<int:product_id>/image', methods=['POST'])
def upload_image(product_id):
    product = products.get(product_id)
    if product is None:
        abort(404, 'Not found')
    if 'icon' not in request.files:
        abort(400, 'missing arguments')
    file = request.files['icon']
    if file.filename == '':
        abort(400, 'missing arguments')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    product['icon'] = file_path

    return jsonify(product), 200

@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_image(product_id):
    product = products.get(product_id)
    if product is None or product['icon'] is None:
        abort(404, 'Not found')

    return send_file(product['icon']), 200

if __name__ == '__main__':
    app.run(debug=True)