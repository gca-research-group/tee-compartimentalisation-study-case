# A Use-case for Integrating Digital Services with Data Protection at Run Time

**Abstract:** The integration of digital services often involves sensitive data which is traditionally executed in untrusted execution environments that expose it to exfiltration risks, putting security and privacy under threat. This is unacceptable in applications that compute highly sensitive data. To address this issue, we present iDevS, an API designed for the development and execution of integration processes within Trusted Execution Environments. We use smart cities as a context where such APIs are missing, e.g. to process medical data. A salient feature of iDevS API is that it is independent of underlying technologies. It ensures data protection at execution--time and supports attestation of the execution environment. We discuss a case study to demonstrate how it can be used.

---

## Integration Problem Overview

![Conceptual View of the EAI](./figs/EAI-2.png)

*Figure 1: Conceptual View of the EAI.*

A store rewards customers who spend at least \$150 with free transport home. These customers receive confirmation messages via WhatsApp. The integration process automates and secures interactions among three digital services:

- **Store Service**: Provides customer and purchase data.
- **Taxi Service**: Schedules transport.
- **Messaging Service**: Sends booking confirmations.

The integration process:
1. Periodically reads transactions from the Store Service.
2. Verifies if customers qualify.
3. Requests taxi service.
4. Sends a confirmation message.

---

## Integration Process Design

![Architecture of the Integration Process](./figs/case-study.png)

*Figure 2: Architecture of the integration solution using TEE and CHERI compartments.*

The `Integration Process` runs in a memory-compartmented environment on the Morello Board. The `Launcher`, running in the normal environment, handles compilation, certificate generation, and execution. Digital services remain external and untrusted.

The Launcher relays encrypted requests and responses between the integration process and external services. It compiles source code, generates X.509 certificates, and executes the process inside a secure CHERI compartment.

---

## Execution of a Read Action

![Read Operation](./figs/read.png)

*Figure 3: Read action flow from the integration process to a digital service.*

Steps:
1. `Integration Process` invokes `read(srvId)`.
2. `Launcher` verifies the program using its certificate and retrieves the public key.
3. `Launcher` sends a `request()` to the digital service with the signed certificate and public key.
4. Digital service validates the certificate:
   - Is it signed by a trusted CA (e.g., VeriSign)?
   - Are the attestable attributes trustworthy?
5. If valid, the service fetches data, encrypts it with the integration process’s public key.
6. Encrypted data is returned through the Launcher.
7. `Integration Process` decrypts the data using its private key.

---

## Execution of a Write Action

![Write Operation](./figs/write.png)

*Figure 4: Write action flow to transmit encrypted data to a digital service.*

Steps:
1. `Integration Process` encrypts the payload using the target service’s public key.
2. Calls `write(srvId, dataEnc)` on the `Launcher`.
3. `Launcher` attaches the signed certificate and forwards the encrypted data to the digital service.
4. The digital service verifies the certificate (as above).
5. If valid, it decrypts the data using its private key and stores it locally.

---

## Component Overview

### App-Store, App-Transport, and App-Whatsapp

Each application includes:
- REST APIs: `API1.py`, `API2.py`, `API3.py`
- Databases: `compras.db`, `transport_app.db`
- Key pairs: `cert.pem`, `priv.pem`
- Certificate verification logic: `verifyCertificate.py`

| Service         | Endpoint        | Description                        |
|----------------|-----------------|------------------------------------|
| App-Store      | `/api/sales`    | Check last sale                    |
| App-Transport  | `/api/trips`    | Book trip                          |
| App-Whatsapp   | `/send-message` | Send booking confirmation message  |

### Launcher

Responsible for:
- Receiving program uploads
- Compiling with CHERI (`clang-morello`, `-mabi=purecap`)
- Creating X.509 certificates with hardware metadata
- Executing in a secure compartment
- Handling secure HTTPS interactions

#### Key Files
- `launcher.py`: Main server
- `command-line-interface.py`: CLI client
- `generate_certificate.py`: Generates attestable certificates
- `file_database.json`: Metadata of uploaded files

#### Directory Structure
```plaintext
launcher/
├── launcher.py
├── command-line-interface.py
├── attestable-data/
│   ├── generate_certificate.py
│   └── signatures/
├── programs-data-base/
│   ├── file_database.json
│   ├── sources/
│   ├── cheri-caps-executables/
│   └── certificates/
├── keys/
│   ├── cert.pem
│   ├── prk.pem
│   └── puk.pem
```

---

## Execution Instructions

1. **Start the Launcher**
```bash
$ python3 launcher.py
```

2. **Run the CLI**
```bash
$ python3 command-line-interface.py
```

---

## System Requirements

- **Hardware**: Research Morello Board (Research Morello SoC r0p0)
- **CPU**: 4 cores
- **RAM**: 16 GB DDR4
- **Architecture**: aarch64c with CHERI support
- **Operating System**: CheriBSD 22.12 
- **Execution Model**: CheriABI processes using `purecap` ABI

---

## Installation

### System Dependencies

Run the following commands to install the required system packages:

```bash
sudo apt-get update
sudo apt-get install \
  python3 \
  python3-pip \
  python3-tk \
  sqlite3 \
  libsqlite3-dev \
  libssl-dev \
  openssl \
  build-essential \
  clang \  
```

> On CheriBSD, use:  
> `sudo pkg64 install python3 py39-pip openssl curl sqlite3`

---

### Python Packages

Install all required Python packages:

```bash
pip install flask flask-talisman cryptography click requests
```

---

### CHERI Compilation

Make sure you have the **Morello toolchain** installed and accessible (e.g., `clang-morello`).  
Compile your C programs using the following flags:

```bash
clang-morello -march=morello+c64 -mabi=purecap -g -o integration_process integration_process.c \
  -L. -Wl,-dynamic-linker,/libexec/ld-elf-c18n.so.1 -lssl -lcrypto -lpthread
```

---

### Certificate Generation

The certificates are generated by `generate_certificate.py` and require:

- Python cryptography module (already listed above)
- `procstat` command (included in CheriBSD)
- CHERI-compiled executable to extract memory metadata

The script is automatically triggered by `integration_process.c` using:

```c
system("python3 .../generate_certificate.py <pid>");
```

Certificates are stored in:
```
launcher/programs-data-base/certificates/
```

---
