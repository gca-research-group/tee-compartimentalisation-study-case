# A Use-case for Integrating Digital Services with Data Protection at Execution-Time

**Abstract:** The integration of digital services is currently implemented by integration processes owned by third parties and executed in conventional computer with no mechanisms for preventing data exfiltration at execution-time. This is unacceptable when the integration processes retrieve highly sensitive data from digital services. To address this issue, we have designed iDevS, an API for the development of integration processes to be executed  within Trusted Execution Environments. We use smart cities as a context where such APIs are missing, e.g. to process medical data. iDevS API is agnostic to the underlying technologies, ensures data protection at execution--time and supports attestation of the execution environment. We discuss a case study to demonstrate its use.

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

### Overhead Analysis

The `overhead-analysis/` directory contains the scripts and results used to estimate the computational overhead introduced by the `Launcher` component. 

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
- **Operating System**: CheriBSD 24.05 
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
  libssl-dev \
  openssl \
  build-essential \
  clang \  
```

> On CheriBSD, use:  
> `sudo pkg64 install python39 py39-pip py39-openssl`

---

### Python Packages

Install all required Python packages:

```bash
pip install flask flask-talisman cryptography click requests
```

---
