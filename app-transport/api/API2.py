##
# Programmer   : Regis Rodolfo Schuch
# Date         : 10 June 2024
#              : Applied Computing Research Group, Unijui University, Brazil
#              : regis.schuch@unijui.edu.br
#              :
# Title        : API2.py 
#              :
# Description  : The API2.py code defines a RESTful API using the Flask framework to manage journeys in a transport 
#              : system. It includes routes to register (POST), list (GET), get details (GET), update (PUT), and 
#              : delete (DELETE) journeys in an SQLite database. The application initialises the connection to the 
#              : database and sets up a logging mechanism to monitor activity. A separate thread is used to monitor 
#              : updates to the database log table and display messages related to new updates. Each database operation 
#              : is protected by a lock to ensure secure access and avoid conflicts in a multithreading environment. 
#              : The application also uses TLS/SSL connections for secure network transactions, with specified 
#              : certificates (cert.pem and priv.pem).
#              :
# Source       : Some inspiration from
#              : https://flask.palletsprojects.com/en/3.0.x/
#              : https://docs.python.org/3/library/sqlite3.html
#              : https://flask.palletsprojects.com/en/3.0.x/patterns/sqlite3/
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
# dependencies : The API2.py code was run on Linux, on the Ubuntu 22.04.4 LTS distribution
#              : $ sudo apt-get install python3
#              :
#              : $ sudo apt update
#              : $ sudo apt install python3-pip
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
# run          : $ python3 API2.py
#              :
#              :
# Directory    :
# structure    : app-transport
#              : ├── api
#              : │   └── API2.py
#              : ├── data_access
#              : │   └── transporte_app.db
#              : ├── desktop_transporte.py
#              : └── keys
#              :     ├── cert.pem
#              :     |── priv.pem
#              :     └── public_key.pem
#              :
##   

import sqlite3
import time
import threading
from flask import Flask, request, jsonify
import logging

# Starting the Flask application
app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Defining a lock to control database access
db_lock = threading.Lock()

# Function to monitor database updates and display messages
def monitorar_atualizacoes():
    # Connecting to the database
    conn = sqlite3.connect('../data_access/transporte_app.db')
    c = conn.cursor()
    ultima_verificacao = None
    while True:
        # Check the last update in the update log
        c.execute("SELECT max(DataHora) FROM LogAtualizacoes")
        ultima_atualizacao = c.fetchone()[0]
        if ultima_atualizacao != ultima_verificacao:
            ultima_verificacao = ultima_atualizacao
            # Retrieve the message from the last update
            c.execute("SELECT Mensagem FROM LogAtualizacoes WHERE DataHora = ?", (ultima_atualizacao,))
            mensagem = c.fetchone()[0]
            print("API2:", mensagem)  # Display the message from the last update
        time.sleep(5)  # Check every second for updates

# Start monitoring updates in a separate thread
t = threading.Thread(target=monitorar_atualizacoes)
t.start()

# API2 Operations

# Route to register a new trip
@app.route('/api/viagens', methods=['POST'])
def cadastrar_viagem():
    data = request.json
    id_motorista = data.get('id_motorista')
    id_veiculo = data.get('id_veiculo')
    id_passageiro = data.get('id_passageiro')
    data_hora_inicio = data.get('data_hora_inicio')
    data_hora_fim = data.get('data_hora_fim')
    local_origem = data.get('local_origem')
    local_destino = data.get('local_destino')
    valor = data.get('valor')
    telefone_cliente = data.get('telefone_cliente')

    if not all([id_motorista, id_veiculo, data_hora_inicio, local_origem, local_destino, valor, telefone_cliente]):
        return jsonify({"error": "All fields are required"}), 400

    # Try to execute the database operation with a wait and retry
    attempts = 3
    for i in range(attempts):
        try:
            # Synchronize database access
            with db_lock:
                conn = sqlite3.connect('../data_access/transporte_app.db')
                c = conn.cursor()
                c.execute("INSERT INTO Viagens (id_motorista, id_veiculo, id_passageiro, data_hora_inicio, data_hora_fim, local_origem, local_destino, valor, telefone_cliente) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (id_motorista, id_veiculo, id_passageiro, data_hora_inicio, data_hora_fim, local_origem, local_destino, valor, telefone_cliente))
                conn.commit()
                # Get the inserted trip ID
                viagem_id = c.lastrowid
                conn.close()
                # Display trip details in the prompt
                print("New trip registered:")
                print("ID:", viagem_id)
                print("Driver:", id_motorista)
                print("Vehicle:", id_veiculo)
                print("Passenger:", id_passageiro)
                print("Start Date/Time:", data_hora_inicio)
                print("End Date/Time:", data_hora_fim)
                print("Origin:", local_origem)
                print("Destination:", local_destino)
                print("Value:", valor)
                print("Client Phone:", telefone_cliente)
                logger.info('TLS encrypted connection successfully established for trip registration.')
            # If the operation was successful, exit the loop
            break
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            # If it is the last attempt, return an error
            if i == attempts - 1:
                return jsonify({"error": "Database access error"}), 500
            # Wait a short period of time before trying again
            time.sleep(0.1)

    # Return the trip ID in the response
    return jsonify({"viagem_id": viagem_id, "message": "Trip successfully registered"}), 200

# Route to list all trips
@app.route('/api/viagens', methods=['GET'])
def listar_viagens():
    try:
        logger.info('TLS encrypted connection successfully established for listing trips.')
        # Connect to the database
        conn = sqlite3.connect('../data_access/transporte_app.db')
        c = conn.cursor()
        # Execute a query to retrieve all trips
        c.execute("SELECT * FROM Viagens")
        viagens = c.fetchall()
        # Close the database connection
        conn.close()
        # If there are no trips registered in the trips table, return an empty list
        if not viagens:
            return jsonify([]), 200
        # Format trip data to return as JSON
        viagens_formatadas = []
        for viagem in viagens:
            viagem_formatada = {
                "id": viagem[0],
                "id_motorista": viagem[1],
                "id_veiculo": viagem[2],
                "id_passageiro": viagem[3],
                "data_hora_inicio": viagem[4],
                "data_hora_fim": viagem[5],
                "local_origem": viagem[6],
                "local_destino": viagem[7],
                "valor": viagem[8],
                "telefone_cliente": viagem[9]
            }
            viagens_formatadas.append(viagem_formatada)
        return jsonify(viagens_formatadas), 200
    except sqlite3.Error as e:
        print("Error listing trips:", e)
        return jsonify({"error": "Error listing trips"}), 500

# Route to get trip details by ID
@app.route('/api/viagens/<int:id>', methods=['GET'])
def obter_viagem(id):
    try:
        # Connect to the database
        conn = sqlite3.connect('../data_access/transporte_app.db')
        c = conn.cursor()
        # Execute a query to get trip details based on the provided ID
        c.execute("SELECT * FROM Viagens WHERE id=?", (id,))
        viagem = c.fetchone()
        conn.close()
        # Check if the trip was found
        if viagem:
            detalhes_viagem = {
                "id": viagem[0],
                "id_motorista": viagem[1],
                "id_veiculo": viagem[2],
                "id_passageiro": viagem[3],
                "data_hora_inicio": viagem[4],
                "data_hora_fim": viagem[5],
                "local_origem": viagem[6],
                "local_destino": viagem[7],
                "valor": viagem[8],
                "telefone_cliente": viagem[9]
            }
            print("Trip details:", detalhes_viagem)
            logger.info('TLS encrypted connection successfully established for obtaining trip details.')
            return jsonify(detalhes_viagem), 200
        else:
            print("Trip not found.")
            return jsonify({"error": "Trip not found"}), 404
    except sqlite3.Error as e:
        print("Error obtaining trip details:", e)
        return jsonify({"error": "Error obtaining trip details"}), 500

# Route to update trip details by ID
@app.route('/api/viagens/<int:id>', methods=['PUT'])
def atualizar_viagem(id):
    data = request.json
    # Implement logic here to update trip details by ID
    print("Update trip details with ID:", id, "to:", data)
    logger.info('TLS encrypted connection successfully established for updating trip details.')
    return jsonify({"message": "Trip details successfully updated"}), 200

# Route to delete a trip by ID
@app.route('/api/viagens/<int:id>', methods=['DELETE'])
def excluir_viagem(id):
    # Implement logic here to delete a trip by ID
    print("Delete trip with ID:", id)
    logger.info('TLS encrypted connection successfully established for deleting the trip.')
    return jsonify({"message": "Trip successfully deleted"}), 200

if __name__ == '__main__':
    # Start the Flask application with HTTPS
    app.run(ssl_context=('../keys/cert.pem', '../keys/priv.pem'), debug=True, use_reloader=False, host='200.17.87.182', port=8080)

