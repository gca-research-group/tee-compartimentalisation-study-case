##
# Title        : API1.py 
#              :
# Source       : Some inspiration from
#              : https://flask.palletsprojects.com/en/3.0.x/
#              : https://docs.python.org/3/library/sqlite3.html
#              : https://flask.palletsprojects.com/en/3.0.x/patterns/sqlite3/
#              : https://github.com/GoogleCloudPlatform/flask-talisman
#              : https://docs.python.org/3/howto/logging.html
#              : https://docs.python.org/3/howto/logging-cookbook.html
#              : https://www.geeksforgeeks.org/multithreading-python-set-1/
#              : https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/
#              : https://medium.com/@bubu.tripathy/best-practices-for-designing-rest-apis-5b1809545e3c    
#              : https://towardsdatascience.com/creating-restful-apis-using-flask-and-python-655bad51b24
#              : https://auth0.com/blog/developing-restful-apis-with-python-and-flask/    
#              : https://flask-restful.readthedocs.io/en/latest/
#              : https://medium.com/@geekprogrammer11/understanding-ssl-with-flask-api-d0b137906cbd
#              : https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
#              :
#              :
# Install      :
# dependencies : The API1.py code was run on Linux, on the Ubuntu 22.04.4 LTS distribution
#              : $ sudo apt-get install python3
#              :
#              : $ sudo apt update
#              : $ sudo apt install python3-pip
#              : 
#              : $ pip install Flask Flask-Talisman
#              :
#              : $ sudo apt-get install libsqlite3-dev
#              :
#              : Creation of keys and certificates with:
#              : $ sudo apt install openssl
#              :
#              : Generate the private key:
#              : $ openssl genpkey -algorithm RSA -out priv.pem -pkeyopt rsa_keygen_bits:2048
#              : Extract the public key from the private key:
#              : $ openssl rsa -in priv.pem -pubout -out public_key.pem
#              : Generate the certificate:
#              : $ openssl req -new -x509 -key priv.pem -out cert.pem -days 365
#              :
# Compile and  :
# run          : $ python3 API1.py
#              :
#              :
# Directory    :
# structure    : app-store
#              : ├── api
#              : │   └── API1.py
#              : ├── data_access
#              : │   └── compras.db
#              : ├── desktop_compras.py
#              : └── keys
#              :     ├── cert.pem
#              :     |── priv.pem
#              :     └── public_key.pem
#              :
##   
    
import logging
from flask import Flask, request, jsonify
import sqlite3
import threading
import time
from flask_talisman import Talisman
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

app = Flask(__name__)
talisman = Talisman(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Defining a lock to control database access
db_lock = threading.Lock()

# Function to get a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('../data_access/compras.db')
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

# Function to ensure the necessary tables exist
def ensure_tables_exist():
    with db_lock:
        conn, c = get_db_connection()
        c.execute('''CREATE TABLE IF NOT EXISTS Vendas (
                        ID INTEGER PRIMARY KEY,
                        IDVendedor INTEGER,
                        IDCliente INTEGER,
                        Total REAL,
                        Data TEXT,
                        ID_LogAtualizacoes INTEGER
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS LogAtualizacoes (
                        ID INTEGER PRIMARY KEY,
                        Mensagem TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Vendedores (
                        ID INTEGER PRIMARY KEY,
                        Nome TEXT NOT NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Clientes (
                        ID INTEGER PRIMARY KEY,
                        Cliente TEXT NOT NULL,
                        Estado TEXT NOT NULL,
                        Sexo TEXT NOT NULL,
                        Status TEXT NOT NULL,
                        Telefone TEXT NOT NULL,
                        Endereco TEXT NOT NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Produtos (
                        ID INTEGER PRIMARY KEY,
                        Produto TEXT NOT NULL,
                        Preco REAL NOT NULL
                    )''')
        conn.commit()
        conn.close()

# Variable to store the ID of the last sale
ultima_id_venda = None

# Function to monitor updates in the sales database
def monitorar_atualizacoes():
    global ultima_id_venda
    while True:
        with db_lock:
            conn, c = get_db_connection()

            # Query to get the last sale
            c.execute("SELECT * FROM Vendas ORDER BY id DESC LIMIT 1")
            ultima_venda = c.fetchone()
            if ultima_venda:
                id_venda = ultima_venda['id']
                if id_venda != ultima_id_venda:
                    ultima_id_venda = id_venda
                    id_log_atualizacoes = ultima_venda['ID_LogAtualizacoes']
                    if id_log_atualizacoes:
                        # Query to get the message related to the last sale
                        c.execute("SELECT Mensagem FROM LogAtualizacoes WHERE ID = ?", (id_log_atualizacoes,))
                        mensagem_row = c.fetchone()
                        if mensagem_row:
                            mensagem = mensagem_row['Mensagem']
                            if mensagem.startswith('Venda efetuada'):
                                logger.info(f'New sale recorded - Message: {mensagem}')
                        else:
                            logger.warning("No message found for the last sale")
            else:
                logger.warning("No sales found")

            conn.close()
        time.sleep(5)

# Route to register a new vendor
@app.route('/api/vendedores', methods=['POST'])
def cadastrar_vendedor():
    data = request.json
    nome = data.get('nome')

    if nome:
        with db_lock:
            conn, c = get_db_connection()
            c.execute("INSERT INTO Vendedores (Nome) VALUES (?)", (nome,))
            conn.commit()
            conn.close()
            logger.info(f'New vendor registered: {nome}')
            return jsonify({"message": "Vendor successfully registered"}), 201
    else:
        return jsonify({"error": "Vendor name not provided"}), 400

# Route to register a new customer
@app.route('/api/clientes', methods=['POST'])
def cadastrar_cliente():
    data = request.json
    cliente = data.get('cliente')
    estado = data.get('estado')
    sexo = data.get('sexo')
    status = data.get('status')
    telefone = data.get('telefone')
    endereco = data.get('endereco')

    if cliente and estado and sexo and status and telefone and endereco:
        with db_lock:
            conn, c = get_db_connection()
            c.execute("INSERT INTO Clientes (Cliente, Estado, Sexo, Status, Telefone, Endereco) VALUES (?, ?, ?, ?, ?, ?)",
                      (cliente, estado, sexo, status, telefone, endereco))
            conn.commit()
            conn.close()
            logger.info(f'New customer registered: {cliente}')
            return jsonify({"message": "Customer successfully registered"}), 201
    else:
        return jsonify({"error": "Incomplete customer data"}), 400

# Route to register a new product
@app.route('/api/produtos', methods=['POST'])
def cadastrar_produto():
    data = request.json
    produto = data.get('produto')
    preco = data.get('preco')

    if produto and preco:
        with db_lock:
            conn, c = get_db_connection()
            c.execute("INSERT INTO Produtos (Produto, Preco) VALUES (?, ?)", (produto, preco))
            conn.commit()
            conn.close()
            logger.info(f'New product registered: {produto}')
            return jsonify({"message": "Product successfully registered"}), 201
    else:
        return jsonify({"error": "Incomplete product data"}), 400

# Route to consult sales
@app.route('/api/vendas', methods=['GET'])
def consultar_vendas():
    cert_pem = request.files.get('certificate')
    if not cert_pem:
        return jsonify({"error": "No certificate provided"}), 400

    cert = x509.load_pem_x509_certificate(cert_pem.read(), default_backend())
    
    # Check for specific strings in the certificate
    check_strings = ['CheriBSD 22.12', 'Research Morello SoC r0p0']
    found_any = {check_str: False for check_str in check_strings}
    
    for extension in cert.extensions:
        extension_data = extension.value
        if isinstance(extension_data, x509.UnrecognizedExtension):
            data = extension_data.value
            try:
                lines = data.decode().split('\n')
            except UnicodeDecodeError:
                # If decoding fails, treat data as binary
                lines = [data.hex()]
            
            for line in lines:
                for check_str in check_strings:
                    if check_str in line:
                        found_any[check_str] = True

    if not all(found_any.values()):
        return jsonify({"error": "Execution environment is not secure"}), 403

    with db_lock:
        conn, c = get_db_connection()
        c.execute("SELECT V.ID, V.IDVendedor, V.IDCliente, V.Total, V.Data, C.Telefone, C.Endereco \
                   FROM Vendas V \
                   JOIN Clientes C ON V.IDCliente = C.IDCliente")
        vendas = [dict(row) for row in c.fetchall()]
        conn.close()
    return jsonify({"vendas": vendas}), 200

# Route to register a new sale
@app.route('/api/vendas', methods=['POST'])
def cadastrar_venda():
    data = request.json
    id_vendedor = data.get('IDVendedor')
    id_cliente = data.get('IDCliente')
    total = data.get('Total')
    data_venda = data.get('Data')

    if id_vendedor and id_cliente and total and data_venda:
        with db_lock:
            conn, c = get_db_connection()
            c.execute("INSERT INTO Vendas (IDVendedor, IDCliente, Total, Data) VALUES (?, ?, ?, ?)",
                      (id_vendedor, id_cliente, total, data_venda))
            conn.commit()
            conn.close()
            logger.info(f'New sale recorded: IDVendedor={id_vendedor}, IDCliente={id_cliente}, Total={total}, Data={data_venda}')
            logger.info('TLS encrypted connection successfully established for sale registration.')
            return jsonify({"message": "Sale successfully registered"}), 201
    else:
        return jsonify({"error": "Incomplete sale data"}), 400

if __name__ == '__main__':
    ensure_tables_exist()

    # Initialize the thread to monitor updates in the sales database
    t = threading.Thread(target=monitorar_atualizacoes)
    t.start()

    # Disable reloader to avoid multiple prompts for PEM pass phrase
    app.run(ssl_context=('../keys/cert.pem', '../keys/priv.pem'), debug=True, use_reloader=False, host='200.17.87.181', port=8080)

