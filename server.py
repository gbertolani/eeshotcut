import os
from flask import Flask, send_from_directory, render_template
from flask import redirect, request, abort
import odoorpc

from flask_cors import CORS

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

port = int(os.environ.get("PORT", 5000))


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/',  methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/api/', methods=['POST'])
def api():
    if not request.is_json:
        return abort(400)
    try:
        url = request.json['ODOO_URL']
        port = request.json['ODOO_PORT']
        db = request.json['ODOO_DB']
        username = request.json['ODOO_USER']
        password = request.json['ODOO_PASSWORD']
        model = request.json['ODOO_MODEL']
        args = request.json['ODOO_ARGS']
        kwargs = request.json['ODOO_KWARGS']
    except Exception:
        abort(400)

    protocol = 'jsonrpc'
    if str(port).strip() == '443':
        protocol = 'jsonrpc+ssl'

    try:
        odoo = odoorpc.ODOO(url, protocol=protocol, port=port)
        odoo.login(db, username, password)
    except Exception:
        abort(401)

    try:
        return odoo.execute(model, 'search_read', *args, **kwargs)
    except Exception:
        abort(404)


@app.route('/<path:path>')
def all_routes(path):
    return redirect('/')


if __name__ == "__main__":
    app.run(port=port)
