## Project Overview
This project is focused on extracting, processing, and organizing literary work metadata using ontologies and SPARQL queries. This project integrates **Goodreads data**, **ontological representations**, and **SPARQL queries** to construct structured knowledge bases about books, authors, and literary topics.

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python 3.9+
- Java (for SPARQL processing)
- [Docker](https://www.docker.com/) (optional for using the dev container)

### Install Dependencies
To install required Python packages, run:
```bash
pip install -r requirements.txt
```

### Running the Project

#### Fetch and Process Goodreads Data
To extract book details, genres, and topics from Goodreads:
```bash
python src/goodreads_books.py
python src/goodreads_topics.py
python src/goodreads_shelf.py
```

#### Run SPARQL Queries with SPARQL Anything
To generate RDF triples using SPARQL:
```bash
python src/pa_ex.py
```

#### Viewing RDF Outputs
After running the queries, you will find the processed RDF data in the `output/` directory. The RDF files can be viewed with tools like Protégé or a triple store like Apache Jena.

## Development Environment

### Using VS Code Dev Container
For an isolated development environment, use **VS Code with Dev Containers**:
1. Install **VS Code** and the **Remote - Containers** extension.
2. Open the project in VS Code.
3. Press `F1` and select **Remote-Containers: Open Folder in Container**.
4. The container will be built with all dependencies pre-installed.

## Data Sources
- [Goodreads](https://www.goodreads.com/) - Extracted book metadata
- **Ontology-based classification** - Used for knowledge organization
- **SPARQL Anything** - For querying JSON and CSV files

## Contribution
Feel free to contribute! Fork the repository, create a branch, make changes, and submit a pull request.

## License
This project is licensed under the MIT License.
