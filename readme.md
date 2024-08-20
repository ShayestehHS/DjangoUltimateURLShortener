# Django Ultimate URL Shortener

This repository contains a URL shortener service that generates and manages short URLs.  
The service is optimized for performance using caching mechanisms and custom database indexing.  
A Celery-based task periodically manages the availability of tokens.  

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Database Structure](#database-structure)
- [Cache Usage](#cache-usage)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **URL Shortening**: Convert long URLs into short, easily shareable links.
- **Token Management**: Efficient token generation and assignment through scheduled tasks.
- **Caching**: Optimized URL retrieval using caching mechanisms.
- **Database Indexing**: Improved query performance with specific indexing strategies.

## How It Works

1. **Token Generation**:
    - A Celery beat task runs every 4 hours to ensure that there are at least 4 pre-generated tokens available in the database.
    - The task checks if there are 4 rows in the database with the `url` column value set to `READY_TO_SET_TOKEN_URL`.
    - If fewer than 4 rows are available, the task creates additional rows with `READY_TO_SET_TOKEN_URL` and assigns tokens to them.

2. **URL Creation**:
    - When a new URL needs to be shortened, the system checks for a row in the database where the `url` column value is `READY_TO_SET_TOKEN_URL`.
    - If such a row exists, it updates the `url` value to the desired URL.
    - If no such row is found, the system triggers the token generation process to ensure availability.

## Database Structure

- **Indexes**:
    1. **Hash Index on `token` Field**: This index allows for fast retrieval of URLs based on their tokens.
    2. **Conditional Index on `url` Field**: This index is applied to rows where the `url` column value is `READY_TO_SET_TOKEN_URL`. It optimizes the process of checking the availability of pre-generated tokens.

## Cache Usage

Caching is employed to store frequently accessed URLs and tokens, reducing the load on the database and improving response times.

## Installation

To install and run the URL shortener service, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ShayestehHS/DjangoUltimlateURLShortener.git
   cd url-shortener

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt

3. **Set Up the Database**:
Ensure your database is configured correctly with the necessary indexes.

4. **Run Migrations**:
    ```bash
    python manage.py migrate

5. **Start Celery**:
    ```bash
    celery -A your_project beat -l info
    celery -A your_project worker -l info

6. **Run the Server**:
    ```bash
    python manage.py runserver

## Usage
Once the service is running, you can start shortening URLs by interacting with the provided API endpoints.

## Contributing
Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.