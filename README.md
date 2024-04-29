# FHIR to Elasticsearch Pipeline

This project sets up a pipeline that listens for new documents from a HAPI FHIR Server, triggers a webhook on a custom web server, and then inserts the document into an Elasticsearch index.

## Prerequisites

- Python 3.7 or higher
- HAPI FHIR Server
- Elasticsearch

## Installation

1. Clone the repository:

git clone


2. Install the required dependencies:

pip install -r requirements.txt



## Configuration

1. Create a subscription on the HAPI FHIR Server using the `fhir_subscription.json` file.
2. Update the `web_server.py` file with the correct Elasticsearch connection details.
3. Start the Flask web server middleware:

python src/app.py



## Usage

1. Trigger a new document creation on the HAPI FHIR Server.
2. Verify that the document is indexed in the Elasticsearch instance.

## Contributing

If you find any issues or have suggestions for improvements, feel free to open a new issue or submit a pull request.

## License

This project is licensed under the MIT.


