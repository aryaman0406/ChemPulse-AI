from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions
from .models import UploadHistory
from .serializers import UploadHistorySerializer
import pandas as pd
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io

class UploadCSVView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
        file_obj = request.FILES['file']
        try:
            df = pd.read_csv(file_obj)
            
            # Validation
            required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                 return Response({"error": f"Missing columns: {missing}"}, status=status.HTTP_400_BAD_REQUEST)

            # Analytics
            total_count = len(df)
            avg_flowrate = float(df['Flowrate'].mean())
            avg_pressure = float(df['Pressure'].mean())
            avg_temperature = float(df['Temperature'].mean())
            type_distribution = df['Type'].value_counts().to_dict()

            summary = {
                "total_count": total_count,
                "avg_flowrate": avg_flowrate,
                "avg_pressure": avg_pressure,
                "avg_temperature": avg_temperature,
                "type_distribution": type_distribution,
                "data": df.fillna('').to_dict(orient='records')
            }

            # Manage history (Keep last 5)
            existing_count = UploadHistory.objects.count()
            if existing_count >= 5:
                # Delete oldest
                oldest_ids = UploadHistory.objects.order_by('upload_date').values_list('id', flat=True)[:existing_count - 4]
                UploadHistory.objects.filter(id__in=oldest_ids).delete()

            # Save
            file_obj.seek(0)
            UploadHistory.objects.create(
                filename=file_obj.name,
                summary_data=summary,
                file=file_obj 
            )

            return Response(summary, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        history = UploadHistory.objects.order_by('-upload_date')
        serializer = UploadHistorySerializer(history, many=True)
        return Response(serializer.data)

class PDFReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        latest = UploadHistory.objects.order_by('-upload_date').last() # last() is actually most recent if ordered by date ascending default, but we want most recent.
        # Wait, order_by('-upload_date') means Descending. So .first() is the newest.
        latest = UploadHistory.objects.order_by('-upload_date').first()
        
        if not latest:
            return Response({"error": "No data available"}, status=status.HTTP_404_NOT_FOUND)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        
        p = canvas.Canvas(response)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, f"Report for {latest.filename}")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, 780, f"Date: {latest.upload_date.strftime('%Y-%m-%d %H:%M')}")
        
        summary = latest.summary_data
        y = 750
        p.drawString(100, y, f"Total Equipment: {summary.get('total_count')}")
        y -= 25
        p.drawString(100, y, f"Avg Flowrate: {summary.get('avg_flowrate'):.2f}")
        y -= 25
        p.drawString(100, y, f"Avg Pressure: {summary.get('avg_pressure'):.2f}")
        y -= 25
        p.drawString(100, y, f"Avg Temperature: {summary.get('avg_temperature'):.2f}")
        
        y -= 45
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, "Type Distribution:")
        p.setFont("Helvetica", 12)
        y -= 25
        for k, v in summary.get('type_distribution', {}).items():
            p.drawString(120, y, f"{k}: {v}")
            y -= 20
        
        p.showPage()
        p.save()
        return response
