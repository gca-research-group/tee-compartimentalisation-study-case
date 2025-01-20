<h1 style="font-size: 2em;">A Use-case for Integrating Digital Services with Data Protection at Run Time</h1>

This repository focuses on evaluating two key attestable properties:

- The operation of the cloud-based attestation procedure discussed in the [attestablelauncher repository](https://github.com/CAMB-DSbD/attestablelauncher).
- Some performance properties of compartments created on a Morello Board, using a library compartmentalisation tool.

To explore these properties, we have implemented an **Enterprise Application Integration (EAI)** solution, also referred to as an **Integration Solution**, which operates within a trusted execution environment (TEE) on experimental Morello Board hardware.

In the implemented case study, a store offers a promotion to its customers: if a customer spends more than $150.00, they receive a ride home in an app-based car service, paid for by the store. This business strategy integrates the store’s operations with the transportation service, promoting sales and enhancing customer convenience through seamless digital service integration. The integration process is executed inside a TEE, demonstrating how secure communication and interaction between different digital services, running on distinct remote servers, can be achieved in a trusted environment.

We demonstrate how to execute an integration process within a TEE using Morello Board hardware located in Canada. The case study implements three mock digital services (apps) running on distinct remote servers in Brazil, along with an integration process (program) written and compiled for **CHERI capabilities (cheri-caps)**. The integration process runs inside a secure compartment.


## Conceptual View of the EAI

A conceptual view of the application involved in the EAI is illustrated in Figure 1.


<img src="./figs/EAI.png" alt="Conceptual View of the EAI" width="400">

*Figure 1: Conceptual View of the EAI.* 
<!--(Author: Carlos Molina-Jimenez, Computer Lab, University of Cambridge. CAMB project).-->


The EAI integrates three main components: the store, taxi, and messaging services. These components act as servers, and the EAI operates as a client that sends requests to these services. The interaction between the EAI and the component applications follows a message-driven process:

1. The EAI requests a copy of the bill for a store's client, for example, Alice.
2. The store responds with the bill amount. Let's assume the bill is above $150.00, which entitles Alice to a courtesy taxi ride.
3. The EAI sends a request to the taxi service to arrange a ride for Alice.
4. The taxi service responds with the taxi's number and the driver’s name, confirming that a taxi is ready for boarding.
5. The EAI then sends a message to Alice, offering her the taxi service.
6. Alice responds with an acceptance of the offer.


## Implementation architecture of the EAI

In the Figure 2, we assume that the implementation of the EAI is delegated to a third-party company (say, Bob's), and that the four involved parties do not necessarily trust each other. For example, the store, taxi, and messaging services are hesitant to provide their data to the EAI unless Bob implements mechanisms that ensure data protection during execution. This is a critical requirement that our implementation addresses. As shown in the following figure, we use an attestable to meet this requirement.


<img src="./figs/EAIwithATT.png" alt="Enterprise Application Integration with Data Protection" width="400">

*Figure 2: Enterprise Application Integration with Data Protection (Author: Carlos Molina-Jimenez, Computer Lab, University of Cambridge. CAMB project).*


In the Figure 2, we use the following notation: the applications (store, taxi, and messaging services) execute on conventional platforms, represented by the "env" boxes with single lines. The attestable (att) is depicted by a double-lined box to indicate that it provides an execution environment that guarantees data protection. The EAI is deployed and executed inside the attestable to protect the data provided by the applications. It's important to note that the EAI acts as a client of the three servers (store, taxi, and messaging) and is programmed to periodically make requests.

To illustrate the practicality of our current implementation, we highlight that the attestable is created on a Morello Board physically located in Toronto, while the applications run on conventional computers located at the Applied Computing Research Group of the University of Ijuí, Brazil.



# Functionality of the Components

### 1) App-Store, App-Transport, and App-Whatsapp

Each of these directories contains the following components:

- **API**: Each directory includes an API file (`API1.py`, `API2.py`, `API3.py`) responsible for providing specific endpoints:
  - **API1.py (App-Store)**: Provides the `/api/sales` endpoint to check the last sale.
  - **API2.py (App-Transport)**: Provides the `/api/trips` endpoint to book a trip.
  - **API3.py (App-Whatsapp)**: Provides the `/send-message` endpoint to send a confirmation message via WhatsApp.
- **Database**: The databases (`compras.db`, `transport_app.db`) are used to store relevant data for sales and transport bookings.
- **Key Pair**: Each application has its own key pair (`cert.pem`, `priv.pem`), used for secure communication.


### 2) Launcher

- **launcher.py**: A server that manages the upload, compilation, and execution of programs inside a TEE within secure compartments. It runs on the operating system outside the TEE and handles the following tasks:
  - Manages upload requests.
  - Compiles C code (`integration_process.c`) written with CHERI capabilities (cheri-caps).
  - Executes the compiled binary code inside a single compartment.
  - Creates and stores the required certificates locally, outside the TEE.
  
- **command-line-interface.py**: A command-line interface (CLI) client for interacting with the `launcher.py` server. It allows the user to:

  <div style="margin-left: 20px;">
    <ol>
      <li>List files.</li>
      <li>Upload a file.</li>
      <li>Delete a program.</li>
      <li>Compile a program.</li>
      <li>Execute a program.</li>
      <li>Exit.</li>
    </ol>
  </div>


- **generate_certificate.py**: This script generates certificates and keys for the `integration_process` executable binary code. The certificates include:
  - CPU model.
  - Number of CPUs.
  - Memory addresses.
  - Hash of the executable binary code.
  - Signature added to the certificate for attestation.

### Programs and Data Structure

- **programs-data-base/sources**: Contains the source code of programs written in C (e.g. `integration_process.c`).
- **programs-data-base/cheri-caps-executables**: Stores the executable binary codes generated for CHERI capabilities (cheri-caps).
- **programs-data-base/certificates**: Contains the attestables and the keys generated for the secure execution environment of each executable binary code.
- **attestable-data/signatures**: Stores the signatures of the executable binary codes for attestation purposes.

   
### Execution Sequence

1. **Launcher Initialisation**
   - The launcher is started by running `launcher.py`.
   - Once started, the launcher is ready to receive requests to upload, compile, and run programs.

2. **Code Upload**
   - The CLI (`command-line-interface.py`) is used to upload a C program (e.g. `integration_process.c`) to the Morello Board environment.
   - The launcher saves the uploaded file in the `programs-data-base/sources` folder and updates the `file_database.json`.

3. **Code Compilation**
   - A request to compile the source code is made via the CLI.
   - The launcher compiles the source code for CHERI capabilities and saves the executable binary code in the folder `programs-data-base/cheri-caps-executables`.
   - A corresponding certificate directory is created inside the folder `programs-data-base/certificates`.

4. **Code Execution**
   - The compiled binary code is executed via the CLI.
   - The launcher runs the binary and returns the output.

5. **Certificate Generation**
   - During execution, the `integration_process.c` calls the `generate_certificate.py` script located inside the folder `attestable-data`.
   - The `generate_certificate.py` script generates the corresponding keys and certificates for the running executable binary code, including information such as CPU model, number of CPUs, and memory addresses.

6. **Interaction with External APIs**
   - The `integration_process.c` makes HTTPS calls to the defined APIs (`API1_URL`, `API2_URL`, `API3_URL`), using OpenSSL to check sales, book trips, and send confirmation messages via WhatsApp.




# Attestation and Set-Up of the Attestable

The sequence diagram in Figure 3 represents the attestation and interaction process within the Integration Solution, managed by a **Launcher** program that operates outside the TEE but within the Morello Board operating system. The **Integration Process** functions as a client, interacting with remote servers hosting the digital service applications (apps).

![Sequence Diagram](./figs/launcher.png)

*Figure 3: Sequence diagram of the attestation and interaction process in the Integration Solution (Author: Rafael Zancan-Frantz, Applied Computing Research Group, Unijui University, Brazil).*


#### Explanation of the Sequence Diagram:

1. **Launcher Initialization**: The launcher begins the process by invoking the `start()` operation, which prepares the system to handle various operations, such as retrieving source code, compiling, and executing programs.

2. **Retrieving the Source Code**: For each source code, the launcher retrieves the necessary program (Integration Process) from its local database using the `retrieveProgram(id)` operation. This step fetches the source code of the **Integration Process**, essential for the subsequent operations.

3. **Compartment Creation**: The launcher requests the creation of a secure compartment by calling the `createCompartment()` operation in the Morello Board's operating system. This compartment provides a secure execution environment for the **Integration Process**.

4. **Source Code Compilation**: After retrieving the source code, the launcher compiles it for CHERI capabilities using the `compile(src)` operation. The result is an executable (`exe`) suitable for secure execution within the compartment.

5. **Deploying the Integration Process**: The compiled executable is then deployed within the compartment using the `deploy(exe)` operation. This deployment generates attestable data (`attestableData`), represented as a `HashMap`, which is crucial for ensuring the process operates securely inside the compartment.

6. **Key Pair Generation**: Inside the compartment, the **Integration Process** generates a key pair using the `generateKeyPair()` function. This pair consists of a public key (`puK`) and a private key (`prK`), which will be used for secure communication with the digital services.

7. **Certificate and Public Key Exchange**:
   - The `generateAttestableDoc()` operation is called to generate an attestable document containing the attestable data from the secure environment.
   - The public key of the **Integration Process** is retrieved using the `getPublicKey()` operation, ensuring secure interaction with external services.
   - The **Integration Process** gathers all available digital services using the `getIntegratedServices()` operation.
   - A key exchange occurs between the public key of the **Integration Process** and the external services using the `exchangeKeys(puK, services)` operation.

8. **Registering the Service's Public Key**: After the key exchange, the public keys of the digital services are securely stored via the `putServicePublicKey(srvId, puK_)` operation. This ensures that the keys are safely registered for communication with the **Integration Process**.

9. **Certificate Generation and Signing**: The launcher generates the final attestable certificate using the `generateCertificate(doc)` operation. This certificate is signed by a root certificate authority, such as Verisign, using the `sign(certificate)` operation to verify the integrity and authenticity of the process.

10. **Execution of the Integration Process**: Finally, the launcher invokes the `run()` operation, executing the compiled **Integration Process** within the secure compartment. At this point, the **Integration Process** can securely interact with external services (e.g., store, transportation, or messaging apps), ensuring data protection and the attestation of the trusted execution environment.

### Additional Considerations

- The secure compartment acts as a critical component in the execution, ensuring that all interactions and data exchanges remain encrypted and protected.
- The sequence of events includes not only the setup of the integration process but also important steps such as key exchange, certificate generation, and secure data transfer between services.
- The role of the root of trust (Verisign) ensures that the certificates used during the process are valid and can be trusted by external digital services.


# Execution of a Read Operation

The integration process is responsible for securely reading data from integrated digital services. This is accomplished through a read operation, with the **Integration Process** acting as the client and the **Digital Service** as the server. The sequence diagram in Figure 4 illustrates the sequence of events in the execution of a read operation that the EAI performs against one of the applications, such as the storage service, to request data.

![Sequence Diagram of the Read Operation](./figs/read.png)

*Figure 4: Sequence diagram of the read operation in the Integration Solution (Author: Rafael Zancan-Frantz, Applied Computing Research Group, Unijuí University, Brazil).*

The sequence diagram in Figure 4 provides a structured view of how data is securely retrieved from a digital service. Below is an explanation of the key steps involved in the read operation:

1. **Start of the Read Request**: The **Integration Process** initiates a read request to retrieve data from the **Digital Service**, identified by `srvId`. The goal is to obtain the dataset (`Dataset`).

2. **Request for Encrypted Data**: The **Integration Process** sends a request to the **Launcher**, asking for encrypted data (`EncDataset`) from the **Digital Service**. The `srvId` and `progId` are used to identify the digital service and the integration process.

3. **Service Lookup**: The **Launcher** locates the digital service using the service ID (`srvId`) and establishes a connection to it, typically via a RESTful service, using the `lockupService(srvId)` function.

4. **Retrieval of Signed Certificate**: The **Launcher** retrieves the signed certificate corresponding to the integration process by calling the `getCertificate(progId)` function. This certificate is necessary to verify that the integration process is running in a trusted execution environment.

5. **Obtaining the Public Key**: The **Launcher** then calls the `getProgramPublicKey(progId)` function to retrieve the public key (`puK`) of the **Integration Process**, which will be used for encrypting and decrypting the data.

6. **Requesting Data from the Service**: The **Launcher** sends a secure request to the **Digital Service**, providing both the signed certificate and the public key (`puK`), through the `request(signedCert, puK)` function.

7. **Certificate Verification**: The **Digital Service** verifies the certificate using the `verifyCertificate(signedCert)` function. If the certificate is valid (`r == true`), the service proceeds to retrieve the requested data.

8. **Data Retrieval and Encryption**: The **Digital Service** retrieves the requested dataset (`Dataset`) from its local storage by calling the `retrieveLocalData()` function and encrypts it using the public key (`puK`), through the `encrypt(puK, data)` function, to ensure that only the **Integration Process** can decrypt and access the data.

9. **Sending Encrypted Data**: The **Digital Service** sends the encrypted dataset (`dataEnc`) back to the **Launcher**, which forwards it to the **Integration Process**.

10. **Data Decryption**: The **Integration Process** uses its private key (`prK`) to decrypt the encrypted dataset. Once decrypted, the integration process has access to the dataset, completing the read operation by calling the `decrypt(prK, dataEnc)` function.

This interaction ensures that the data transferred between the **Integration Process** and the **Digital Service** remains encrypted and protected, with the **Launcher** acting as a facilitator but never having access to the actual data. The encryption and attestation-based verification ensure the security of the operation, confirming that only authorised integration processes can read and decrypt the data.



# Execution of a Write Operation

The integration process is responsible for securely sending processed data within the integration flow to integrated digital services. This process is carried out through a write operation, with the **Integration Process** acting as the client and the **Digital Service** as the server. The diagram in **Figure 5** illustrates the sequence of events during the execution of a write operation that the EAI performs to send data to one of the applications, such as a messaging service. For instance, the EAI executes a write operation to the messaging application to notify it that a client is ready for a taxi ride home.

![Sequence Diagram of the Write Operation](./figs/write.png)

*Figure 5: Sequence diagram of the write operation in the Integration Solution (Author: Rafael Zancan-Frantz, Applied Computing Research Group, Unijui University, Brazil).*

The sequence diagram in **Figure 5** provides a structured view of how data is securely transmitted from the **Integration Process** to a **Digital Service**. Below is an explanation of the steps involved in the write operation:

1. **Initiating the Write Request**: The **Integration Process** initiates a write request, specifying the destination **Digital Service**, identified by `srvId`, and the data to be sent.

2. **Retrieving the Public Key of the Service**: The **Integration Process** retrieves the public key (`puK_`) of the **Digital Service** using the `getServicePublicKey(srvId)` operation. This public key will be used to encrypt the data, ensuring secure transmission.

3. **Encrypting the Data**: The data is encrypted using the public key (`puK_`) retrieved in the previous step. The result is an encrypted dataset (`dataEnc`), which will be securely transmitted to the service.

4. **Sending the Encrypted Data**: The **Integration Process** sends the encrypted data (`dataEnc`) to the **Launcher** via the `write(srvId, progId, dataEnc)` operation. The `progId` identifies the integration process.

5. **Service Lookup**: The **Launcher** searches for the digital service using the `lockupService(srvId)` operation to locate the corresponding **Digital Service** for this request.

6. **Retrieving the Certificate**: The **Launcher** retrieves the signed certificate of the **Integration Process** using the `getCertificate(progId)` operation, which will be used to verify the integrity of the process.

7. **Sending the Encrypted Data**: The **Launcher** securely sends the encrypted data and the signed certificate to the **Digital Service** using the `post(signedCert, dataEnc)` operation.

8. **Verifying the Certificate**: The **Digital Service** verifies the provided certificate using the `verifyCertificate(signedCert)` operation. If the certificate is valid (`r == true`), the service proceeds to process the data.

9. **Decrypting the Data**: The **Digital Service** decrypts the encrypted data (`dataEnc`) using its private key (`prK_`), recovering the original dataset (`Dataset`).

10. **Storing the Data**: The decrypted data is locally stored in the service using the `storeLocalData(data)` operation, completing the write operation.

This sequence ensures that the data sent from the **Integration Process** to the **Digital Service** is encrypted and protected during transmission, with the **Launcher** acting as the communication facilitator without having access to the data. The encryption and attestable-based verification guarantee that only authorised and trusted integration processes can write data to the digital service.



## Acknowledgements

Special thanks to **Carlos Molina-Jimenez** ([carlos.molina@cl.cam.ac.uk](mailto:carlos.molina@cl.cam.ac.uk)), 
from the Computer Lab, University of Cambridge, for providing the architecture images, assisting in identifying the research problem, and supporting the project development as part of the CAMB project.

The UML diagrams were created by **Rafael Zancan-Frantz** ([rzfrantz@unijui.edu.br](mailto:rzfrantz@unijui.edu.br)), 
from the Applied Computing Research Group at Unijui University, Brazil. Along with **Carlos Molina-Jimenez**, Rafael served as mentor and guide throughout the entire project.



## Corresponding Author

**Regis Rodolfo Schuch**  
*Applied Computing Research (GCA) Group, Unijui University, Brazil*  
[regis.schuch@unijui.edu.br](mailto:regis.schuch@unijui.edu.br)

