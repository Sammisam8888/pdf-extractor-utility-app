# PDF Extractor

A Flask application to extract and view PDFs from SelfStudys pages.

## Setup and Run

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

4.  **Open in browser:**
    Go to `http://127.0.0.1:5000`

## Usage
Paste a SelfStudys page URL (e.g., `https://www.selfstudys.com/books/...`) into the input box and click "Extract & View PDF".

## Server Deployment

To deploy on a server, you can use the provided helper script:

```bash
chmod +x deploy.sh
./deploy.sh
```

This will set up the environment and install dependencies. Then you can start the production server:

```bash
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

