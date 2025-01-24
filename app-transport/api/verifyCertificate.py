import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Define VERIFY_SIGNATURE as True to verify the certificate's signature
VERIFY_SIGNATURE = True

# Function to check if extension data contains specific strings
def check_extension_data(data, check_strs):
    try:
        lines = data.decode().split('\n')
    except UnicodeDecodeError:
        # If decoding fails, treat data as binary
        lines = [data.hex()]
    
    found = {check_str: False for check_str in check_strs}
    for line in lines:
        for check_str in check_strs:
            if check_str in line:
                found[check_str] = True
    return found

# Function to verify if the certificate is signed by a CA
def is_cert_signed_by_ca(cert, ca_cert):
    try:
        ca_public_key = ca_cert.public_key()
        ca_public_key.verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
        return True
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return False

def check_certificate(cert_pem):
    ca_cert_path = "ca_cert.pem"
    
    # Load the root CA certificate
    with open(ca_cert_path, "rb") as f:
        ca_cert_data = f.read()
    
    ca_cert = x509.load_pem_x509_certificate(ca_cert_data, default_backend())
    
    # Verify the certificate's signature if VERIFY_SIGNATURE is True
    if VERIFY_SIGNATURE:
        is_valid = is_cert_signed_by_ca(cert_pem, ca_cert)
        if not is_valid:
            return False, "Certificate is not signed by a trusted CA"
    
    # Specific checks
    check_strings = ['CheriBSD 22.12', 'Research Morello SoC r0p0']
    found_any = check_extension_data(cert_pem.tbs_certificate_bytes, check_strings)
    
    if not all(found_any.values()):
        return False, "Execution environment is not secure"
    
    return True, "Certificate is valid"

# Example usage
if __name__ == "__main__":
    # Load the certificate to be verified
    with open("certificate.pem", "rb") as f:
        cert_data = f.read()
    
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    result, message = check_certificate(cert)
    print(f"{message}")

