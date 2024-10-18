<h1 style="font-size: 2em;">A use-case for attestable evaluation</h1>

This repository focuses on evaluating two key attestable properties:

- The operation of the cloud-based attestation procedure discussed in the [attestablelauncher repository](https://github.com/CAMB-DSbD/attestablelauncher).
- Some performance properties of compartments created on a Morello Board, using a library compartmentalisation tool.

To explore these properties, we have implemented an **Enterprise Application Integration (EAI)** solution, also referred to as an **Integration Solution**, which operates within a trusted execution environment (TEE) on experimental Morello Board hardware.

In the implemented case study, a store offers a promotion to its customers: if a customer spends more than $150.00, they receive a ride home in an app-based car service, paid for by the store. This business strategy integrates the store’s operations with the transportation service, promoting sales and enhancing customer convenience through seamless digital service integration. The integration process is executed inside a TEE, demonstrating how secure communication and interaction between different digital services, running on distinct remote servers, can be achieved in a trusted environment.

We demonstrate how to execute an integration process within a TEE using Morello Board hardware located in Canada. The case study implements three mock digital services (apps) running on distinct remote servers in Brazil, along with an integration process (program) written and compiled for **CHERI capabilities (cheri-caps)**. The integration process runs inside a secure compartment.


## Conceptual View of the Enterprise Application Integration (EAI)

A conceptual view of the application involved in the EAI is illustrated in Figure 1.


![Conceptual View of the EAI.](./EAI.png)

*Figure 1: Conceptual View of the EAI.* 


The EAI integrates three main components: the store, taxi, and messaging services. These components act as servers, and the EAI operates as a client that sends requests to these services. The interaction between the EAI and the component applications follows a message-driven process:

1. The EAI requests a copy of the bill for a store's client, for example, Alice.
2. The store responds with the bill amount. Let's assume the bill is above £150, which entitles Alice to a courtesy taxi ride.
3. The EAI sends a request to the taxi service to arrange a ride for Alice.
4. The taxi service responds with the taxi's number and the driver’s name, confirming that a taxi is ready for boarding.
5. The EAI then sends a message to Alice, offering her the taxi service.
6. Alice responds with an acceptance of the offer.






# Description

1) App-Store, App-Transport and App-Whatsapp
- Each of these directories contains an API (API1.py, API2.py, API3.py), a database (compras.db, transport_app.db), and a key pair (cert.pem, priv.pem).
- The APIs are responsible for providing specific endpoints:
 - API1.py (App-Store): Provides the /api/sales endpoint to check the last sale.
 - API2.py (App-Transport): Provides the /api/trips endpoint to book a trip.
 - API3.py (App-Whatsapp): Provides the /send-message endpoint to send a confirmation message via WhatsApp.
   
2) Launcher
- launcher.py: A server that manages the upload, compilation and execution of programs inside a TEE at compartments. It runs on the operating system outside the TEE and handles upload requests, compiles the C code (integration_process.c) written with cheri-caps, and allows the generated binary code to be executed inside a single compartment. It also creates and store the required certificates locally outside the TEE on the operating system.
- command-line-interface.py: A command line client interface (CLI) for interacting with the server (launcher.py), allowing to list files, upload, delete, compile and run programs.
- generate_certificate.py: Generates the certificates and keys for the integration_process executable binary code. It includes information such as CPU model, number of CPUs, memory addresses, hash of the executable binary code and its signature to the certificate.
- Programs and Data:
 - programs-data-base/sources: Contains the program source codes written in C language (e.g. integration_process.c).
 - programs-data-base/cheri-caps-executables: Contains the executable binary codes generated for cheri-caps.
 - programs-data-base/certificates: Contains the attestables and the keys generated for the execution environment of each executable binary code.
 - attestable-data/signatures: Contains the signatures of the executable binary codes.

   
# Execution sequence

1) Launcher initialisation
 - The launcher is started by running launcher.py.
 - The launcher is ready to receive requests to upload, compile and run programmes.
2) Code upload
 - The CLI (command-line-interface.py) is used to upload a C program (ex. integration_process.c) to the Morello Board Environment.
 - The launcher saves the uploaded file in the programs-data-base/sources folder and updates the file_database.json.
3) Code compilation
 - The request to compile the source code is made via the CLI.
 - The launcher compiles the source code for cheri caps and saves the executable binary code in folder programs-data-base/cheri-caps-executables.
 - A corresponding certificate directory is created inside the folder programs-data-base/certificates.
4) Code execution
 - The compiled binary code is executed via the CLI.
 - The launcher executes the binary and returns the output.
5) Certificate generation
 - During execution, the integration_process.c calls the generate_certificate.py located inside folder attestable-data.
 - The generate_certificate.py script generates the corresponding keys and certificates for the running executable binary code, including information such as CPU model, number of CPUs, and memory addresses.
6) Interaction with External APIs
 - The integration_process.c makes HTTPS calls to the defined APIs (API1_URL, API2_URL, API3_URL), using OpenSSL to check sales, book trips and send confirmation messages via WhatsApp.
