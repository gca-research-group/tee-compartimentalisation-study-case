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
import sqlite3
import subprocess
import stat

# Application settings
DATABASE = 'data_access/files.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'c'}  # Only allow files with .c extension
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file size limit

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

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

        # Insert file information into the database
        connection = get_db_connection()
        connection.execute('INSERT INTO Files (file_name, file_path, executable) VALUES (?, ?, ?)', 
                           (filename, secure_filename, None))
        connection.commit()
        connection.close()

        return jsonify({'message': 'File successfully uploaded'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    """Endpoint to list all uploaded files."""
    connection = get_db_connection()
    files = connection.execute('SELECT * FROM Files').fetchall()
    connection.close()

    files_list = [{'id': file['id'], 'file_name': file['file_name'], 'file_path': file['file_path']} for file in files]
    return jsonify(files_list), 200

@app.route('/files/<int:program_id>', methods=['DELETE'])
def delete_file(program_id):
    """Endpoint to delete a specific file."""
    connection = get_db_connection()
    file_info = connection.execute('SELECT * FROM Files WHERE id = ?', (program_id,)).fetchone()
    if not file_info:
        return jsonify({'error': 'File not found'}), 404

    connection.execute('DELETE FROM Files WHERE id = ?', (program_id,))
    connection.commit()
    connection.close()

    if os.path.exists(file_info['file_path']):
        os.remove(file_info['file_path'])

    return jsonify({'message': 'File successfully deleted'}), 200

@app.route('/compile/<int:program_id>', methods=['POST'])
def compile_program(program_id):
    """Endpoint to compile a specific program."""
    connection = get_db_connection()
    file_info = connection.execute('SELECT * FROM Files WHERE id = ?', (program_id,)).fetchone()
    connection.close()

    if not file_info:
        return jsonify({'error': 'Invalid program selected'}), 404

    file_path = file_info['file_path']
    if not os.path.exists(file_path):
        return jsonify({'error': 'File does not exist'}), 404

    executable_name = os.path.splitext(os.path.basename(file_path))[0]
    executable_path = os.path.join(app.config['UPLOAD_FOLDER'], executable_name)

    compile_command = f"gcc {file_path} -o {executable_path}"
    try:
        result = subprocess.run(compile_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        error_output = result.stderr.decode('utf-8')

        # Log compilation output
        app.logger.info(f"Compilation output for program ID {program_id}:\n{output}")
        if error_output:
            app.logger.error(f"Compilation error output for program ID {program_id}:\n{error_output}")

        # Store the executable in the database
        with open(executable_path, 'rb') as f:
            executable_data = f.read()

        connection = get_db_connection()
        connection.execute('UPDATE Files SET executable = ? WHERE id = ?', (executable_data, program_id))
        connection.commit()
        connection.close()

        # Remove the file from the filesystem after storing it in the database
        os.remove(executable_path)
        return jsonify({'message': 'Compilation successful', 'output': output, 'error_output': error_output}), 200
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Compilation failed for program ID {program_id}: {e}")
        return jsonify({'error': f'Compilation failed: {e}', 'output': e.output.decode('utf-8')}), 500

@app.route('/execute/<int:program_id>', methods=['POST'])
def execute_program(program_id):
    """Endpoint to execute a compiled program."""
    connection = get_db_connection()
    file_info = connection.execute('SELECT * FROM Files WHERE id = ?', (program_id,)).fetchone()
    connection.close()

    if not file_info:
        return jsonify({'error': 'Invalid program selected'}), 404

    executable_data = file_info['executable']
    if not executable_data:
        return jsonify({'error': 'Executable does not exist. Please compile the program first.'}), 404

    executable_name = os.path.splitext(os.path.basename(file_info['file_path']))[0]
    executable_path = os.path.join(app.config['UPLOAD_FOLDER'], executable_name)

    # Write the executable back to the filesystem
    with open(executable_path, 'wb') as f:
        f.write(executable_data)

    # Set execution permissions for the file
    os.chmod(executable_path, stat.S_IRWXU)

    execute_command = f"./{executable_path}"
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
    finally:
        os.remove(executable_path)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Start the Flask server with HTTPS
    app.run(debug=True, ssl_context=('keys/cert.pem', 'keys/prk.pem'), host='127.0.0.1', port=5000)

