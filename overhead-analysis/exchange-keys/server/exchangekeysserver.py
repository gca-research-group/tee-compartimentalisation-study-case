from flask import Flask, request, jsonify
import os

app = Flask(__name__)

os.makedirs("received_keys", exist_ok=True)

@app.route("/exchange-key", methods=["POST"])
def exchange_key():
    data = request.get_json()
    sender_id = data.get("id")
    public_key_pem = data.get("public_key")

    if not sender_id or not public_key_pem:
        return jsonify({"error": "Missing ID or public key"}), 400

    key_path = f"received_keys/{sender_id}_pub.pem"
    with open(key_path, "w") as f:
        f.write(public_key_pem)

    return jsonify({"message": f"Public key from '{sender_id}' received."}), 200

if __name__ == "__main__":
    app.run(ssl_context=("cert.pem", "priv.pem"), host="0.0.0.0", port=8443)

