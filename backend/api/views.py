from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import UploadHistory, ThresholdSettings, EquipmentHistory, AlertSettings, AlertLog, MaintenanceSchedule
from .serializers import UploadHistorySerializer
import pandas as pd
import numpy as np
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings as django_settings
from reportlab.pdfgen import canvas
import io
import random
from datetime import datetime, timedelta, date


def get_thresholds():
    """Get or create default threshold settings"""
    thresholds, _ = ThresholdSettings.objects.get_or_create(name="default")
    return thresholds


def calculate_risk_score(pressure, temperature, flowrate, thresholds):
    """
    ML-inspired risk scoring algorithm
    Combines multiple factors to predict equipment failure risk
    """
    risk = 0
    factors = []
    
    # Pressure risk calculation
    if pressure > thresholds.pressure_critical:
        pressure_risk = min(40, (pressure - thresholds.pressure_critical) * 2)
        risk += pressure_risk
        factors.append(f"High pressure ({pressure} bar)")
    elif pressure > thresholds.pressure_warning:
        pressure_risk = (pressure - thresholds.pressure_warning) / (thresholds.pressure_critical - thresholds.pressure_warning) * 20
        risk += pressure_risk
        factors.append(f"Elevated pressure ({pressure} bar)")
    
    # Temperature risk calculation
    if temperature > thresholds.temperature_critical:
        temp_risk = min(40, (temperature - thresholds.temperature_critical) * 1.5)
        risk += temp_risk
        factors.append(f"High temperature ({temperature}°C)")
    elif temperature > thresholds.temperature_warning:
        temp_risk = (temperature - thresholds.temperature_warning) / (thresholds.temperature_critical - thresholds.temperature_warning) * 20
        risk += temp_risk
        factors.append(f"Elevated temperature ({temperature}°C)")
    
    # Flowrate anomaly detection
    if flowrate < thresholds.flowrate_min:
        flow_risk = min(20, (thresholds.flowrate_min - flowrate) * 0.5)
        risk += flow_risk
        factors.append(f"Low flowrate ({flowrate} L/h)")
    elif flowrate > thresholds.flowrate_max:
        flow_risk = min(20, (flowrate - thresholds.flowrate_max) * 0.3)
        risk += flow_risk
        factors.append(f"High flowrate ({flowrate} L/h)")
    
    # Cap risk at 100
    risk = min(100, max(0, risk))
    
    # Determine risk level
    if risk >= 70:
        level = "critical"
        maintenance_days = max(1, int(7 - (risk - 70) / 10))
    elif risk >= 40:
        level = "warning"
        maintenance_days = max(7, int(30 - (risk - 40) / 2))
    elif risk >= 20:
        level = "moderate"
        maintenance_days = max(30, int(60 - risk))
    else:
        level = "healthy"
        maintenance_days = max(60, int(90 - risk))
    
    return {
        "score": round(risk, 1),
        "level": level,
        "maintenance_days": maintenance_days,
        "factors": factors
    }


def predict_equipment_health(df, thresholds):
    """
    Predict maintenance needs for all equipment
    Returns predictions with risk scores and maintenance timeline
    """
    predictions = []
    
    for _, row in df.iterrows():
        pressure = float(row.get('Pressure', 0))
        temperature = float(row.get('Temperature', 0))
        flowrate = float(row.get('Flowrate', 0))
        
        risk_data = calculate_risk_score(pressure, temperature, flowrate, thresholds)
        
        predictions.append({
            "equipment_name": row.get('Equipment Name', 'Unknown'),
            "type": row.get('Type', 'Unknown'),
            "pressure": pressure,
            "temperature": temperature,
            "flowrate": flowrate,
            "risk_score": risk_data["score"],
            "risk_level": risk_data["level"],
            "maintenance_in_days": risk_data["maintenance_days"],
            "maintenance_date": (datetime.now() + timedelta(days=risk_data["maintenance_days"])).strftime("%Y-%m-%d"),
            "risk_factors": risk_data["factors"]
        })
    
    # Sort by risk score descending
    predictions.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return predictions


class UploadCSVView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

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

            # Get configurable thresholds
            thresholds = get_thresholds()

            # Analytics
            total_count = len(df)
            avg_flowrate = float(df['Flowrate'].mean())
            avg_pressure = float(df['Pressure'].mean())
            avg_temperature = float(df['Temperature'].mean())
            type_distribution = df['Type'].value_counts().to_dict()

            # Advanced Analysis using configurable thresholds
            critical_items = df[
                (df['Pressure'] > thresholds.pressure_critical) | 
                (df['Temperature'] > thresholds.temperature_critical)
            ].fillna('').to_dict(orient='records')
            
            warning_items = df[
                ((df['Pressure'] > thresholds.pressure_warning) & (df['Pressure'] <= thresholds.pressure_critical)) |
                ((df['Temperature'] > thresholds.temperature_warning) & (df['Temperature'] <= thresholds.temperature_critical))
            ].fillna('').to_dict(orient='records')

            # Calculate health score
            health_score = max(0, 100 - (len(critical_items) * 10) - (len(warning_items) * 3))

            # Generate ML predictions
            predictions = predict_equipment_health(df, thresholds)
            
            # Calculate prediction summary
            critical_count = len([p for p in predictions if p["risk_level"] == "critical"])
            warning_count = len([p for p in predictions if p["risk_level"] == "warning"])
            avg_maintenance_days = sum(p["maintenance_in_days"] for p in predictions) / len(predictions) if predictions else 0

            summary = {
                "total_count": total_count,
                "avg_flowrate": avg_flowrate,
                "avg_pressure": avg_pressure,
                "avg_temperature": avg_temperature,
                "type_distribution": type_distribution,
                "critical_items": critical_items,
                "warning_items": warning_items,
                "health_score": health_score,
                "data": df.fillna('').to_dict(orient='records'),
                # New ML prediction data
                "predictions": predictions,
                "prediction_summary": {
                    "critical_count": critical_count,
                    "warning_count": warning_count,
                    "avg_maintenance_days": round(avg_maintenance_days, 1),
                    "next_maintenance": predictions[0]["maintenance_date"] if predictions else None,
                    "highest_risk": predictions[0] if predictions else None
                },
                # Store thresholds used for reference
                "thresholds_used": {
                    "pressure_critical": thresholds.pressure_critical,
                    "pressure_warning": thresholds.pressure_warning,
                    "temperature_critical": thresholds.temperature_critical,
                    "temperature_warning": thresholds.temperature_warning,
                    "flowrate_min": thresholds.flowrate_min,
                    "flowrate_max": thresholds.flowrate_max,
                }
            }

            # Manage history (Keep last 5)
            existing_count = UploadHistory.objects.count()
            if existing_count >= 5:
                oldest_ids = UploadHistory.objects.order_by('upload_date').values_list('id', flat=True)[:existing_count - 4]
                UploadHistory.objects.filter(id__in=oldest_ids).delete()

            # Save upload history
            file_obj.seek(0)
            upload_record = UploadHistory.objects.create(
                filename=file_obj.name,
                summary_data=summary,
                file=file_obj 
            )
            
            # NEW: Save individual equipment records for historical trend analysis
            for _, row in df.iterrows():
                EquipmentHistory.objects.create(
                    equipment_name=row.get('Equipment Name', 'Unknown'),
                    equipment_type=row.get('Type', 'Unknown'),
                    pressure=float(row.get('Pressure', 0)),
                    temperature=float(row.get('Temperature', 0)),
                    flowrate=float(row.get('Flowrate', 0)),
                    upload_session=upload_record
                )
            
            # NEW: Send email alerts for critical equipment
            try:
                alert_settings = get_alert_settings()
                if alert_settings.email_enabled and alert_settings.email_address:
                    # Alert for critical items
                    if alert_settings.alert_on_critical and len(critical_items) > 0:
                        critical_names = [item.get('Equipment Name', 'Unknown') for item in critical_items[:5]]
                        message = f"🚨 CRITICAL ALERT: {len(critical_items)} equipment require immediate attention!\n\n"
                        message += f"Equipment: {', '.join(critical_names)}\n\n"
                        message += f"Upload: {file_obj.name}\nHealth Score: {health_score}%"
                        
                        send_alert_email(
                            alert_type='critical',
                            equipment_name=f"{len(critical_items)} equipment",
                            message=message,
                            email_address=alert_settings.email_address
                        )
                    
                    # Alert for warning items
                    if alert_settings.alert_on_warning and len(warning_items) > 0:
                        warning_names = [item.get('Equipment Name', 'Unknown') for item in warning_items[:5]]
                        message = f"⚠️ WARNING: {len(warning_items)} equipment have elevated readings.\n\n"
                        message += f"Equipment: {', '.join(warning_names)}\n\n"
                        message += f"Upload: {file_obj.name}"
                        
                        send_alert_email(
                            alert_type='warning',
                            equipment_name=f"{len(warning_items)} equipment",
                            message=message,
                            email_address=alert_settings.email_address
                        )
            except Exception as e:
                print(f"Alert error: {e}")
                pass  # Don't fail upload if email fails

            return Response(summary, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HistoryView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        history = UploadHistory.objects.order_by('-upload_date')
        serializer = UploadHistorySerializer(history, many=True)
        return Response(serializer.data)


class ThresholdView(APIView):
    """API endpoint for managing threshold settings"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get current threshold settings"""
        thresholds = get_thresholds()
        return Response({
            "pressure_warning": thresholds.pressure_warning,
            "pressure_critical": thresholds.pressure_critical,
            "temperature_warning": thresholds.temperature_warning,
            "temperature_critical": thresholds.temperature_critical,
            "flowrate_min": thresholds.flowrate_min,
            "flowrate_max": thresholds.flowrate_max,
            "updated_at": thresholds.updated_at.isoformat() if thresholds.updated_at else None
        })
    
    def put(self, request):
        """Update threshold settings"""
        thresholds = get_thresholds()
        data = request.data
        
        # Update fields if provided
        if 'pressure_warning' in data:
            thresholds.pressure_warning = float(data['pressure_warning'])
        if 'pressure_critical' in data:
            thresholds.pressure_critical = float(data['pressure_critical'])
        if 'temperature_warning' in data:
            thresholds.temperature_warning = float(data['temperature_warning'])
        if 'temperature_critical' in data:
            thresholds.temperature_critical = float(data['temperature_critical'])
        if 'flowrate_min' in data:
            thresholds.flowrate_min = float(data['flowrate_min'])
        if 'flowrate_max' in data:
            thresholds.flowrate_max = float(data['flowrate_max'])
        
        thresholds.save()
        
        return Response({
            "message": "Thresholds updated successfully",
            "pressure_warning": thresholds.pressure_warning,
            "pressure_critical": thresholds.pressure_critical,
            "temperature_warning": thresholds.temperature_warning,
            "temperature_critical": thresholds.temperature_critical,
            "flowrate_min": thresholds.flowrate_min,
            "flowrate_max": thresholds.flowrate_max,
        })


class PredictMaintenanceView(APIView):
    """Re-run predictions on existing data with current thresholds"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get predictions for the latest uploaded data"""
        latest = UploadHistory.objects.order_by('-upload_date').first()
        
        if not latest:
            return Response({"error": "No data available"}, status=status.HTTP_404_NOT_FOUND)
        
        thresholds = get_thresholds()
        data = latest.summary_data.get('data', [])
        
        if not data:
            return Response({"error": "No equipment data found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(data)
        predictions = predict_equipment_health(df, thresholds)
        
        # Calculate summary stats
        critical_count = len([p for p in predictions if p["risk_level"] == "critical"])
        warning_count = len([p for p in predictions if p["risk_level"] == "warning"])
        healthy_count = len([p for p in predictions if p["risk_level"] == "healthy"])
        
        return Response({
            "predictions": predictions,
            "summary": {
                "total": len(predictions),
                "critical": critical_count,
                "warning": warning_count,
                "healthy": healthy_count,
                "highest_risk_equipment": predictions[0]["equipment_name"] if predictions else None,
                "next_maintenance_date": predictions[0]["maintenance_date"] if predictions else None
            },
            "generated_at": datetime.now().isoformat()
        })


class PDFReportView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
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
        p.drawString(100, y, f"Health Score: {summary.get('health_score', 100)}%")
        y -= 25
        p.drawString(100, y, f"Avg Flowrate: {summary.get('avg_flowrate'):.2f}")
        y -= 25
        p.drawString(100, y, f"Avg Pressure: {summary.get('avg_pressure'):.2f}")
        y -= 25
        p.drawString(100, y, f"Avg Temperature: {summary.get('avg_temperature'):.2f}")
        
        # Add prediction summary
        pred_summary = summary.get('prediction_summary', {})
        if pred_summary:
            y -= 45
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y, "Predictive Maintenance:")
            p.setFont("Helvetica", 12)
            y -= 25
            p.drawString(120, y, f"Critical Alerts: {pred_summary.get('critical_count', 0)}")
            y -= 20
            p.drawString(120, y, f"Warnings: {pred_summary.get('warning_count', 0)}")
            y -= 20
            p.drawString(120, y, f"Next Maintenance: {pred_summary.get('next_maintenance', 'N/A')}")
        
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


# ============================================================================
# FEATURE 1: Historical Trend Analysis
# ============================================================================

def get_alert_settings():
    """Get or create default alert settings"""
    settings, _ = AlertSettings.objects.get_or_create(pk=1)
    return settings


def send_alert_email(alert_type, equipment_name, message, email_address):
    """Send alert email and log it"""
    try:
        subject_map = {
            'critical': '🚨 CRITICAL: Equipment Alert',
            'warning': '⚠️ WARNING: Equipment Alert',
            'maintenance': '🔧 Maintenance Reminder'
        }
        
        subject = f"{subject_map.get(alert_type, 'Alert')} - {equipment_name}"
        
        # Try to send email (will fail gracefully if not configured)
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=django_settings.DEFAULT_FROM_EMAIL if hasattr(django_settings, 'DEFAULT_FROM_EMAIL') else 'noreply@chemviz.local',
                recipient_list=[email_address],
                fail_silently=False
            )
            was_successful = True
        except Exception as e:
            print(f"ERROR: Email send failed: {e}")
            was_successful = False
        
        # Log the alert
        AlertLog.objects.create(
            alert_type=alert_type,
            equipment_name=equipment_name,
            message=message,
            sent_to=email_address,
            was_successful=was_successful
        )
        
        return was_successful
    except Exception:
        return False


class EquipmentHistoryView(APIView):
    """API endpoint for historical equipment data trends"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get historical trend data for equipment"""
        equipment_name = request.query_params.get('equipment', None)
        days = int(request.query_params.get('days', 30))
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        queryset = EquipmentHistory.objects.order_by('-recorded_at')
        
        if equipment_name:
            queryset = queryset.filter(equipment_name=equipment_name)
        
        # Limit to 100 points per device for performance
        queryset = queryset[:100]
        
        # Group by equipment and time
        history_data = {}
        for record in queryset:
            name = record.equipment_name
            if name not in history_data:
                history_data[name] = {
                    'equipment_name': name,
                    'equipment_type': record.equipment_type,
                    'data_points': []
                }
            
            history_data[name]['data_points'].append({
                'timestamp': record.recorded_at.isoformat(),
                'pressure': record.pressure,
                'temperature': record.temperature,
                'flowrate': record.flowrate
            })
        
        # Get list of all equipment names for dropdown
        all_equipment = EquipmentHistory.objects.values_list('equipment_name', flat=True).distinct()
        
        # Calculate trend summary
        trends = []
        for name, data in history_data.items():
            points = data['data_points']
            if len(points) >= 2:
                first_point = points[-1]  # Oldest
                last_point = points[0]    # Newest
                
                pressure_trend = 'stable'
                if last_point['pressure'] > first_point['pressure'] * 1.05:
                    pressure_trend = 'increasing'
                elif last_point['pressure'] < first_point['pressure'] * 0.95:
                    pressure_trend = 'decreasing'
                
                temp_trend = 'stable'
                if last_point['temperature'] > first_point['temperature'] * 1.05:
                    temp_trend = 'increasing'
                elif last_point['temperature'] < first_point['temperature'] * 0.95:
                    temp_trend = 'decreasing'
                
                trends.append({
                    'equipment_name': name,
                    'pressure_trend': pressure_trend,
                    'temperature_trend': temp_trend,
                    'data_points_count': len(points)
                })
        
        return Response({
            'equipment_list': list(all_equipment),
            'history': list(history_data.values()),
            'trends': trends,
            'period_days': days
        })


class AlertSettingsView(APIView):
    """API endpoint for managing email alert settings"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get current alert settings"""
        settings = get_alert_settings()
        return Response({
            'email_enabled': settings.email_enabled,
            'email_address': settings.email_address,
            'alert_on_critical': settings.alert_on_critical,
            'alert_on_warning': settings.alert_on_warning,
            'alert_on_maintenance_due': settings.alert_on_maintenance_due,
            'alert_frequency': settings.alert_frequency,
            'maintenance_reminder_days': settings.maintenance_reminder_days,
            'last_alert_sent': settings.last_alert_sent.isoformat() if settings.last_alert_sent else None,
            'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
        })
    
    def put(self, request):
        """Update alert settings"""
        settings = get_alert_settings()
        data = request.data
        
        if 'email_enabled' in data:
            settings.email_enabled = data['email_enabled']
        if 'email_address' in data:
            settings.email_address = data['email_address']
        if 'alert_on_critical' in data:
            settings.alert_on_critical = data['alert_on_critical']
        if 'alert_on_warning' in data:
            settings.alert_on_warning = data['alert_on_warning']
        if 'alert_on_maintenance_due' in data:
            settings.alert_on_maintenance_due = data['alert_on_maintenance_due']
        if 'alert_frequency' in data:
            settings.alert_frequency = data['alert_frequency']
        if 'maintenance_reminder_days' in data:
            settings.maintenance_reminder_days = int(data['maintenance_reminder_days'])
        
        settings.save()
        
        return Response({
            'message': 'Alert settings updated successfully',
            'email_enabled': settings.email_enabled,
            'email_address': settings.email_address
        })


class AlertLogView(APIView):
    """API endpoint for viewing alert history"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get recent alert logs"""
        limit = int(request.query_params.get('limit', 50))
        logs = AlertLog.objects.all()[:limit]
        
        return Response([{
            'id': log.id,
            'alert_type': log.alert_type,
            'equipment_name': log.equipment_name,
            'message': log.message,
            'sent_to': log.sent_to,
            'sent_at': log.sent_at.isoformat(),
            'was_successful': log.was_successful
        } for log in logs])


class TestAlertView(APIView):
    """Test email alert functionality"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Send a test alert email"""
        settings = get_alert_settings()
        
        if not settings.email_enabled or not settings.email_address:
            return Response({
                'success': False,
                'message': 'Email alerts not configured. Please enable and set an email address first.'
            }, status=400)
        
        success = send_alert_email(
            alert_type='critical',
            equipment_name='Test Equipment',
            message='This is a test alert from Chemical Equipment Visualizer. If you received this, your alert system is working correctly!',
            email_address=settings.email_address
        )
        
        return Response({
            'success': success,
            'message': 'Test alert sent successfully!' if success else 'Failed to send test alert. Check email configuration.'
        })


# ============================================================================
# FEATURE 3: Maintenance Scheduling
# ============================================================================

class MaintenanceScheduleView(APIView):
    """API endpoint for maintenance scheduling"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all maintenance schedules"""
        status_filter = request.query_params.get('status', None)
        equipment_filter = request.query_params.get('equipment', None)
        upcoming_days = request.query_params.get('upcoming_days', None)
        
        queryset = MaintenanceSchedule.objects.all()
        
        # Update overdue statuses
        today = date.today()
        MaintenanceSchedule.objects.filter(
            scheduled_date__lt=today,
            status='scheduled'
        ).update(status='overdue')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if equipment_filter:
            queryset = queryset.filter(equipment_name__icontains=equipment_filter)
        if upcoming_days:
            end_date = today + timedelta(days=int(upcoming_days))
            queryset = queryset.filter(scheduled_date__lte=end_date, scheduled_date__gte=today)
        
        schedules = [{
            'id': m.id,
            'equipment_name': m.equipment_name,
            'equipment_type': m.equipment_type,
            'title': m.title,
            'description': m.description,
            'scheduled_date': m.scheduled_date.isoformat(),
            'scheduled_time': m.scheduled_time.strftime('%H:%M') if m.scheduled_time else None,
            'priority': m.priority,
            'status': m.status,
            'assigned_to': m.assigned_to,
            'estimated_duration': m.estimated_duration,
            'notes': m.notes,
            'created_at': m.created_at.isoformat()
        } for m in queryset]
        
        # Summary stats
        all_schedules = MaintenanceSchedule.objects.all()
        summary = {
            'total': all_schedules.count(),
            'scheduled': all_schedules.filter(status='scheduled').count(),
            'in_progress': all_schedules.filter(status='in_progress').count(),
            'completed': all_schedules.filter(status='completed').count(),
            'overdue': all_schedules.filter(status='overdue').count(),
            'upcoming_7_days': all_schedules.filter(
                scheduled_date__gte=today,
                scheduled_date__lte=today + timedelta(days=7),
                status__in=['scheduled', 'in_progress']
            ).count()
        }
        
        return Response({
            'schedules': schedules,
            'summary': summary
        })
    
    def post(self, request):
        """Create a new maintenance schedule"""
        data = request.data
        
        try:
            schedule = MaintenanceSchedule.objects.create(
                equipment_name=data.get('equipment_name'),
                equipment_type=data.get('equipment_type', ''),
                title=data.get('title'),
                description=data.get('description', ''),
                scheduled_date=data.get('scheduled_date'),
                scheduled_time=data.get('scheduled_time') if data.get('scheduled_time') else None,
                priority=data.get('priority', 'medium'),
                status=data.get('status', 'scheduled'),
                assigned_to=data.get('assigned_to', ''),
                estimated_duration=int(data.get('estimated_duration', 60)),
                notes=data.get('notes', '')
            )
            
            # Send alert if enabled
            alert_settings = get_alert_settings()
            if alert_settings.email_enabled and alert_settings.alert_on_maintenance_due and alert_settings.email_address:
                send_alert_email(
                    alert_type='maintenance',
                    equipment_name=schedule.equipment_name,
                    message=f"New maintenance scheduled: {schedule.title}\n\nEquipment: {schedule.equipment_name}\nDate: {schedule.scheduled_date}\nPriority: {schedule.priority}\n\nDescription: {schedule.description}",
                    email_address=alert_settings.email_address
                )
            
            return Response({
                'id': schedule.id,
                'message': 'Maintenance scheduled successfully',
                'schedule': {
                    'id': schedule.id,
                    'equipment_name': schedule.equipment_name,
                    'title': schedule.title,
                    'scheduled_date': schedule.scheduled_date.isoformat(),
                    'priority': schedule.priority,
                    'status': schedule.status
                }
            }, status=201)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class MaintenanceDetailView(APIView):
    """API endpoint for individual maintenance schedule operations"""
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        """Get a specific maintenance schedule"""
        try:
            schedule = MaintenanceSchedule.objects.get(pk=pk)
            return Response({
                'id': schedule.id,
                'equipment_name': schedule.equipment_name,
                'equipment_type': schedule.equipment_type,
                'title': schedule.title,
                'description': schedule.description,
                'scheduled_date': schedule.scheduled_date.isoformat(),
                'scheduled_time': schedule.scheduled_time.strftime('%H:%M') if schedule.scheduled_time else None,
                'priority': schedule.priority,
                'status': schedule.status,
                'assigned_to': schedule.assigned_to,
                'estimated_duration': schedule.estimated_duration,
                'notes': schedule.notes,
                'completed_at': schedule.completed_at.isoformat() if schedule.completed_at else None,
                'created_at': schedule.created_at.isoformat()
            })
        except MaintenanceSchedule.DoesNotExist:
            return Response({'error': 'Schedule not found'}, status=404)
    
    def put(self, request, pk):
        """Update a maintenance schedule"""
        try:
            schedule = MaintenanceSchedule.objects.get(pk=pk)
            data = request.data
            
            if 'equipment_name' in data:
                schedule.equipment_name = data['equipment_name']
            if 'equipment_type' in data:
                schedule.equipment_type = data['equipment_type']
            if 'title' in data:
                schedule.title = data['title']
            if 'description' in data:
                schedule.description = data['description']
            if 'scheduled_date' in data:
                schedule.scheduled_date = data['scheduled_date']
            if 'scheduled_time' in data:
                schedule.scheduled_time = data['scheduled_time'] if data['scheduled_time'] else None
            if 'priority' in data:
                schedule.priority = data['priority']
            if 'status' in data:
                old_status = schedule.status
                schedule.status = data['status']
                if data['status'] == 'completed' and old_status != 'completed':
                    schedule.completed_at = datetime.now()
            if 'assigned_to' in data:
                schedule.assigned_to = data['assigned_to']
            if 'estimated_duration' in data:
                schedule.estimated_duration = int(data['estimated_duration'])
            if 'notes' in data:
                schedule.notes = data['notes']
            
            schedule.save()
            
            return Response({
                'message': 'Schedule updated successfully',
                'id': schedule.id,
                'status': schedule.status
            })
        except MaintenanceSchedule.DoesNotExist:
            return Response({'error': 'Schedule not found'}, status=404)
    
    def delete(self, request, pk):
        """Delete a maintenance schedule"""
        try:
            schedule = MaintenanceSchedule.objects.get(pk=pk)
            schedule.delete()
            return Response({'message': 'Schedule deleted successfully'})
        except MaintenanceSchedule.DoesNotExist:
            return Response({'error': 'Schedule not found'}, status=404)


class AutoScheduleMaintenanceView(APIView):
    """Auto-generate maintenance schedules based on ML predictions"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Auto-create maintenance schedules from predictions"""
        latest = UploadHistory.objects.order_by('-upload_date').first()
        
        if not latest:
            return Response({'error': 'No equipment data available'}, status=404)
        
        thresholds = get_thresholds()
        data = latest.summary_data.get('data', [])
        
        if not data:
            return Response({'error': 'No equipment data found'}, status=404)
        
        df = pd.DataFrame(data)
        predictions = predict_equipment_health(df, thresholds)
        
        created_schedules = []
        today = date.today()
        
        for pred in predictions:
            if pred['risk_level'] in ['critical', 'warning']:
                # Check if already scheduled
                existing = MaintenanceSchedule.objects.filter(
                    equipment_name=pred['equipment_name'],
                    status__in=['scheduled', 'in_progress']
                ).first()
                
                if not existing:
                    priority = 'critical' if pred['risk_level'] == 'critical' else 'high'
                    scheduled_date = today + timedelta(days=min(pred['maintenance_in_days'], 7))
                    
                    schedule = MaintenanceSchedule.objects.create(
                        equipment_name=pred['equipment_name'],
                        equipment_type=pred['type'],
                        title=f"Predicted Maintenance - {pred['risk_level'].title()} Risk",
                        description=f"Auto-generated based on ML predictions.\n\nRisk Score: {pred['risk_score']}%\nRisk Factors: {', '.join(pred['risk_factors']) if pred['risk_factors'] else 'None'}",
                        scheduled_date=scheduled_date,
                        priority=priority,
                        status='scheduled'
                    )
                    
                    created_schedules.append({
                        'id': schedule.id,
                        'equipment_name': schedule.equipment_name,
                        'scheduled_date': schedule.scheduled_date.isoformat(),
                        'priority': schedule.priority
                    })
        
        return Response({
            'message': f'Created {len(created_schedules)} maintenance schedules',
            'schedules': created_schedules
        }, status=201)
