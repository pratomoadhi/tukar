# PDF Translation

This project consists of a backend API for translation and a frontend Flutter application for PDF upload.

## Project Structure

The project is organized into the following directories:

* `backend`: Contains the Translation API built with FastAPI.
* `frontend`: Contains the Flutter application for PDF upload.

## Backend: Translation API (FastAPI)

### Features

* Sentence translation functionality.
* API endpoints for file upload and translation.
* Built with FastAPI framework.

### Technologies Used

* FastAPI
* Python

### Setup Instructions

1.  Navigate to the `backend` directory: `cd backend`
2.  Install the required dependencies: `pip install -r requirements.txt` (if you have a requirements.txt)
3.  Run the FastAPI application: `uvicorn main:app --reload` (if your main file is main.py and app is the FastAPI instance)
4.  The API will be accessible at `http://localhost:8000` (default).

### Endpoints

* \[List the API endpoints and their functionalities, e.g.,
    * `POST /translate-pdf`: Translate uploaded pdf content.
    ]

## Frontend: PDF Upload and Translation (Flutter)

### Features

* PDF upload functionality.
* User-friendly interface.
* Built with Flutter.

### Technologies Used

* Flutter
* Dart
* \[Add any other specific packages used, e.g., flutter\_pdfview, google\_ml\_kit]

### Setup Instructions

1.  Navigate to the `frontend` directory: `cd frontend`
2.  Ensure you have Flutter installed and configured.  See the [Flutter installation guide](https://docs.flutter.dev/get-started/install) for details.
3.  Get the dependencies: `flutter pub get`
4.  Run the Flutter application: `flutter run`

### Prerequisites

* Flutter SDK installed on your machine.
* A connected Android or iOS device or emulator.

## Additional Notes

* Ensure that the backend API is running before running the Flutter application.
* Configure the API endpoint in the Flutter application to match your backend server address.
* \[Add any other relevant information, such as environment variables, database setup, etc.]