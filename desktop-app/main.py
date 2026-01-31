import sys
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
                             QLineEdit, QFormLayout, QHeaderView, QFrame, QComboBox,
                             QDateEdit, QTimeEdit, QCheckBox)
from PyQt5.QtCore import Qt, QDate, QTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

API_URL = "http://127.0.0.1:8000/api/"

LIGHT_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background: white;
    border-radius: 12px;
}
QTabBar::tab {
    background: #f1f5f9;
    color: #64748b;
    padding: 12px 25px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: white;
    color: #6366f1;
    font-weight: bold;
    border-bottom: 2px solid #6366f1;
}
QLineEdit {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px;
    color: #1e293b;
}
QLineEdit:focus {
    border: 1px solid #6366f1;
}
QPushButton {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4f46e5;
}
QPushButton#SecondaryButton {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
}
QPushButton#SecondaryButton:hover {
    background-color: #e2e8f0;
}
QTableWidget {
    background-color: white;
    gridline-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
}
QLabel#Header {
    font-size: 26px;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 10px;
}
QLabel#StatsValue {
    font-size: 30px;
    font-weight: bold;
    color: #1e293b;
}
QLabel#StatsLabel {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    font-weight: bold;
}
QWidget#Card {
    background-color: white;
    border-radius: 15px;
    border: 1px solid #e2e8f0;
}
"""

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}
QTabWidget::pane {
    border: 1px solid #334155;
    background: #1e293b;
    border-radius: 12px;
}
QTabBar::tab {
    background: #0f172a;
    color: #94a3b8;
    padding: 12px 25px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}
QTabBar::tab:selected {
    background: #1e293b;
    color: #6366f1;
    font-weight: bold;
    border-bottom: 2px solid #6366f1;
}
QLineEdit {
    background-color: #334155;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 10px;
    color: white;
}
QLineEdit:focus {
    border: 1px solid #6366f1;
}
QPushButton {
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4f46e5;
}
QPushButton#SecondaryButton {
    background-color: #334155;
    color: #cbd5e1;
}
QPushButton#SecondaryButton:hover {
    background-color: #475569;
}
QTableWidget {
    background-color: #1e293b;
    gridline-color: #334155;
    border: none;
    border-radius: 12px;
}
QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px;
    border: none;
}
QLabel#Header {
    font-size: 26px;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 10px;
}
QLabel#StatsValue {
    font-size: 30px;
    font-weight: bold;
    color: #f8fafc;
}
QLabel#StatsLabel {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
}
QWidget#Card {
    background-color: #1e293b;
    border-radius: 12px;
    border: 1px solid #334155;
}
"""

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login - Chemical Visualizer")
        self.setGeometry(300, 300, 400, 250)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout container
        main_layout = QVBoxLayout()
        
        # Content Box
        content_box = QFrame()
        content_box.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        layout = QVBoxLayout(content_box)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Welcome Back")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setText("admin") 
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setText("password") 

        self.btn_login = QPushButton("Sign In")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.check_login)
        
        btn_close = QPushButton("Exit")
        btn_close.setObjectName("SecondaryButton")
        btn_close.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_login)
        layout.addWidget(btn_close)
        
        main_layout.addWidget(content_box)
        self.setLayout(main_layout)

    def check_login(self):
        auth = (self.username.text(), self.password.text())
        try:
            r = requests.get(API_URL + "history/", auth=auth)
            if r.status_code == 200:
                self.on_login_success(auth)
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials.")
        except:
             QMessageBox.critical(self, "Error", "Could not connect to backend.")

class MainWindow(QMainWindow):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        # Apply Default Theme (Light)
        self.is_dark_mode = False
        self.setStyleSheet(LIGHT_STYLESHEET)

        # Header for MainWindow (with Theme Toggle)
        self.header_container = QWidget()
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        app_title = QLabel("ChemPulse AI | Predictive Maintenance")
        app_title.setStyleSheet("font-weight: 800; font-size: 18px; color: #6366f1;")
        
        self.btn_theme = QPushButton("🌙 Switch Theme")
        self.btn_theme.setObjectName("SecondaryButton")
        self.btn_theme.setFixedWidth(150)
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_theme)
        
        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(0,0,0,0)
        self.root_layout.setSpacing(0)
        self.root_layout.addWidget(self.header_container)
        
        self.tabs = QTabWidget()
        self.root_layout.addWidget(self.tabs)
        
        central_widget = QWidget()
        central_widget.setLayout(self.root_layout)
        self.setCentralWidget(central_widget)
        
        self.tabs.setDocumentMode(True)

        self.upload_tab = QWidget()
        self.history_tab = QWidget()
        self.visualizer_tab = QWidget()
        self.predictions_tab = QWidget()
        self.trends_tab = QWidget()
        self.alerts_tab = QWidget()
        self.maintenance_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.upload_tab, "Dashboard & Upload")
        self.tabs.addTab(self.history_tab, "History & Reports")
        self.tabs.addTab(self.visualizer_tab, "Visualizer")
        self.tabs.addTab(self.predictions_tab, "ML Predictions")
        self.tabs.addTab(self.trends_tab, "Trends")
        self.tabs.addTab(self.alerts_tab, "Email Alerts")
        self.tabs.addTab(self.maintenance_tab, "Maintenance")
        self.tabs.addTab(self.settings_tab, "Thresholds")

        # Store current data and thresholds
        self.current_data = None
        self.thresholds = {
            'pressure_warning': 70,
            'pressure_critical': 80,
            'temperature_warning': 130,
            'temperature_critical': 150,
            'flowrate_min': 10,
            'flowrate_max': 200
        }

        self.setup_upload_tab()
        self.setup_history_tab()
        self.setup_visualizer_tab()
        self.setup_predictions_tab()
        self.setup_trends_tab()
        self.setup_alerts_tab()
        self.setup_maintenance_tab()
        self.setup_settings_tab()
        
        # Load thresholds from backend
        self.load_thresholds()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.setStyleSheet(DARK_STYLESHEET)
            self.btn_theme.setText("☀️ Light Mode")
            plt.style.use('dark_background')
        else:
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.btn_theme.setText("🌙 Dark Mode")
            plt.style.use('default')
        
        # Trigger redraw of charts if data exists
        if self.current_data:
            self.display_upload_results(self.current_data)
        self.load_trend_data()

    def setup_upload_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header Section
        header_box = QHBoxLayout()
        header_label = QLabel("Equipment Analytics Dashboard")
        header_label.setObjectName("Header")
        
        self.btn_select = QPushButton("Import CSV Dataset")
        self.btn_select.setCursor(Qt.PointingHandCursor)
        self.btn_select.setFixedWidth(200)
        self.btn_select.clicked.connect(self.upload_file)
        
        header_box.addWidget(header_label)
        header_box.addStretch()
        header_box.addWidget(self.btn_select)
        
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: #64748b; font-style: italic;")
        
        # Results Container
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_layout.setContentsMargins(0,0,0,0)
        self.results_widget.setLayout(self.results_layout)

        layout.addLayout(header_box)
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.results_widget)
        layout.addStretch()
        
        self.upload_tab.setLayout(layout)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            self.lbl_status.setText(f"Processing {fname}...")
            files = {'file': open(fname, 'rb')}
            try:
                r = requests.post(API_URL + "upload/", files=files, auth=self.auth)
                if r.status_code == 201:
                    data = r.json()
                    self.current_data = data
                    self.display_upload_results(data)
                    self.lbl_status.setText("✅ Analysis Complete")
                    
                    # Refresh all other tabs automatically
                    self.refresh_history()
                    self.fetch_predictions()
                    self.update_visualizer(data)
                    self.load_trend_data()
                    self.load_alert_logs()
                    self.load_maintenance()
                    
                    # Show notification for critical items
                    critical_count = len(data.get('critical_items', []))
                    if critical_count > 0:
                        QMessageBox.warning(self, "Critical Alert", 
                                          f"🚨 {critical_count} equipment require immediate attention!\nAlert notifications have been processed.")
                else:
                    self.lbl_status.setText(f"❌ Error: {r.text}")
            except Exception as e:
                self.lbl_status.setText(f"❌ Connection Error: {e}")

    def create_stat_card(self, title, value, color_hex):
        card = QWidget()
        card.setObjectName("Card")
        l = QVBoxLayout()
        
        t = QLabel(title)
        t.setObjectName("StatsLabel")
        
        v = QLabel(str(value))
        v.setObjectName("StatsValue")
        v.setStyleSheet(f"color: {color_hex}; font-size: 28px; font-weight: bold;")
        
        l.addWidget(t)
        l.addWidget(v)
        card.setLayout(l)
        return card

    def display_upload_results(self, data):
        # Clear previous
        for i in reversed(range(self.results_layout.count())): 
            w = self.results_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        stats_box = QHBoxLayout()
        stats_box.setSpacing(20)
        
        stats_box.addWidget(self.create_stat_card("TOTAL EQUIPMENT", data['total_count'], "#818cf8"))
        
        health = data.get('health_score', 100)
        c_health = "#10b981" if health > 70 else "#f43f5e"
        stats_box.addWidget(self.create_stat_card("HEALTH SCORE", f"{health}%", c_health))

        critical_count = len(data.get('critical_items', []))
        c_crit = "#f43f5e" if critical_count > 0 else "#94a3b8"
        stats_box.addWidget(self.create_stat_card("CRITICAL ALERTS", str(critical_count), c_crit))

        stats_box.addWidget(self.create_stat_card("AVG FLOWRATE", f"{data['avg_flowrate']:.2f}", "#34d399"))
        stats_box.addWidget(self.create_stat_card("AVG PRESSURE", f"{data['avg_pressure']:.2f}", "#fb7185"))
        stats_box.addWidget(self.create_stat_card("AVG TEMP", f"{data['avg_temperature']:.2f}", "#fbbf24"))
        
        stats_wrapper = QWidget()
        stats_wrapper.setLayout(stats_box)
        stats_wrapper.setFixedHeight(120)
        self.results_layout.addWidget(stats_wrapper)
        
        # Critical Items Warning
        if critical_count > 0:
            warning_widget = QWidget()
            warning_widget.setStyleSheet("""
                background-color: rgba(244, 63, 94, 0.1);
                border: 1px solid rgba(244, 63, 94, 0.2);
                border-radius: 12px;
                padding: 15px;
            """)
            warning_layout = QVBoxLayout()
            warning_label = QLabel(f"⚠️ Warning: {critical_count} equipment need attention")
            warning_label.setStyleSheet("color: #fca5a5; font-weight: bold; font-size: 16px;")
            warning_layout.addWidget(warning_label)
            
            # List critical items
            for idx, item in enumerate(data.get('critical_items', [])[:5]):
                item_label = QLabel(f"• {item.get('Equipment Name', 'Unknown')} - Pressure: {item.get('Pressure', 'N/A')} Bar")
                item_label.setStyleSheet("color: #fca5a5; margin-left: 20px;")
                warning_layout.addWidget(item_label)
            
            if critical_count > 5:
                more_label = QLabel(f"+{critical_count - 5} more critical items")
                more_label.setStyleSheet("color: #fca5a5; margin-left: 20px; font-style: italic;")
                warning_layout.addWidget(more_label)
            
            warning_widget.setLayout(warning_layout)
            self.results_layout.addWidget(warning_widget)
        
        # Charts Area
        chart_box = QHBoxLayout()
        chart_box.setSpacing(20)
        
        # Common Chart Style
        plt.style.use('dark_background')
        chart_bg = '#1e293b'
        
        # Donut Chart
        fig1 = Figure(figsize=(5, 4), dpi=100, facecolor=chart_bg)
        canvas1 = FigureCanvas(fig1)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(chart_bg)
        
        dist = data['type_distribution']
        colors = ['#6366f1', '#10b981', '#f43f5e', '#f59e0b']
        wedges, texts, autotexts = ax1.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', colors=colors, startangle=90)
        for t in texts: t.set_color('white')
        for t in autotexts: t.set_color('white')
        
        circle = plt.Circle((0,0), 0.70, fc=chart_bg)
        fig1.gca().add_artist(circle)
        ax1.set_title("Equipment Distribution", color='white', pad=20)
        fig1.tight_layout()
        
        # Bar Chart
        if 'data' in data:
            df_data = data['data']
            # Simple histogram of flowrates
            fig2 = Figure(figsize=(5, 4), dpi=100, facecolor=chart_bg)
            canvas2 = FigureCanvas(fig2)
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor(chart_bg)
            
            flowrates = [float(x['Flowrate']) for x in df_data]
            ax2.hist(flowrates, bins=10, color='#6366f1', alpha=0.7, rwidth=0.85)
            ax2.set_title("Flowrate Distribution", color='white', pad=20)
            ax2.grid(color='#334155', linestyle='--', linewidth=0.5)
            ax2.spines['bottom'].set_color('#475569')
            ax2.spines['left'].set_color('#475569')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.tick_params(colors='#94a3b8')
            fig2.tight_layout()
            
            chart_box.addWidget(canvas2)
        
        chart_box.addWidget(canvas1)
        
        chart_container = QWidget()
        chart_container.setLayout(chart_box)
        self.results_layout.addWidget(chart_container)

    def setup_history_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        header_box = QHBoxLayout()
        l = QLabel("Analysis History")
        l.setObjectName("Header")
        header_box.addWidget(l)
        header_box.addStretch()
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setObjectName("SecondaryButton")
        btn_refresh.clicked.connect(self.refresh_history)
        
        btn_pdf = QPushButton("Download Report")
        btn_pdf.clicked.connect(self.download_pdf)
        
        header_box.addWidget(btn_refresh)
        header_box.addWidget(btn_pdf)
        
        layout.addLayout(header_box)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["FILENAME", "DATE", "SUMMARY"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setShowGrid(False)
        self.history_table.setAlternatingRowColors(True) # Note: styling handles bg
        
        layout.addWidget(self.history_table)
        self.history_tab.setLayout(layout)

    def refresh_history(self):
        self.history_table.setRowCount(0)
        try:
            r = requests.get(API_URL + "history/", auth=self.auth)
            if r.status_code == 200:
                data = r.json()
                self.history_table.setRowCount(len(data))
                for i, row in enumerate(data):
                    self.history_table.setItem(i, 0, QTableWidgetItem(row['filename']))
                    self.history_table.setItem(i, 1, QTableWidgetItem(row['upload_date'][:16].replace('T', ' ')))
                    summary = f"{row['summary_data']['total_count']} Units | {row['summary_data']['avg_temperature']:.1f}°C Avg Temp"
                    self.history_table.setItem(i, 2, QTableWidgetItem(summary))
        except:
            pass

    def download_pdf(self):
        try:
            r = requests.get(API_URL + "report_pdf/", auth=self.auth)
            if r.status_code == 200:
                path, _ = QFileDialog.getSaveFileName(self, "Save Report", "report.pdf", "PDF Files (*.pdf)")
                if path:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    QMessageBox.information(self, "Success", "Report saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed: {e}")

    def setup_visualizer_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("Equipment Visualizer")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        desc = QLabel("Interactive view of equipment - larger circles indicate higher flowrate")
        desc.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Scrollable area for equipment circles
        scroll = QWidget()
        self.visualizer_layout = QVBoxLayout()
        scroll.setLayout(self.visualizer_layout)
        
        layout.addWidget(scroll)
        self.visualizer_tab.setLayout(layout)

    def update_visualizer(self, data):
        # Clear previous
        for i in reversed(range(self.visualizer_layout.count())): 
            w = self.visualizer_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        if not data or 'data' not in data:
            return
            
        units = data['data']
        grid = QHBoxLayout()
        grid.setSpacing(20)
        
        # We'll create a scroll area content
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        for unit in units:
            unit_box = QFrame()
            unit_box.setFixedSize(140, 160)
            unit_box.setStyleSheet("""
                QFrame {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 12px;
                }
            """)
            unit_layout = QVBoxLayout(unit_box)
            
            # Flowrate circle
            flow = float(unit.get('Flowrate', 0))
            size = min(60, max(20, int(flow / 4)))
            
            circle_container = QWidget()
            circle_container.setFixedSize(size, size)
            
            # Color based on pressure
            p = float(unit.get('Pressure', 0))
            color = "#10b981" # Healthy
            if p > self.thresholds['pressure_critical']: color = "#f43f5e" # Critical
            elif p > self.thresholds['pressure_warning']: color = "#f59e0b" # Warning
            
            circle_container.setStyleSheet(f"background-color: {color}; border-radius: {size//2}px;")
            
            unit_layout.addWidget(circle_container, 0, Qt.AlignCenter)
            
            name = QLabel(unit.get('Equipment Name', 'Unit'))
            name.setStyleSheet("font-weight: bold; font-size: 11px; color: white;")
            name.setAlignment(Qt.AlignCenter)
            unit_layout.addWidget(name)
            
            type_label = QLabel(unit.get('Type', 'N/A'))
            type_label.setStyleSheet("font-size: 9px; color: #94a3b8;")
            type_label.setAlignment(Qt.AlignCenter)
            unit_layout.addWidget(type_label)
            
            scroll_layout.addWidget(unit_box)
            
        scroll_area = QWidget()
        scroll_area.setLayout(scroll_layout)
        self.visualizer_layout.addWidget(scroll_area)
        self.visualizer_layout.addStretch()

    def setup_predictions_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        header_box = QHBoxLayout()
        header = QLabel("ML Predictions & Risk Assessment")
        header.setObjectName("Header")
        header_box.addWidget(header)
        header_box.addStretch()
        
        btn_refresh = QPushButton("Refresh Predictions")
        btn_refresh.clicked.connect(self.fetch_predictions)
        header_box.addWidget(btn_refresh)
        
        layout.addLayout(header_box)
        
        # Stats area
        self.predictions_stats = QWidget()
        self.predictions_stats_layout = QHBoxLayout()
        self.predictions_stats.setLayout(self.predictions_stats_layout)
        layout.addWidget(self.predictions_stats)
        
        # Table for predictions
        self.predictions_table = QTableWidget()
        self.predictions_table.setColumnCount(6)
        self.predictions_table.setHorizontalHeaderLabels([
            "Equipment", "Type", "Risk Score", "Status", "Maintenance (days)", "Risk Factors"
        ])
        self.predictions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.predictions_table.verticalHeader().setVisible(False)
        self.predictions_table.setShowGrid(False)
        
        layout.addWidget(self.predictions_table)
        self.predictions_tab.setLayout(layout)

    def setup_settings_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        header = QLabel("Threshold Settings")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        desc = QLabel("Configure threshold values for equipment monitoring and anomaly detection")
        desc.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Settings form
        form = QFormLayout()
        form.setSpacing(15)
        
        # Pressure thresholds
        pressure_label = QLabel("Pressure Thresholds (Bar)")
        pressure_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc; margin-top: 10px;")
        layout.addWidget(pressure_label)
        
        self.pressure_warning_input = QLineEdit(str(self.thresholds['pressure_warning']))
        self.pressure_critical_input = QLineEdit(str(self.thresholds['pressure_critical']))
        
        form.addRow("Warning Level:", self.pressure_warning_input)
        form.addRow("Critical Level:", self.pressure_critical_input)
        
        # Temperature thresholds
        temp_label = QLabel("Temperature Thresholds (°C)")
        temp_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc; margin-top: 20px;")
        layout.addWidget(temp_label)
        
        self.temp_warning_input = QLineEdit(str(self.thresholds['temperature_warning']))
        self.temp_critical_input = QLineEdit(str(self.thresholds['temperature_critical']))
        
        form.addRow("Warning Level:", self.temp_warning_input)
        form.addRow("Critical Level:", self.temp_critical_input)
        
        # Flowrate thresholds
        flow_label = QLabel("Flowrate Range (L/h)")
        flow_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc; margin-top: 20px;")
        layout.addWidget(flow_label)
        
        self.flow_min_input = QLineEdit(str(self.thresholds['flowrate_min']))
        self.flow_max_input = QLineEdit(str(self.thresholds['flowrate_max']))
        
        form.addRow("Minimum:", self.flow_min_input)
        form.addRow("Maximum:", self.flow_max_input)
        
        layout.addLayout(form)
        
        # Save button
        btn_save = QPushButton("Save Thresholds")
        btn_save.setFixedWidth(200)
        btn_save.clicked.connect(self.save_thresholds)
        layout.addWidget(btn_save)
        
        layout.addStretch()
        self.settings_tab.setLayout(layout)

    def load_thresholds(self):
        try:
            r = requests.get(API_URL + "thresholds/", auth=self.auth)
            if r.status_code == 200:
                self.thresholds = r.json()
        except:
            pass

    def save_thresholds(self):
        try:
            self.thresholds = {
                'pressure_warning': float(self.pressure_warning_input.text()),
                'pressure_critical': float(self.pressure_critical_input.text()),
                'temperature_warning': float(self.temp_warning_input.text()),
                'temperature_critical': float(self.temp_critical_input.text()),
                'flowrate_min': float(self.flow_min_input.text()),
                'flowrate_max': float(self.flow_max_input.text())
            }
            
            r = requests.put(API_URL + "thresholds/", json=self.thresholds, auth=self.auth)
            if r.status_code == 200:
                QMessageBox.information(self, "Success", "✅ Thresholds saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save thresholds")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save: {e}")

    def fetch_predictions(self):
        try:
            r = requests.get(API_URL + "predict/", auth=self.auth)
            if r.status_code == 200:
                predictions = r.json()
                self.display_predictions(predictions)
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch predictions")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Connection error: {e}")

    def display_predictions(self, predictions):
        # Clear stats
        for i in reversed(range(self.predictions_stats_layout.count())): 
            w = self.predictions_stats_layout.itemAt(i).widget()
            if w: w.setParent(None)
        
        summary = predictions.get('summary', {})
        
        self.predictions_stats_layout.addWidget(
            self.create_stat_card("CRITICAL RISK", str(summary.get('critical', 0)), "#f43f5e")
        )
        self.predictions_stats_layout.addWidget(
            self.create_stat_card("WARNING", str(summary.get('warning', 0)), "#fbbf24")
        )
        self.predictions_stats_layout.addWidget(
            self.create_stat_card("HEALTHY", str(summary.get('healthy', 0)), "#10b981")
        )
        self.predictions_stats_layout.addWidget(
            self.create_stat_card("NEXT MAINT.", summary.get('next_maintenance_date', 'N/A'), "#3b82f6")
        )
        
        # Fill table
        pred_list = predictions.get('predictions', [])
        self.predictions_table.setRowCount(len(pred_list))
        
        for i, pred in enumerate(pred_list):
            self.predictions_table.setItem(i, 0, QTableWidgetItem(pred.get('equipment_name', 'N/A')))
            self.predictions_table.setItem(i, 1, QTableWidgetItem(pred.get('type', 'N/A')))
            self.predictions_table.setItem(i, 2, QTableWidgetItem(f"{pred.get('risk_score', 0)}%"))
            
            status = pred.get('risk_level', 'unknown')
            status_item = QTableWidgetItem(status.capitalize())
            
            # Color code status
            if status == 'critical':
                status_item.setForeground(Qt.red)
            elif status == 'warning':
                status_item.setForeground(Qt.yellow)
            elif status == 'healthy':
                status_item.setForeground(Qt.green)
            
            self.predictions_table.setItem(i, 3, status_item)
            self.predictions_table.setItem(i, 4, QTableWidgetItem(str(pred.get('maintenance_in_days', 'N/A'))))
            
            risk_factors = pred.get('risk_factors', [])
            factors_str = ', '.join(risk_factors[:2]) if risk_factors else 'All normal'
            self.predictions_table.setItem(i, 5, QTableWidgetItem(factors_str))
        
        # Show notification for critical items
        critical_count = summary.get('critical', 0)
        if critical_count > 0:
            QMessageBox.warning(self, "Critical Alert", 
                              f"⚠️ {critical_count} equipment flagged as critical risk!")

    # ============= NEW FEATURE: TRENDS =============
    def setup_trends_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30,30,30,30)
        
        header = QLabel("Historical Trend Analysis")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        controls = QHBoxLayout()
        self.trend_equipment_combo = QComboBox()
        self.trend_equipment_combo.addItem("Select Equipment...")
        self.trend_equipment_combo.currentTextChanged.connect(self.load_trend_data)
        
        self.trend_days_combo = QComboBox()
        self.trend_days_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days"])
        self.trend_days_combo.currentTextChanged.connect(self.load_trend_data)
        
        btn_refresh = QPushButton("Refresh Trends")
        btn_refresh.setFixedWidth(150)
        btn_refresh.clicked.connect(self.load_trend_data)
        
        controls.addWidget(QLabel("Equipment:"))
        controls.addWidget(self.trend_equipment_combo)
        controls.addWidget(QLabel("Period:"))
        controls.addWidget(self.trend_days_combo)
        controls.addStretch()
        controls.addWidget(btn_refresh)
        
        layout.addLayout(controls)
        
        self.trend_figure = Figure(figsize=(10, 6), dpi=100)
        self.trend_canvas = FigureCanvas(self.trend_figure)
        self.trend_figure.patch.set_facecolor('#1e293b')
        layout.addWidget(self.trend_canvas)
        
        self.trends_tab.setLayout(layout)

    def load_trend_data(self):
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        days = days_map.get(self.trend_days_combo.currentText(), 30)
        equipment = self.trend_equipment_combo.currentText()
        if equipment == "Select Equipment...":
            equipment = ""
            
        try:
            params = {'days': days}
            if equipment: params['equipment'] = equipment
            
            r = requests.get(API_URL + "equipment-history/", auth=self.auth, params=params)
            if r.status_code == 200:
                data = r.json()
                
                # Update combo if needed
                current_names = [self.trend_equipment_combo.itemText(i) for i in range(self.trend_equipment_combo.count())]
                for name in data.get('equipment_list', []):
                    if name not in current_names:
                        self.trend_equipment_combo.addItem(name)
                
                self.plot_trends(data.get('history', []))
        except Exception as e:
            print(f"Trend error: {e}")

    def plot_trends(self, history):
        self.trend_figure.clear()
        if not history:
            return
            
        ax = self.trend_figure.add_subplot(111)
        ax.set_facecolor('#0f172a')
        
        if history:
            equipment = history[0]
            points = equipment.get('data_points', [])
            if points:
                points.sort(key=lambda x: x['timestamp'])
                
                times = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) for p in points]
                pressures = [p['pressure'] for p in points]
                temps = [p['temperature'] for p in points]
                
                ax.plot(times, pressures, label='Pressure (bar)', color='#fb7185', linewidth=2, marker='o')
                ax.plot(times, temps, label='Temp (°C)', color='#fbbf24', linewidth=2, marker='s')
                
                ax.set_title(f"Trends for {equipment['equipment_name']}", color='white', pad=20)
                ax.legend()
                ax.tick_params(axis='x', colors='white', rotation=45)
                ax.tick_params(axis='y', colors='white')
                ax.grid(True, color='#334155', alpha=0.3)
                
        self.trend_figure.tight_layout()
        self.trend_canvas.draw()

    # ============= NEW FEATURE: ALERTS =============
    def setup_alerts_tab(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(30,30,30,30)
        layout.setSpacing(30)
        
        # Left side: Settings
        settings_panel = QVBoxLayout()
        header = QLabel("Email Alert Settings")
        header.setObjectName("Header")
        settings_panel.addWidget(header)
        
        form = QFormLayout()
        self.chk_email_enabled = QCheckBox("Enable Notifications")
        self.edt_email_address = QLineEdit()
        self.chk_alert_critical = QCheckBox("Alert on Critical Risk")
        self.chk_alert_warning = QCheckBox("Alert on Warnings")
        self.chk_alert_maint = QCheckBox("Maintenance Reminders")
        
        form.addRow("", self.chk_email_enabled)
        form.addRow("Email Address:", self.edt_email_address)
        form.addRow("", self.chk_alert_critical)
        form.addRow("", self.chk_alert_warning)
        form.addRow("", self.chk_alert_maint)
        
        btn_save = QPushButton("Save Alert Settings")
        btn_save.clicked.connect(self.save_alert_settings)
        btn_test = QPushButton("Send Test Alert")
        btn_test.setObjectName("SecondaryButton")
        btn_test.clicked.connect(self.send_test_alert)
        
        settings_panel.addLayout(form)
        settings_panel.addSpacing(20)
        settings_panel.addWidget(btn_save)
        settings_panel.addWidget(btn_test)
        settings_panel.addStretch()
        
        # Right side: History/Logs
        logs_panel = QVBoxLayout()
        logs_header = QLabel("Alert History Logs")
        logs_header.setObjectName("Header")
        logs_panel.addWidget(logs_header)
        
        self.alert_logs_table = QTableWidget()
        self.alert_logs_table.setColumnCount(4)
        self.alert_logs_table.setHorizontalHeaderLabels(["Date", "Type", "Equipment", "Status"])
        self.alert_logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        logs_panel.addWidget(self.alert_logs_table)
        
        layout.addLayout(settings_panel, 1)
        layout.addLayout(logs_panel, 2)
        
        self.alerts_tab.setLayout(layout)
        self.load_alert_settings()
        self.load_alert_logs()

    def load_alert_settings(self):
        try:
            r = requests.get(API_URL + "alerts/settings/", auth=self.auth)
            if r.status_code == 200:
                data = r.json()
                self.chk_email_enabled.setChecked(data.get('email_enabled', False))
                self.edt_email_address.setText(data.get('email_address', ''))
                self.chk_alert_critical.setChecked(data.get('alert_on_critical', True))
                self.chk_alert_warning.setChecked(data.get('alert_on_warning', False))
                self.chk_alert_maint.setChecked(data.get('alert_on_maintenance_due', True))
        except: pass

    def save_alert_settings(self):
        data = {
            'email_enabled': self.chk_email_enabled.isChecked(),
            'email_address': self.edt_email_address.text(),
            'alert_on_critical': self.chk_alert_critical.isChecked(),
            'alert_on_warning': self.chk_alert_warning.isChecked(),
            'alert_on_maintenance_due': self.chk_alert_maint.isChecked()
        }
        try:
            r = requests.put(API_URL + "alerts/settings/", auth=self.auth, json=data)
            if r.status_code == 200:
                QMessageBox.information(self, "Success", "Alert settings saved successfully.")
        except: QMessageBox.critical(self, "Error", "Failed to save settings.")

    def send_test_alert(self):
        try:
            r = requests.post(API_URL + "alerts/test/", auth=self.auth)
            if r.status_code == 200:
                QMessageBox.information(self, "Success", "Test alert sent!")
            else:
                QMessageBox.warning(self, "Failed", r.json().get('message'))
        except: QMessageBox.critical(self, "Error", "Connection failed.")

    def load_alert_logs(self):
        try:
            r = requests.get(API_URL + "alerts/logs/", auth=self.auth)
            if r.status_code == 200:
                logs = r.json()
                self.alert_logs_table.setRowCount(len(logs))
                for i, log in enumerate(logs):
                    dt = datetime.fromisoformat(log['sent_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                    self.alert_logs_table.setItem(i, 0, QTableWidgetItem(dt))
                    self.alert_logs_table.setItem(i, 1, QTableWidgetItem(log['alert_type'].capitalize()))
                    self.alert_logs_table.setItem(i, 2, QTableWidgetItem(log['equipment_name']))
                    status = "Success" if log['was_successful'] else "Failed"
                    self.alert_logs_table.setItem(i, 3, QTableWidgetItem(status))
        except: pass

    # ============= NEW FEATURE: MAINTENANCE =============
    def setup_maintenance_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30,30,30,30)
        
        header_box = QHBoxLayout()
        header = QLabel("Maintenance Schedule 📅")
        header.setObjectName("Header")
        
        btn_auto = QPushButton("Auto-Schedule (ML)")
        btn_auto.setFixedWidth(200)
        btn_auto.clicked.connect(self.run_auto_schedule)
        
        btn_refresh = QPushButton("Refresh List")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setObjectName("SecondaryButton")
        btn_refresh.clicked.connect(self.load_maintenance)
        
        header_box.addWidget(header)
        header_box.addStretch()
        header_box.addWidget(btn_auto)
        header_box.addWidget(btn_refresh)
        
        layout.addLayout(header_box)
        
        self.maint_table = QTableWidget()
        self.maint_table.setColumnCount(6)
        self.maint_table.setHorizontalHeaderLabels(["Equipment", "Task Title", "Scheduled Date", "Priority", "Status", "Actions"])
        self.maint_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.maint_table)
        
        self.maintenance_tab.setLayout(layout)
        self.load_maintenance()

    def load_maintenance(self):
        try:
            r = requests.get(API_URL + "maintenance/", auth=self.auth)
            if r.status_code == 200:
                data = r.json()
                schedules = data.get('schedules', [])
                self.maint_table.setRowCount(len(schedules))
                for i, s in enumerate(schedules):
                    self.maint_table.setItem(i, 0, QTableWidgetItem(s['equipment_name']))
                    self.maint_table.setItem(i, 1, QTableWidgetItem(s['title']))
                    self.maint_table.setItem(i, 2, QTableWidgetItem(s['scheduled_date']))
                    self.maint_table.setItem(i, 3, QTableWidgetItem(s['priority'].upper()))
                    self.maint_table.setItem(i, 4, QTableWidgetItem(s['status'].capitalize()))
                    
                    btn_done = QPushButton("Mark Done")
                    btn_done.setMaximumWidth(100)
                    btn_done.clicked.connect(lambda checked, s_id=s['id']: self.mark_maint_completed(s_id))
                    if s['status'] == 'completed':
                        btn_done.setEnabled(False)
                        btn_done.setText("Completed")
                    self.maint_table.setCellWidget(i, 5, btn_done)
        except: pass

    def run_auto_schedule(self):
        try:
            r = requests.post(API_URL + "maintenance/auto-schedule/", auth=self.auth)
            if r.status_code == 201:
                QMessageBox.information(self, "Success", r.json().get('message'))
                self.load_maintenance()
        except: QMessageBox.critical(self, "Error", "Scheduling failed.")

    def mark_maint_completed(self, maint_id):
        try:
            r = requests.put(API_URL + f"maintenance/{maint_id}/", auth=self.auth, json={'status': 'completed'})
            if r.status_code == 200:
                self.load_maintenance()
        except: pass



if __name__ == '__main__':
    # High DPI settings must be set BEFORE QApplication is created
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)

    def start_main(auth):
        window = MainWindow(auth)
        window.show()
        app._main_window = window 

    login = LoginWindow(start_main)
    login.show()
    
    sys.exit(app.exec_())

