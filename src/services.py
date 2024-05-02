import requests
from elasticsearch import Elasticsearch
import os
import json

def fetch_document_from_fhir(document_id, auth_token):
    fhir_server_url = os.getenv('FHIR_SERVER_URL')
    document_url = f"{fhir_server_url}/DocumentReference/{document_id}"
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.get(document_url, headers=headers)
    return response.json() if response.status_code == 200 else None

def fetch_binary_document(url, auth_token=None):
    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
        return response.content  # Returns the content of the document as bytes
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def generate_elasticsearch_insert(document):
    doc_type = document.get('type', {}).get('coding', [{}])[0].get('display', 'Unknown Type')
    doc_category = document.get('category', [{}])[0].get('coding', [{}])[0].get('display', 'General')
    patient_info = next((item for item in document.get('contained', []) if item['resourceType'] == 'Patient'), None)
    patient_name = " ".join(patient_info.get('name', [{}])[0].get('given', [])) + " " + patient_info.get('name', [{}])[0].get('family', '') if patient_info else 'Unknown'
    author_info = next((item for item in document.get('contained', []) if item['resourceType'] == 'Practitioner'), None)
    author_name = " ".join(author_info.get('name', [{}])[0].get('given', [])) + " " + author_info.get('name', [{}])[0].get('family', '') if author_info else 'Unknown Author'
    organization_info = next((item for item in document.get('contained', []) if item['resourceType'] == 'Organization'), None)
    organization_name = organization_info.get('name', 'Unknown Organization') if organization_info else 'Unknown Organization'
    binary_content = fetch_binary_document(content_url, auth_token) if content_url else None


    es_document = {
        'document_id': document['id'],
        'document_type': doc_type,
        'document_content': binary_content,
        'category': doc_category,
        'patient_name': patient_name,
        'author_name': author_name,
        'organization_name': organization_name,
        'status': document.get('status', 'unknown'),
        'description': document.get('description', ''),
        'content_type': document.get('content', [{}])[0].get('attachment', {}).get('contentType', ''),
        'content_language': document.get('content', [{}])[0].get('attachment', {}).get('language', ''),
        'content_url': document.get('content', [{}])[0].get('attachment', {}).get('url', ''),
        'content_size': document.get('content', [{}])[0].get('attachment', {}).get('size', 0),
        'last_updated': document.get('meta', {}).get('lastUpdated', ''),
        'context_practice_setting': document.get('context', {}).get('practiceSetting', {}).get('coding', [{}])[0].get('display', 'Unknown'),
        'raw_document_meta_data': json.dumps(document)
    }
    return es_document

def create_index(index_name):
    """Creates an Elasticsearch index if it doesn't already exist."""
    es = Elasticsearch([{'host': os.getenv('ELASTICSEARCH_HOST'), 'port': os.getenv('ELASTICSEARCH_PORT')}])
    if not es.indices.exists(index=index_name):
        index_settings = {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "document_type": {"type": "keyword"},
                    "document_content": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "patient_name": {"type": "text"},
                    "author_name": {"type": "text"},
                    "organization_name": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "description": {"type": "text"},
                    "content_type": {"type": "keyword"},
                    "content_language": {"type": "keyword"},
                    "content_url": {"type": "keyword"},
                    "content_size": {"type": "integer"},
                    "last_updated": {"type": "date"},
                    "context_practice_setting": {"type": "keyword"},
                    "raw_document_data": {"type": "text"}
                }
            }
        }
        es.indices.create(index=index_name, body=index_settings)
        print(f"Created index {index_name}")
    else:
        print(f"Index {index_name} already exists")

