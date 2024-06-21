import subprocess
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime
import hashlib
import os

# Function to run commands and capture output
def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")
        raise

# Get the hardware model
model = run_command(["sysctl", "-n", "hw.model"])
print(f"CPU Model: {model}")

# Get the number of CPUs
ncpu = run_command(["sysctl", "-n", "hw.ncpu"])
print(f"Number of CPUs: {ncpu}")

# Get memory addresses of the `integration_process`
proc_pid = sys.argv[1]

# Get memory addresses using `procstat`
mem_addresses = run_command(["procstat", "-v", proc_pid])
print(f"Memory Capabilities:\n{mem_addresses}")

# Generate the private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Save the private key to a file
with open("/home/regis/NB-LOCAL-attestable/launcher/attestable/generate-certificate/keys/private_key.pem", "wb") as key_file:
    key_file.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

# Get the public key
public_key = private_key.public_key()

# Save the public key to a file
with open("/home/regis/NB-LOCAL-attestable/launcher/attestable/generate-certificate/keys/public_key.pem", "wb") as key_file:
    key_file.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )

# Read the executable file and calculate its hash
executable_path = os.path.abspath('integration_process')
with open(executable_path, 'rb') as executable_file:
    executable_data = executable_file.read()

executable_hash = hashlib.sha256(executable_data).digest()

# Sign the calculated hash
signature = private_key.sign(
    executable_hash,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Save the signature to a file
with open('/home/regis/NB-LOCAL-attestable/launcher/attestable/signature/file/signature.txt', 'wb') as signature_file:
    signature_file.write(signature)

# Convert the hash and signature to hex strings for display
executable_hash_hex = executable_hash.hex()
signature_hex = signature.hex()

# Create an X.509 certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Rio Grande do Sul"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Ijui"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Unijui"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"Integration Process Certificate"),
])

# Create the certificate and include custom extensions
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    public_key
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    # Certificate valid for 1 year
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName("unijui.edu.br"),
    ]),
    critical=False
).add_extension(
    x509.UnrecognizedExtension(
        oid=x509.ObjectIdentifier("1.2.3.4.5.6.7.8.1"),
        value=bytes(f"Model: {model}", "utf-8")
    ),
    critical=False
).add_extension(
    x509.UnrecognizedExtension(
        oid=x509.ObjectIdentifier("1.2.3.4.5.6.7.8.2"),
        value=bytes(f"CPUs: {ncpu}", "utf-8")
    ),
    critical=False
).add_extension(
    x509.UnrecognizedExtension(
        oid=x509.ObjectIdentifier("1.2.3.4.5.6.7.8.3"),
        value=bytes(f"Memory: {mem_addresses}", "utf-8")
    ),
    critical=False
).add_extension(
    x509.UnrecognizedExtension(
        oid=x509.ObjectIdentifier("1.2.3.4.5.6.7.8.4"),
        value=executable_hash
    ),
    critical=False
).add_extension(
    x509.UnrecognizedExtension(
        oid=x509.ObjectIdentifier("1.2.3.4.5.6.7.8.5"),
        value=signature
    ),
    critical=False
).sign(private_key, hashes.SHA256(), default_backend())

# Save the certificate to a file
with open("/home/regis/NB-LOCAL-attestable/launcher/attestable/generate-certificate/keys/certificate.pem", "wb") as cert_file:
    cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

# Print success message and the executable hash
print(f"Executable SHA-256 Hash: {executable_hash_hex}")
print(f"Signature: {signature_hex}")
print("Private key, public key, and certificate generated successfully!")
