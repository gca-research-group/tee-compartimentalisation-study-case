# Case study of compartmentalisation-based TEE

# Description of Operation
1) App-Store, App-Transport and App-Whatsapp
- Each of these directories contains an API (API1.py, API2.py, API3.py), a database (compras.db, transport_app.db), and a key pair (cert.pem, priv.pem).
- The APIs are responsible for providing specific endpoints:
 - API1.py (App-Store): Provides the /api/sales endpoint to check the last sale.
 - API2.py (App-Transport): Provides the /api/trips endpoint to book a trip.
 - API3.py (App-Whatsapp): Provides the /send-message endpoint to send a confirmation message via WhatsApp.
2) Launcher
- launcher.py: A Flask server that manages the upload, compilation and execution of programmes. It handles upload requests, compiles the C code (integration_process.c), and allows the generated binary to be executed. Certificates are created and stored as required.
- command-line-interface.py: A CLI for interacting with the Flask server (launcher.py), allowing you to list files, upload, delete, compile and run programmes.
- generate_certificate.py: Generates certificates and keys for the integration_process executable. Includes information such as CPU model, number of CPUs, memory addresses, hash of the executable and its signature.
- Programmes and Data:
 - programs-data-base/sources: Contains the programme codes (e.g. integration_process.c).
 - programs-data-base/cheri-caps-executables: Contains the executables generated for cheri caps.
 - programs-data-base/certificates: Contains the attestables and keys generated for the execution environment of each executable.
 - attestable-data/signatures: Contains the signatures of the executables.
   
# Execution sequence
1) Launcher initialisation
 - The launcher is started by running launcher.py.
 - The launcher is ready to receive requests to upload, compile and run programmes.
2) Code upload
 - The CLI (command-line-interface.py) is used to upload a C programme (integration_process.c).
 - The launcher saves the file in the programs-data-base/sources folder and updates the file_database.json.
3) Code compilation
 - The request to compile the code is made via the CLI.
 - The launcher compiles the code for cheri caps and saves the executable in programs-data-base/cheri-caps-executables.
 - A corresponding certificate directory is created in programs-data-base/certificates.
4) Code execution
 - The compiled code is executed via the CLI.
 - The launcher executes the binary and returns the output.
5) Certificate generation
 - During execution, integration_process.c calls generate_certificate.py in attestable-data.
 - The generate_certificate.py script generates keys and certificates for the running executable, including information such as CPU model, number of CPUs, and memory addresses.
6) Interaction with External APIs
 - integration_process.c makes HTTPS calls to the defined APIs (API1_URL, API2_URL, API3_URL), using OpenSSL to check sales, book trips and send confirmation messages via WhatsApp.
