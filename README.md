# A Use-case for Integrating Digital Services with Data Protection at Run Time

The integration of digital services often involves sensitive data which is traditionally executed in untrusted execution environments that expose it to exfiltration risks, putting security and privacy under threat. This is unacceptable in applications that compute highly sensitive data. To address this issue, we present **iDevS**, an API designed for the development and execution of integration processes within **Trusted Execution Environments (TEEs)**. We use smart cities as a context where such APIs are missing, e.g. to process medical data. A salient feature of iDevS~API is that it is independent of underlying technologies. It ensures data protection at execution-time and supports attestation of the execution environment. We discuss a case study to demonstrate how it can be used.

---

## System Requirements

The experiments and implementation rely on the following system specifications:

- **Hardware**: ARM Research Morello Board based on the Research Morello SoC r0p0 processor  
- **CPU**: 4 cores  
- **RAM**: 16 GB DDR4 ECC (2933 MT/s)  
- **Architecture**: aarch64c with CHERI support  
- **Operating System**: CheriBSD 22.12 compiled using Clang with Morello extensions  
- **Execution Model**: CheriABI processes using `purecap` ABI 


---

## Integration Problem Overview

A conceptual view of the application involved in the EAI is illustrated in **Figure 1**.

![Conceptual View of the EAI](./figs/EAI-2.png)

*Figure 1: Conceptual view of the integration process.*

The scenario represents a strategy implemented by a store to attract and retain customers: it offers free transport back home to customers who spend at least \$150 in the store. The rewarded customers receive booking confirmation messages on their mobile phones. The integration process is responsible for automating and securely coordinating the interactions among three independent digital services:

- **Store Service**: Provides details about customers (e.g., mobile phone number and address) and their purchases (e.g., Total purchased).
- **Taxi Service**: Schedules transportation.
- **Messaging Service**: Sends booking confirmation messages.

To automate the coordination, the integration process executes the following *read* and *write* actions:

1. **Read Action**: Periodically executes *read* actions on the Store Service to retrieve customers' transaction details.  
2. **Eligibility Check**: Identifies customers who are eligible for free transport based on their purchase amount.  
3. **Write Action (Taxi Service)**: Executes a *write* action on the Taxi Service to request taxi services for the rewarded customers.  
4. **Write Action (Messaging Service)**: Executes a *write* action on the Messaging Service to send booking confirmations to the awarded customers.  

---

## Integration Process Design

![Architecture](./figs/case-study.png)

*Figure 2: Architecture of the integration process solution in the case study.*

The integration process runs in a secure memory compartment (indicated in yellow). The **Launcher** orchestrates compilation, deployment and secure communication with external digital services. It compiles the source code uploaded to it, signs the binary and generates a certificate with system attributes embedded as X.509 extensions. Data read/write actions are relayed by the Launcher without accessing their contents.

---

## Execution of a Read Action

![Read Operation](./figs/read.png)

*Figure 3: Operations to implement the read action for requesting data from a digital service.*

The integration process invokes `read(srvId)` → The Launcher verifies the executable’s certificate → The digital service validates the certificate and returns encrypted data → The integration process decrypts and uses the data.

---

## Execution of a Write Action

![Write Operation](./figs/write.png)

*Figure 4: Operations to implement the write action for posting data to a digital service.*

The integration process encrypts the payload with the service’s public key and calls `write(srvId, dataEnc)` → The Launcher attaches the certificate and sends it → The digital service validates the certificate and decrypts the data for local processing.

---

## Implementation and Execution

### 1) App-Store, App-Transport, and App-Whatsapp

Each of these directories includes:

- `API1.py`, `API2.py`, `API3.py`: REST APIs for reading sales, booking transport, and sending messages.
- SQLite databases (`compras.db`, `transport_app.db`).
- Certificates and keys (`cert.pem`, `priv.pem`).

### 2) Launcher

- `launcher.py`: Main server to manage upload, compilation, and execution.
- `command-line-interface.py`: CLI client to interact with the launcher.
- `generate_certificate.py`: Creates attestable certificates for compiled binaries.
- `programs-data-base/`: Stores source codes, executables, certificates and metadata.
- `attestable-data/signatures/`: Holds signature files for attestation.

### Execution Sequence

1. Run `launcher.py`.
2. Open `command-line-interface.py`.
3. Upload the C program (`integration_process.c`).
4. Compile the code for CHERI using purecap ABI.
5. Execute the program inside a CHERI compartment.
6. Certificates are generated automatically from hardware/software state.
7. `integration_process.c` performs secure HTTPS calls to APIs using OpenSSL.

---

## Directory Structure

```plaintext
launcher/
├── launcher.py                       # Core logic of the launcher
├── command-line-interface.py         # CLI client to interact with the launcher
├── attestable-data/
│   ├── generate_certificate.py       # Script to generate X.509 certificates
│   └── signatures/                   # Digital signatures of binaries
├── programs-data-base/
│   ├── file_database.json            # JSON metadata about uploaded programs
│   ├── sources/                      # Source files (*.c)
│   ├── cheri-caps-executables/       # Compiled binaries with CHERI capabilities
│   └── certificates/                 # Generated certificates for binaries
├── keys/
│   ├── cert.pem                      # Root certificate
│   ├── prk.pem                       # Private key
│   └── puk.pem                       # Public key
