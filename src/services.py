import requests
from elasticsearch import Elasticsearch
import os

def fetch_document_from_fhir(document_id, auth_token):
    # Construct the URL for fetching the document from the FHIR server
    fhir_server_url = os.getenv('FHIR_SERVER_URL')
    document_url = f"{fhir_server_url}/DocumentReference/{document_id}"

    # Set the headers for authentication
    headers = {'Authorization': f'Bearer {auth_token}'}

    # Fetch the document using the constructed URL and headers
    response = requests.get(document_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def generate_elasticsearch_insert(patient_id, document):
    # Extract the relevant data from the document
    document_id = document['id']
    document_content = document.get('content', {})

    # Create the Elasticsearch insert statement
    elasticsearch_insert = {
        'patient_id': patient_id,
        'document_id': document_id,
        'document_content': document_content
    }

    return elasticsearch_insert

def send_to_elasticsearch(elasticsearch_insert):
    # Connect to the Elasticsearch instance
    es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'), 'port': os.getenv('ELASTICSEARCH_PORT')}])

    # Index the document in Elasticsearch
    es.index(index=os.getenv('ELASTICSEARCH_INDEX'), body=elasticsearch_insert)
