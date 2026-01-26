# Chemical Equipment Parameter Visualizer

A full-stack hybrid application (Web & Desktop) for analyzing chemical equipment parameters.

## Features
- **Hybrid Architecture**: Shared Python Django backend serving both React Web App and PyQt5 Desktop App.
- **Data Analysis**: Upload CSV files to compute equipment counts, averages (Flowrate, Pressure, Temperature), and distributions.
- **Visualization**: Interactive Charts (Chart.js for Web, Matplotlib for Desktop).
- **History Tracking**: Keeps track of the last 5 uploads using SQLite.
- **PDF Reporting**: Generate downloadable PDF reports of analytics.
- **Authentication**: Basic Authentication implemented (Default: `admin` / `password`).

## Tech Stack
- **Backend**: Python, Django, Django REST Framework, Pandas, ReportLab.
- **Web Frontend**: React, Vite, Tailwind CSS, Chart.js.
- **Desktop Frontend**: Python, PyQt5, Matplotlib, Requests.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js & npm

### 1. Backend Setup
```bash
cd backend
# Install dependencies
pip install django djangorestframework pandas django-cors-headers reportlab

# Initialize Database and Create Admin
python manage.py makemigrations
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')"

# Run Server
python manage.py runserver
```

### 2. Web Frontend Setup
```bash
cd web-frontend
npm install
npm run dev
```
Access the web app at `http://localhost:5173`.
Login credentials (embedded): admin / password.

### 3. Desktop App Run
```bash
cd desktop-app
pip install PyQt5 matplotlib requests
python main.py
```

## Usage
1. **Web App**: 
   - Open the URL.
   - Click upload area to select `sample_equipment_data.csv` (located in project root).
   - Click "Analyze Data".
   - View charts and cards.
   - Download PDF Report.
   
2. **Desktop App**:
   - Launch app.
   - Login with `admin` / `password`.
   - Use "Upload & Analytics" tab to upload CSV.
   - Use "History & Reports" tab to view past data and download PDFs.

## Sample Data
A `sample_equipment_data.csv` file is provided in the root directory for testing.
