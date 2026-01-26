from django.urls import path
from .views import UploadCSVView, HistoryView, PDFReportView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report_pdf/', PDFReportView.as_view(), name='report_pdf'),
]
