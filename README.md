# City Data Management System

This project is for managing and analyzing data from various IoT sensors across a smart city. It provides endpoints for retrieving sensor data, air quality information, traffic density, and analytics.

## Features

- RESTful API for sensor data management
- Real-time data processing for air quality and traffic density
- Caching for improved performance
- Rate limiting to prevent API abuse
- Advanced analytics endpoints
- Environment-based configuration for enhanced security

## Technologies Used

- Flask: Web framework
- SQLAlchemy: ORM (Object-Relational Mapping)
- PostgreSQL: Database
- Flask-Migrate: Database migrations
- Flask-Caching: Response caching
- Flask-Limiter: API rate limiting
- Docker: Containerization
- python-dotenv: Environment variable management

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smart-city-data-management.git
   cd smart-city-data-management
   ```

2. Create a `.env` file in the project root and add the following variables:
   ```
   DB_USER=smartcity_user
   DB_PASSWORD=super_secret_password
   DB_NAME=smartcity_db
   DB_HOST=db
   DB_PORT=5432
   FLASK_SECRET_KEY=this_is_a_very_secret_key_change_it_in_production
   FLASK_DEBUG=False
   RATE_LIMIT_DEFAULT=200 per day
   RATE_LIMIT_PER_HOUR=50 per hour
   CACHE_TYPE=simple
   CACHE_DEFAULT_TIMEOUT=300
   ```

3. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:5000`

## API Endpoints

- GET /api/sensors: Retrieve all sensors
- GET /api/sensors/<sensor_id>/readings: Retrieve readings for a specific sensor
- GET /api/air-quality: Get air quality index for a location
- GET /api/traffic: Get traffic density for a location
- GET /api/analytics/sensor-summary: Get summary statistics for sensors of a specific type

## Development

To set up the development environment:

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   flask db upgrade
   ```

4. Run the development server:
   ```
   flask run
   ```

## Testing

To run the tests:

```
python -m unittest discover tests