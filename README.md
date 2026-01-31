# ⌬ ChemPulse AI: Predictive Maintenance & Analytics Suite

**ChemPulse AI** is a state-of-the-art hybrid industrial monitoring system designed for real-time visualization, historical trend analysis, and predictive maintenance of chemical equipment. It bridges the gap between hardware parameters and actionable intelligence using a unified Django backend serving both a high-fidelity Web interface and a robust Desktop application.

![ChemPulse AI](https://images.unsplash.com/photo-1532187875605-2fe3587b1e08?auto=format&fit=crop&q=80&w=2070&ixlib=rb-4.0.3)

## 🚀 Key Features

### 💻 Hybrid Ecosystem
- **Web Analytics Suite**: Built with React & TypeScript, featuring a stunning Glassmorphism UI, real-time Chart.js visualizations, and Framer Motion animations.
- **Desktop Command Center**: A powerful PyQt5 application with integrated Matplotlib plotting for local monitoring and administrative control.

### 🧠 Predictive Maintenance (ML-Driven)
- **Intelligent Risk Scoring**: Analyzes Pressure, Temperature, and Flowrate against dynamic thresholds to calculate equipment health.
- **Auto-Scheduler**: ML models predict maintenance dates and can automatically populate the maintenance calendar.

### 📈 Historical Trend Analysis
- **Parameter Snapshots**: Every data upload is historically snapshotted to track degradation patterns.
- **Interactive Time-Series**: View 7, 30, and 90-day trends to identify anomalies before they become failures.

### 🔔 Smart Alerting System
- **Threshold-Based Notifications**: Automated email alerts for critical and warning-level readings.
- **Maintenance Reminders**: Built-in reminders for upcoming or overdue service tasks.
- **Alert Logs**: Complete historical tracking of all triggered notifications.

### 📅 Maintenance Management
- **Integrated Scheduler**: Full CRUD support for maintenance tasks with priority levels and statuses.
- **Status Dashboard**: At-a-glance stats for Overdue, Upcoming, and Completed tasks.

---

## 🛠 Tech Stack

- **Backend**: Python 3.x, Django 5.0+, Django REST Framework, SQLite
- **Web Frontend**: React 18, Vite, Tailwind CSS (for layout), Framer Motion, Chart.js, Lucide Icons
- **Desktop App**: PyQt5, Requests, Matplotlib
- **Analysis/Reporting**: Pandas, NumPy, ReportLab (PDF Generation)

---

## 📁 Project Structure

```text
ChemPulseAI/
├── backend/            # Django REST API & Database
│   ├── api/            # App logic: models, views, migrations
│   ├── uploads/        # Storage for processed CSV files
│   └── manage.py
├── web-frontend/       # React Analytics Suite
│   ├── src/            # Components & App logic
│   └── vite.config.ts
├── desktop-app/        # PyQt5 Command Center
│   └── main.py
└── sample_data.csv     # Test data for demo purposes
```

---

## 🚦 Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
*Note: Ensure to create a Superuser if you want access to the Django Admin.*

### 2. Web Frontend Setup
```bash
cd web-frontend
npm install
npm run dev
```

### 3. Desktop App Setup
```bash
cd desktop-app
pip install PyQt5 requests matplotlib
python main.py
```

---

## ⚙️ Configuration
The system uses configurable thresholds for all equipment types. These can be adjusted in real-time via the **Thresholds** tab in either the Web or Desktop interface, and changes are synchronized instantly across the ecosystem.

## � License
This project is developed for industrial equipment monitoring demonstrations. All rights reserved.

---

**Crafted with precision for the future of Chemical Industry 4.0**
