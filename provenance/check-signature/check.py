##
# Programmer   : Regis Rodolfo Schuch
# Date         : 10 June 2024
#              : Applied Computing Research Group, Unijui University, Brazil
#              : regis.schuch@unijui.edu.br
#              :
# Title        : check.py 
#              :
# Description  : The code checks the integrity and authenticity of an executable file using digital signatures. 
#              : Firstly, it reads the contents of the executable file (integration_process) and the corresponding 
#              : digital signature (signature.txt). Next, it loads the file's public key (public_key.pem). Using the 
#              : hashlib library, the code calculates the executable's SHA-256 hash. To verify the signature, it 
#              : uses the uploaded public key and compares it with the calculated hash, applying the PSS padding 
#              : scheme and the SHA-256 hash algorithm. If the verification is successful, the code prints that the 
#              : signature is valid and that the executable has not been modified since it was signed. Otherwise, 
#              : it informs you that the signature is invalid or that the executable has been modified.
#              :
# Source       : Some inspiration from
#              : https://cryptography.io/_/downloads/en/latest/pdf/
#              : https://docs.python.org/3/library/hashlib.html
#              : https://www.youtube.com/watch?v=b2pj0yDhDp4
#              : https://www.youtube.com/watch?v=K0IJTb-5h8g
#              : https://www.youtube.com/watch?v=ImZ4GqyOK-M
#              : https://pycryptodome.readthedocs.io/en/latest/src/public_key/public_key.html
#              : https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/
#              : https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files    
#              : https://www.youtube.com/watch?v=z-EnysBSstA
#              :
#              :
# Install      :
# dependencies : The check.py code was executed on the Unix-enabled CheriBSD Operating System, which extends FreeBSD 
#              : to take advantage of Arm's Capability Hardware na Morello and CHERI-RISC-V platforms. 
#              : $ sudo pkg64 install python3
#              :
#              : $ sudo pkg64 install py39-pip
#              : 
#              : $ pip install cryptography
#              :
#              : $ sudo pkg64 install openssl
#              :
# Compile and  :
# run          : $ python3 check.py
#              :
#              :
# Directory    :
# structure    : provenance
#              : ├── check-signature
#              : │   └── check.py
#              : ├── generate-certificate
#              : │   ├── generate_certificate.py
#              : │   └── keys
#              : │       ├── certificate.pem
#              : │       ├── private_key.pem
#              : │       └── public_key.pem
#              : └── signature
#              :     └── file
#              :         └── signature.txt
#              :
##   

import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# Open the executable file in binary mode and read its content
with open('../../integration_process', 'rb') as code_file:
    code = code_file.read()

# Open the signature file in binary mode and read its content
with open('../signature/file/signature.txt', 'rb') as signature_file:
    signature = signature_file.read()

# Open the public key file in binary mode and load the public key
with open('../generate-keys/keys/public_key.pem', 'rb') as key_file:
    public_key = load_pem_public_key(key_file.read(), backend=default_backend())

# Calculate the SHA-256 hash of the executable file using the hashlib library
hasher = hashlib.sha256()
hasher.update(code)
digest = hasher.digest()

# Verify the signature using the public key and the calculated hash
try:
    public_key.verify(
        signature,
        digest,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Valid signature.")
    print("The code has not been modified since it was signed.")
except Exception as e:
    print("Invalid signature or the code has been modified since it was signed:", e)

