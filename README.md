# URL Shortener

A simple and responsive URL Shortener built using Python Flask, SQLite, HTML, CSS and JavaScript.

## Features

- Shorten long URLs
- Validate URL format
- Check whether the webpage is reachable
- Detect common not-found pages
- Generate unique 6-character short URLs
- Store URLs using SQLite
- Redirect short URLs to original URLs
- Copy shortened URL
- Paste URL from clipboard
- Clear URL input
- Responsive dark UI

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Requests

## Project Structure

```text
url-shortener/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   ├── app.css
│   └── app.js
│
└── templates/
    └── index.html