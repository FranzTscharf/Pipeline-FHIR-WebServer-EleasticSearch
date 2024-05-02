from flask import Flask, request, jsonify
from services import fetch_document_from_fhir, generate_elasticsearch_insert, send_to_elasticsearch, create_index
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/fhir-webhook', methods=['POST'])
def handle_fhir_webhook():
    # Extract document ID and authentication token from the request
    document_id = request.json['documentReference']
    auth_token = request.json['authToken']

    # Fetch the document from the FHIR server
    document = fetch_document_from_fhir(document_id, auth_token)
    if document:
        # Check if the index exists and create it if not
        index_name = 'your_index_name'  # Set the index name
        create_index(index_name)

        # Generate the Elasticsearch document
        elasticsearch_document = generate_elasticsearch_insert(document, auth_token)

        # Send the Elasticsearch document to the Elasticsearch index
        send_to_elasticsearch(index_name, elasticsearch_document)

        return jsonify({"message": "Document indexed successfully"}), 200
    else:
        return jsonify({"error": "Failed to fetch document"}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug for development environment
