# SafeWay

SafeWay is a smart web-based safety and route analysis system designed to help users make more informed decisions before and during a journey. It combines interactive maps, reported incident data, route comparison, safety scoring, and personalized safety insights in one platform. Instead of only showing a route, SafeWay focuses on the safety context around a journey and presents useful information through a simple and interactive interface.

## Features

- Interactive Safety Map
  Explore different areas through an interactive OpenStreetMap-based interface.

- Route A/B Comparison
  Compare two routes or areas using their reported safety information.

- Safety Score
  Calculate an informational safety score based on reported incidents and their characteristics.

- Safety Recommendations
  Get recommendations based on the analyzed safety conditions of an area.

- Incident Reporting
  Report incidents with area, incident type, date, time, and description.

- Safety Dashboard
  View incident statistics, safety scores, activity trends, and recent reports.

- User Authentication
  Secure signup and login functionality using password hashing.

- Saved Locations
  Save frequently used locations for easier access.

- Trusted Contacts
  Store trusted contact information within the user's profile.

- Journey Check-in
  Start and finish a journey while maintaining a simple journey status and generating a temporary share code.

- SOS Workflow
  Includes a prototype SOS workflow for demonstrating how an emergency feature could be integrated in a future deployment.

- Responsive Interface
  Designed to work across desktop and smaller screens.

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Leaflet.js
- OpenStreetMap

### Backend

- Python
- Flask

### Database

- SQLite

### Security

- Werkzeug Password Hashing

## How It Works

1. The user opens SafeWay and selects an area or plans a journey.
2. The system analyzes available incident data for the selected areas.
3. Safety scores are calculated using a rule-based scoring system.
4. Route A and Route B can be compared using their safety information.
5. The system provides safety insights and recommendations.
6. Users can report incidents and view updated information through the dashboard.
7. Logged-in users can save locations, manage trusted contacts, and use the journey check-in workflow.

## Safety Score

SafeWay uses a rule-based scoring approach to generate an informational safety indicator.

The score considers factors such as:

- Number of reported incidents
- Type of reported incident
- Reports associated with nighttime
- Incident patterns for the selected area

The resulting score is used to categorize an area into different reported-risk levels.

Note: Safety scores are based on available reported/demo incident data and are intended only as informational indicators. They do not guarantee real-world safety.

## Interactive Map

SafeWay uses Leaflet.js with OpenStreetMap to provide an interactive map experience.

The map allows users to:

- Explore safety-related areas
- Select locations for analysis
- View route-planning information
- Use the browser's location feature to center the map

The map and safety indicators are designed as part of the project's prototype workflow.

## User Features

After creating an account, users can:

- Manage their profile
- Save frequently used locations
- Add trusted contacts
- Report incidents
- Check journey status
- Use route analysis features

## Dashboard

The dashboard provides a centralized view of safety-related information, including:

- Total incident reports
- Day/night activity
- Average safety score
- Incident categories
- Area-wise safety signals
- Recent reports

## Journey Check-in

The Journey Check-in feature provides a simple workflow for recording journey status:

Start Journey -> Active Journey -> Finish Journey

When a journey is started, SafeWay records the start time and generates a temporary share code.

This feature is currently a prototype workflow and does not automatically send messages or provide continuous real-time tracking.

## Future Improvements

SafeWay can be further extended with:

- Real-time route optimization using live traffic and route data
- Real-time location sharing with trusted contacts
- AI-based safety prediction using historical incident patterns
- Smart safety alerts based on route conditions
- Advanced time-based and location-based safety analytics
- Verified emergency alert integration with appropriate emergency services
- Cloud database integration for scalable data storage
- Dedicated Android/iOS mobile application
- Enhanced security and privacy controls
- Integration with reliable external safety and traffic data sources

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Rashikumari18/SafeWay.git
cd SafeWay
```


2. Create a virtual environment
py -m venv .venv
3. Activate the virtual environment

For Windows PowerShell:

.\.venv\Scripts\Activate.ps1
4. Install dependencies
pip install -r requirements.txt
5. Run the application
python app.py
6. Open in browser
http://127.0.0.1:5000
Project Structure
SafeWay/
│
├── app.py
├── requirements.txt
├── sample_incidents.csv
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── routes.html
│   ├── report.html
│   ├── dashboard.html
│   ├── profile.html
│   └── login.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js
Privacy and Safety Note

SafeWay is designed as a prototype safety analysis system. It does not guarantee real-world safety and should not be treated as a replacement for verified emergency services.

The current journey check-in and SOS workflows are demonstrations of how such features could work in a larger production system.

Users should always rely on trusted local information and appropriate emergency services when necessary.

Project By

Rashi Kumari

GitHub:
https://github.com/Rashikumari18/SafeWay




