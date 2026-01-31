from django.urls import path
from .views import (
    UploadCSVView, HistoryView, PDFReportView, ThresholdView, PredictMaintenanceView,
    EquipmentHistoryView, AlertSettingsView, AlertLogView, TestAlertView,
    MaintenanceScheduleView, MaintenanceDetailView, AutoScheduleMaintenanceView
)

urlpatterns = [
    # Existing endpoints
    path('upload/', UploadCSVView.as_view(), name='upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report_pdf/', PDFReportView.as_view(), name='report_pdf'),
    path('thresholds/', ThresholdView.as_view(), name='thresholds'),
    path('predict/', PredictMaintenanceView.as_view(), name='predict'),
    
    # New Feature: Historical Trend Analysis
    path('equipment-history/', EquipmentHistoryView.as_view(), name='equipment_history'),
    
    # New Feature: Email/SMS Alerts
    path('alerts/settings/', AlertSettingsView.as_view(), name='alert_settings'),
    path('alerts/logs/', AlertLogView.as_view(), name='alert_logs'),
    path('alerts/test/', TestAlertView.as_view(), name='test_alert'),
    
    # New Feature: Maintenance Scheduling
    path('maintenance/', MaintenanceScheduleView.as_view(), name='maintenance_list'),
    path('maintenance/<int:pk>/', MaintenanceDetailView.as_view(), name='maintenance_detail'),
    path('maintenance/auto-schedule/', AutoScheduleMaintenanceView.as_view(), name='auto_schedule_maintenance'),
]
