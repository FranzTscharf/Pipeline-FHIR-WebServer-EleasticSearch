from flask import Flask, request
from services import fetch_document_from_fhir, generate_elasticsearch_insert, send_to_elasticsearch
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/fhir-webhook', methods=['POST'])
def handle_fhir_webhook():
    # Extract the patient ID, document ID, and authentication token from the request
    patient_id = request.json['patient']
    document_id = request.json['documentReference']
    auth_token = request.json['authToken']

    # Fetch the document from the FHIR server
    document = fetch_document_from_fhir(document_id, auth_token)
    if document:
        # Generate a casting for the Elasticsearch insert statement
        elasticsearch_insert = generate_elasticsearch_insert(patient_id, document)

        # Send the Elasticsearch insert statement to Elasticsearch
        send_to_elasticsearch(elasticsearch_insert)

        return 'OK'
    else:
        return "Failed to fetch document", 500

if __name__ == '__main__':
    app.run()
