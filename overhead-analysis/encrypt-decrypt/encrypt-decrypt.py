import os
import time
import csv
import subprocess

encrypt_file = "encrypt_results.csv"
decrypt_file = "decrypt_results.csv"
plaintext = b"A" * 128  
key = os.urandom(16).hex()
iv = os.urandom(16).hex()

with open("input_plain.txt", "wb") as f:
    f.write(plaintext)

ciphertexts = []

# ENCRYPT 
with open(encrypt_file, mode='w', newline='') as csvfile_enc:
    writer_enc = csv.writer(csvfile_enc)
    writer_enc.writerow(["iteration", "duration_ms"])

    for i in range(1, 101):
        out_file = f"enc_{i}.bin"
        start = time.perf_counter()
        subprocess.run([
            "openssl", "enc", "-aes-128-cbc", "-e",
            "-in", "input_plain.txt",
            "-out", out_file,
            "-K", key,
            "-iv", iv
        ], check=True, capture_output=True)
        end = time.perf_counter()
        duration = (end - start) * 1000
        writer_enc.writerow([i, f"{duration:.3f}"])
        ciphertexts.append(out_file)

# DECRYPT 
with open(decrypt_file, mode='w', newline='') as csvfile_dec:
    writer_dec = csv.writer(csvfile_dec)
    writer_dec.writerow(["iteration", "duration_ms"])

    for i, enc_file in enumerate(ciphertexts, 1):
        out_file = f"dec_{i}.bin"
        start = time.perf_counter()
        subprocess.run([
            "openssl", "enc", "-aes-128-cbc", "-d",
            "-in", enc_file,
            "-out", out_file,
            "-K", key,
            "-iv", iv
        ], check=True, capture_output=True)
        end = time.perf_counter()
        duration = (end - start) * 1000
        writer_dec.writerow([i, f"{duration:.3f}"])

os.remove("input_plain.txt")
for f in ciphertexts:
    os.remove(f)
    os.remove(f.replace("enc_", "dec_"))
