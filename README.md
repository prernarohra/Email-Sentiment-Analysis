# Email-Sentiment-Analysis
<img src="https://media.sproutsocial.com/uploads/2020/01/Insights-Featured-Art.png" alt="Email Sentiment Analysis" width="900" height="400">

## :clipboard: Overview
This project uses the OpenAI API for performing sentiment analysis on emails and integrates the Calendly API for efficient event management. It also uses Docker for containerization and PostgreSQL as the database, providing a robust and scalable solution for automating sentiment analysis and event scheduling.

## :sparkles: Features
- Sentiment Analysis: Uses OpenAI API to analyze sentiment from email content.
- Event Management: Integrates Calendly API for scheduling and managing events.
- Containerized Deployment: Docker setup for easy deployment.
- Database Management: Uses PostgreSQL to store and manage email and event data.

## :wrench: Installation
1. Clone this repository:

```bash
# Clone the repository
git clone https://github.com/yourusername/your-repository-name.git

# Navigate to the project directory
cd your-repository-name
```

2. Create a .env file in the root directory to securely store your API keys and email credentials:

```bash
touch .env
```

3. In the .env file, replace YOUR_OPENAI_API_KEY and YOUR_CALENDLY_API_KEY with your respective API keys and configure your email credentiatls:

 ```bash
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
CALENDLY_API_KEY=YOUR_CALENDLY_API_KEY
USERNAME=YOUR_EMAIL_USERNAME
PASSWORD=YOUR_EMAIL_PASSWORD
```

4. Start Docker and build the application container:

```bash
docker-compose up --build
```

## :rocket: Usage

1. Set Up Environment Variables: Ensure the .env file has the correct API keys for OpenAI and Calendly and correct credentials.

2. Run the Application: Once the Docker container is up, the app will start, and you can access it through http://localhost:8000 (or your specified port).

3. Sentiment Analysis: The application will process emails and return sentiment analysis using the OpenAI API.
 
4. Event Scheduling: Use the Calendly integration to manage events directly within the application.

5. API Key Replacement:
- OpenAI API Key: Replace YOUR_OPENAI_API_KEY in the .env file.
- Calendly API Key: Replace YOUR_CALENDLY_API_KEY in the .env file.
- Postgresql Database URL: Replace postgresql://username:password@localhost:5432/your-database with your username, password of the server and your database name.

Make sure to restart the Docker container after making any updates to the .env file to apply the new keys.
