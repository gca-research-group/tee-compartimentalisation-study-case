##
# Programmer   : Regis Rodolfo Schuch
# Date         : 10 June 2024
#              : Applied Computing Research Group, Unijui University, Brazil
#              : regis.schuch@unijui.edu.br
#              :
# Title        : API3.py 
#              :
# Description  : The API3.py code defines a RESTful API using Flask to send confirmation messages via WhatsApp 
#              : using the Twilio service. The application is configured with the Twilio account credentials 
#              : (Account SID and Authentication Token) and initialises a Twilio client. The /send-message 
#              : route accepts POST requests, where it receives a phone number and a message in JSON format. 
#              : The send_whatsapp_confirmation_message function is called to send the message via Twilio. The 
#              : application returns a success or error status based on the result of the operation. The application 
#              : runs with SSL/TLS support for security, using specified certificates (cert.pem and priv.pem), and 
#              : is configured to run on host 200.17.87.183 on port 8080.
#              :
# Source       : Some inspiration from
#              : https://flask.palletsprojects.com/en/3.0.x/
#              : https://www.twilio.com/
#              : https://www.twilio.com/pt-br/blog/como-enviar-mensagens-com-midia-em-anexo-no-whatsapp-em-python
#              : https://documentation.botcity.dev/pt/plugins/twilio/whatsapp/
#              : https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/
#              : https://medium.com/@bubu.tripathy/best-practices-for-designing-rest-apis-5b1809545e3c    
#              : https://towardsdatascience.com/creating-restful-apis-using-flask-and-python-655bad51b24
#              : https://auth0.com/blog/developing-restful-apis-with-python-and-flask/   
#              : https://medium.com/@geekprogrammer11/understanding-ssl-with-flask-api-d0b137906cbd
#              : https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
#              :
#              :
# Install      :
# dependencies : The API3.py code was run on Linux, on the Ubuntu 22.04.4 LTS distribution
#              : $ sudo apt-get install python3
#              :
#              : $ sudo apt update
#              : $ sudo apt install python3-pip
#              : 
#              : $ sudo apt-get install libsqlite3-dev
#              :
#              : $ pip install Flask twilio
#              :
#              : Creation of keys and certificates with:
#              : $ sudo apt install openssl
#              :
#              : Generate the private key:
#              : $ openssl genpkey -algorithm RSA -out priv.pem -pkeyopt rsa_keygen_bits:2048
#              : Extract the public key from the private key:
#              : $ openssl rsa -in priv.pem -pubout -out public_key.pem
#              : Generate the certificate:
#              : $ openssl req -new -x509 -key priv.pem -out cert.pem -days 365
#              :
# Compile and  :
# run          : $ python3 API3.py
#              :
#              :
# Directory    :
# structure    : app-whatsapp
#              : ├── api
#              : │   └── API3.py
#              : └── keys
#              :     ├── cert.pem
#              :     |── priv.pem
#              :     └── public_key.pem
#              :
##   

from flask import Flask, request, jsonify
from twilio.rest import Client

# Configuration of Twilio Account SID and Authentication Token
account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
auth_token = 'AUXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Initialize the Flask App
app = Flask(__name__)

def send_whatsapp_confirmation_message(number, message):
    try:
        # Send the message via Twilio
        message = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
            to=f'whatsapp:{number}'
        )
        print("Confirmation message sent via WhatsApp.")
    except Exception as e:
        print("Error sending confirmation message via WhatsApp:", e)

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        # Get the request data
        data = request.get_json()
        
        # Extract the phone number and message
        phone_number = data['numero_telefone']
        message = data['mensagem']
        
        # Call the function to send the message via Twilio
        send_whatsapp_confirmation_message(phone_number, message)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    context = ('../keys/cert.pem', '../keys/priv.pem')
    app.run(host='200.17.87.183', port=8080, ssl_context=context, debug=False, use_reloader=False)

