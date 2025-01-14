# Reddit Keyword Alert System

This project is a Python-based application that monitors a specified subreddit for posts and comments containing predefined keywords. When matches are found, the application sends a summary email containing the relevant links. It uses Reddit's API via the `praw` library, PostgreSQL for database management, and Heroku for deployment.

## Features

- Monitors specific keywords in posts and comments.
- Sends email summaries with timestamps and URLs.
- Tracks processed URLs to avoid duplicate alerts.
- Deployable on Heroku for continuous monitoring.

## Requirements

### Local Environment

- Python 3.8+
- PostgreSQL
- Heroku CLI (for deployment)
- Required Python libraries (see `requirements.txt`):
  - `praw`
  - `smtplib`
  - `email`
  - `psycopg2-binary`

## Installation Instructions

### Local Installation

1. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database**
   Ensure PostgreSQL is running and create the required table:

   ```bash
   python -c "import psycopg2; psycopg2.connect(os.getenv('DATABASE_URL')).cursor().execute('CREATE TABLE IF NOT EXISTS processed_urls (url TEXT PRIMARY KEY);')"
   ```

4. **Run the Application**

   ```bash
   python app.py
   ```

### Deploying to Heroku

1. **Install Heroku CLI**
   Follow the instructions from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).

2. **Log in to Heroku**

   ```bash
   heroku login
   ```

3. **Create a New Heroku App**

   ```bash
   heroku create <app_name>
   ```

4. **Deploy the App**

   ```bash
   git push heroku main
   ```

5. **Start the Application**

   ```bash
   heroku ps:scale worker=1
   ```

## Usage

- The application continuously monitors the specified subreddit.
- Matches are logged in the PostgreSQL database to avoid duplicate alerts.
- Emails are sent to the specified recipients with details of the matched posts and comments.

## Viewing PostgreSQL Logs

To view PostgreSQL logs on Heroku, follow these steps:

1. **Fetch PostgreSQL Logs via Heroku CLI**

   ```bash
   heroku logs --source heroku-postgres --app <app_name>
   ```

2. **Continuously Monitor Logs**

   ```bash
   heroku logs --tail --source heroku-postgres --app <app_name>
   ```

These commands will provide detailed information about PostgreSQL activities on Heroku.

## Error Handling

- API errors are retried with a delay.
- Unhandled exceptions are logged, and the application attempts to recover.
- The application waits 12 hours between scans to prevent excessive API usage and rate limiting.

## Notes

- Ensure your email account has the necessary permissions (e.g., allow less secure app access or use an app password).
- Verify that the database URL is correctly configured on Heroku for seamless operation.
- Check Heroku logs for troubleshooting:

   ```bash
   heroku logs --tail
   ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.


For questions or support, contact `ardagumuss@outlook.com`.

