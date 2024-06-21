##
# Programmer   : Regis Rodolfo Schuch
# Date         : 10 June 2024
#              : Applied Computing Research Group, Unijui University, Brazil
#              : regis.schuch@unijui.edu.br
#              :
# Title        : server_laucher.py 
#              :
# Description  : server_laucher.py defines a web application using the Flask framework that allows C files to be 
#              : uploaded, listed, deleted, compiled and executed via a REST API. The application stores the uploaded 
#              : files in the file system and keeps metadata records in the SQLite files.db database. It includes 
#              : checks to ensure that only files with a .c extension are accepted and that the file size does not 
#              : exceed 16MB. When a file is uploaded, its information is entered into the database. The application 
#              : can compile C files and store the resulting executable in the database. Executable files can be run 
#              : directly from the database, and the results are returned via the API. The application uses HTTPS for 
#              : secure communication and includes detailed logging to track the compilation and execution process.
#              :
# Source       : Some inspiration from
#              : https://flask.palletsprojects.com/en/3.0.x/
#              : https://docs.python.org/3/library/sqlite3.html
#              : https://flask.palletsprojects.com/en/3.0.x/patterns/sqlite3/
#              : https://docs.python.org/3/howto/logging.html
#              : https://docs.python.org/3/howto/logging-cookbook.html
#              : https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/
#              : https://medium.com/@bubu.tripathy/best-practices-for-designing-rest-apis-5b1809545e3c    
#              : https://towardsdatascience.com/creating-restful-apis-using-flask-and-python-655bad51b24
#              : https://auth0.com/blog/developing-restful-apis-with-python-and-flask/    
#              : https://flask-restful.readthedocs.io/en/latest/
#              : https://medium.com/@geekprogrammer11/understanding-ssl-with-flask-api-d0b137906cbd
#              : https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
#              : https://docs.python.org/3/library/subprocess.html
#              :
#              :
# Install      :
# dependencies : The client_launcher.py code was executed on the Unix-enabled CheriBSD Operating System, which extends 
#              : FreeBSD
#              : $ sudo pkg64 install python3
#              :
#              : $ sudo pkg64 install py39-pip
#              : 
#              : $ pip install Flask
#              :
#              : $ sudo pkg64 install sqlite3
#              :
#              : Generate the private key:
#              : $ openssl genpkey -algorithm RSA -out priv.pem -pkeyopt rsa_keygen_bits:2048
#              : Extract the public key from the private key:
#              : $ openssl rsa -in priv.pem -pubout -out public_key.pem
#              : Generate the certificate:
#              : $ openssl req -new -x509 -key priv.pem -out cert.pem -days 365
#              :
# Compile and  :
# run          : $ python3 client_launcher.py
#              :
#              :
# Directory    :
# structure    : launcher
#              : ├── client_launcher.py
#              : ├── data_access
#              : │   └── files.db
#              : ├── executables
#              : ├── keys
#              : │   ├── cert.pem
#              : │   ├── prk.pem
#              : │   └── puk.pem
#              : ├── server_launcher.py
#              : └── uploads
#              :
##   

from flask import Flask, request, jsonify
import os
import json
import subprocess
import stat
import signal
import sys

# Application settings
UPLOAD_FOLDER = 'uploads'
EXECUTABLE_FOLDER = 'executables'
ALLOWED_EXTENSIONS = {'c'}  # Only allow files with .c extension
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file size limit
FILE_DATABASE = 'data_access/file_database.json'

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXECUTABLE_FOLDER'] = EXECUTABLE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# In-memory file database
file_db = {}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_file_database():
    """Load the file database from the JSON file."""
    global file_db
    if os.path.exists(FILE_DATABASE):
        with open(FILE_DATABASE, 'r') as db_file:
            file_db = json.load(db_file)
        # Verify existence of files and executables
        for program_id, file_info in list(file_db.items()):
            if not os.path.exists(file_info['file_path']) or (file_info['executable'] and not os.path.exists(file_info['executable'])):
                del file_db[program_id]
        save_file_database()
    else:
        file_db = {}

def save_file_database():
    """Save the file database to the JSON file."""
    with open(FILE_DATABASE, 'w') as db_file:
        json.dump(file_db, db_file)

def handle_exit_signal(signum, frame):
    """Handle exit signals to save the database."""
    save_file_database()
    sys.exit(0)

# Register signal handlers to save the database on exit
signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint to upload a file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        secure_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0, os.SEEK_SET)

        if file_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large'}), 400

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(secure_filename)

        # Insert file information into the in-memory database
        program_id = len(file_db) + 1
        file_db[program_id] = {'file_name': filename, 'file_path': secure_filename, 'executable': None}
        save_file_database()

        return jsonify({'message': 'File successfully uploaded'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    """Endpoint to list all uploaded files."""
    files_list = [{'id': file_id, 'file_name': file_info['file_name'], 'file_path': file_info['file_path'], 'executable': file_info['executable']} for file_id, file_info in file_db.items()]
    return jsonify(files_list), 200

@app.route('/files/<int:program_id>', methods=['DELETE'])
def delete_file(program_id):
    """Endpoint to delete a specific file."""
    app.logger.debug(f"Delete request received for program ID: {program_id}")

    if program_id not in file_db:
        app.logger.error(f"File not found for program ID: {program_id}")
        return jsonify({'error': 'File not found'}), 404

    file_info = file_db.pop(program_id)
    save_file_database()

    app.logger.debug(f"File info to be deleted: {file_info}")

    if os.path.exists(file_info['file_path']):
        os.remove(file_info['file_path'])
    else:
        app.logger.warning(f"File path does not exist: {file_info['file_path']}")

    executable_path = file_info['executable']
    if executable_path and os.path.exists(executable_path):
        os.remove(executable_path)
    else:
        app.logger.warning(f"Executable path does not exist: {executable_path}")

    app.logger.info(f"File successfully deleted for program ID: {program_id}")
    return jsonify({'message': 'File successfully deleted'}), 200

@app.route('/compile/<int:program_id>', methods=['POST'])
def compile_program(program_id):
    """Endpoint to compile a specific program."""
    if program_id not in file_db:
        return jsonify({'error': 'Invalid program selected'}), 404

    file_info = file_db[program_id]
    file_path = file_info['file_path']
    if not os.path.exists(file_path):
        return jsonify({'error': 'File does not exist'}), 404

    executable_name = os.path.splitext(os.path.basename(file_path))[0]
    executable_path = os.path.join(app.config['EXECUTABLE_FOLDER'], executable_name)

    #compile_command = f"gcc {file_path} -o {executable_path} -lssl -lcrypto -lpthread"
    compile_command = f"clang-morello -march=morello+c64 -mabi=purecap -g -o {executable_path} {file_path} -L. -Wl,-dynamic-linker,/libexec/ld-elf-c18n.so.1 -lssl -lcrypto -lpthread"
    try:
        result = subprocess.run(compile_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error_output = result.stderr.decode('utf-8')

        # Log compilation output
        app.logger.info(f"Compilation output for program ID {program_id}:\n{output}")
        if error_output:
            app.logger.error(f"Compilation error output for program ID {program_id}:\n{error_output}")

        # Store the executable path in the in-memory database
        file_info['executable'] = executable_path
        save_file_database()

        return jsonify({'message': 'Compilation successful', 'output': output, 'error_output': error_output}), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Compilation failed for program ID {program_id}: {e}")
        return jsonify({'error': f'Compilation failed: {e}', 'output': e.output.decode('utf-8')}), 500

@app.route('/execute/<int:program_id>', methods=['POST'])
def execute_program(program_id):
    """Endpoint to execute a compiled program."""
    if program_id not in file_db:
        return jsonify({'error': 'Invalid program selected'}), 404

    executable_path = file_db[program_id]['executable']
    if not executable_path or not os.path.exists(executable_path):
        return jsonify({'error': 'Executable does not exist. Please compile the program first.'}), 404

    # Set execution permissions for the file
    os.chmod(executable_path, stat.S_IRWXU)

    # Execute the program using the specified command
    execute_command = f"env LD_C18N_LIBRARY_PATH=. {executable_path}"
    try:
        result = subprocess.run(execute_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error_output = result.stderr.decode('utf-8')

        # Log execution output
        app.logger.info(f"Execution output for program ID {program_id}:\n{output}")
        if error_output:
            app.logger.error(f"Execution error output for program ID {program_id}:\n{error_output}")

        return jsonify({'message': 'Execution successful', 'output': output, 'error_output': error_output}), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Execution failed for program ID {program_id}: {e}")
        return jsonify({'error': f'Execution failed: {e}', 'output': e.output.decode('utf-8')}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(EXECUTABLE_FOLDER, exist_ok=True)
    load_file_database()
    # Start the Flask server with HTTPS
    app.run(debug=True, ssl_context=('keys/cert.pem', 'keys/prk.pem'), host='127.0.0.1', port=5000)
