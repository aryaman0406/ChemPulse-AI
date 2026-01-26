import sys
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
                             QLineEdit, QFormLayout, QHeaderView)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000/api/"

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Login - Chemical Visualizer")
        self.setGeometry(300, 300, 300, 150)
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
        
        layout = QFormLayout()
        
        self.username = QLineEdit()
        self.username.setText("admin") # Pre-fill for demo
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setText("password") 

        self.btn_login = QPushButton("Login")
        self.btn_login.setStyleSheet("background-color: #007bff; color: white; padding: 5px;")
        self.btn_login.clicked.connect(self.check_login)

        layout.addRow("Username:", self.username)
        layout.addRow("Password:", self.password)
        layout.addRow(self.btn_login)
        self.setLayout(layout)

    def check_login(self):
        auth = (self.username.text(), self.password.text())
        try:
            # Check connection
            r = requests.get(API_URL + "history/", auth=auth)
            if r.status_code == 200:
                self.on_login_success(auth)
                self.close()
            else:
                QMessageBox.warning(self, "Error", f"Invalid Credentials or Server Error: {r.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection Failed: {e}\nIs the backend running?")

class MainWindow(QMainWindow):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("font-family: Segoe UI; font-size: 12px;")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.upload_tab = QWidget()
        self.history_tab = QWidget()

        self.tabs.addTab(self.upload_tab, "Upload & Analytics")
        self.tabs.addTab(self.history_tab, "History & Reports")

        self.setup_upload_tab()
        self.setup_history_tab()

    def setup_upload_tab(self):
        layout = QVBoxLayout()
        
        header = QLabel("Upload Chemical Equipment Data (CSV)")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        
        self.btn_select = QPushButton("Select CSV File")
        self.btn_select.setStyleSheet("background-color: #28a745; color: white; padding: 8px; font-weight: bold;")
        self.btn_select.clicked.connect(self.upload_file)
        
        self.lbl_status = QLabel("Ready")
        
        # Container for results
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_widget.setLayout(self.results_layout)

        layout.addWidget(header)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.results_widget)
        layout.addStretch()
        
        self.upload_tab.setLayout(layout)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            self.lbl_status.setText(f"Uploading {fname}...")
            files = {'file': open(fname, 'rb')}
            try:
                r = requests.post(API_URL + "upload/", files=files, auth=self.auth)
                if r.status_code == 201:
                    data = r.json()
                    self.display_upload_results(data)
                    self.lbl_status.setText("Upload Successful")
                    self.refresh_history()
                else:
                    self.lbl_status.setText(f"Error: {r.text}")
            except Exception as e:
                self.lbl_status.setText(f"Connection Error: {e}")

    def display_upload_results(self, data):
        # Clear previous
        for i in reversed(range(self.results_layout.count())): 
            w = self.results_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        stats_box = QHBoxLayout()
        
        def create_card(title, value):
            card = QWidget()
            card.setStyleSheet("background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 10px;")
            l = QVBoxLayout()
            t = QLabel(title)
            t.setStyleSheet("font-weight: bold; color: #666;")
            v = QLabel(str(value))
            v.setStyleSheet("font-size: 20px; color: #333;")
            l.addWidget(t)
            l.addWidget(v)
            card.setLayout(l)
            return card

        stats_box.addWidget(create_card("Total Count", data['total_count']))
        stats_box.addWidget(create_card("Avg Flowrate", f"{data['avg_flowrate']:.2f}"))
        stats_box.addWidget(create_card("Avg Pressure", f"{data['avg_pressure']:.2f}"))
        stats_box.addWidget(create_card("Avg Temperature", f"{data['avg_temperature']:.2f}"))
        
        stats_widget = QWidget()
        stats_widget.setLayout(stats_box)
        self.results_layout.addWidget(stats_widget)
        
        # Charts
        chart_box = QHBoxLayout()
        
        # Bar Chart
        fig1 = Figure(figsize=(5, 4), dpi=100)
        canvas1 = FigureCanvas(fig1)
        ax1 = fig1.add_subplot(111)
        dist = data['type_distribution']
        ax1.bar(dist.keys(), dist.values(), color='skyblue')
        ax1.set_title("Equipment Type Distribution")
        ax1.tick_params(axis='x', rotation=45)
        fig1.tight_layout()
        
        chart_box.addWidget(canvas1)
        
        # Scatter/Hist Chart (e.g. Flowrate) if we have raw data
        # Assuming data['data'] contains records
        if 'data' in data:
            df_data = data['data']
            flowrates = [float(x['Flowrate']) for x in df_data]
            
            fig2 = Figure(figsize=(5, 4), dpi=100)
            canvas2 = FigureCanvas(fig2)
            ax2 = fig2.add_subplot(111)
            ax2.hist(flowrates, bins=10, color='orange', alpha=0.7)
            ax2.set_title("Flowrate Distribution")
            fig2.tight_layout()
            chart_box.addWidget(canvas2)

        chart_widget = QWidget()
        chart_widget.setLayout(chart_box)
        self.results_layout.addWidget(chart_widget)

    def setup_history_tab(self):
        layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Filename", "Date", "Summary"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        btn_box = QHBoxLayout()
        btn_hist = QPushButton("Refresh History")
        btn_hist.clicked.connect(self.refresh_history)
        btn_pdf = QPushButton("Download PDF Report (Latest)")
        btn_pdf.setStyleSheet("background-color: #dc3545; color: white;")
        btn_pdf.clicked.connect(self.download_pdf)
        
        btn_box.addWidget(btn_hist)
        btn_box.addWidget(btn_pdf)
        
        layout.addLayout(btn_box)
        layout.addWidget(self.history_table)
        self.history_tab.setLayout(layout)
        
    def refresh_history(self):
        try:
            r = requests.get(API_URL + "history/", auth=self.auth)
            if r.status_code == 200:
                data = r.json()
                self.history_table.setRowCount(len(data))
                for i, row in enumerate(data):
                    self.history_table.setItem(i, 0, QTableWidgetItem(row['filename']))
                    self.history_table.setItem(i, 1, QTableWidgetItem(row['upload_date'][:16]))
                    summary_str = f"Count: {row['summary_data']['total_count']}"
                    self.history_table.setItem(i, 2, QTableWidgetItem(summary_str))
        except:
            pass

    def download_pdf(self):
        try:
            r = requests.get(API_URL + "report_pdf/", auth=self.auth)
            if r.status_code == 200:
                with open("report_downloaded.pdf", "wb") as f:
                    f.write(r.content)
                QMessageBox.information(self, "Success", "PDF Downloaded to report_downloaded.pdf")
            else:
                 QMessageBox.warning(self, "Error", "Could not fetch PDF (No data?)")
        except Exception as e:
             QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Enable High DPI display
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    def start_main(auth):
        window = MainWindow(auth)
        window.show()
        app._main_window = window 

    login = LoginWindow(start_main)
    login.show()
    
    sys.exit(app.exec_())
