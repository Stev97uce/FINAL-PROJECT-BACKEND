"""
Main report generation service
KISS principle: Simple orchestration of report generation
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Report, ReportTemplate
from app.schemas import ReportFormat
from app.services.pdf_generator import pdf_generator
from app.services.excel_generator import excel_generator
from app.services.csv_generator import csv_generator
from app.services.microservice_client import microservice_client
from app.config import settings

logger = logging.getLogger(__name__)


class ReportService:
    """
    Core report generation logic
    """
    
    async def generate_report(
        self,
        db: AsyncSession,
        report_id: int,
        token: str
    ) -> bool:
        """
        Generate report file
        
        Args:
            db: Database session
            report_id: Report ID
            token: JWT token for microservice calls
        
        Returns:
            bool: True if successful
        """
        try:
            # Get report
            result = await db.execute(select(Report).where(Report.id == report_id))
            report = result.scalar_one_or_none()
            
            if not report:
                logger.error(f"Report {report_id} not found")
                return False
            
            # Update status
            report.status = "processing"
            await db.commit()
            
            # Collect data based on report type
            data = await self._collect_data(report, token)
            
            if not data:
                report.status = "failed"
                report.error_message = "Failed to collect data"
                await db.commit()
                return False
            
            # Generate file
            file_path = self._get_file_path(report)
            success = False
            
            if report.format == ReportFormat.PDF:
                success = pdf_generator.generate_report(
                    file_path,
                    report.name,
                    data,
                    include_charts=settings.ENABLE_CHARTS
                )
            elif report.format == ReportFormat.XLSX:
                success = excel_generator.generate_report(
                    file_path,
                    report.name,
                    data
                )
            elif report.format == ReportFormat.CSV:
                success = csv_generator.generate_report(
                    file_path,
                    report.name,
                    data
                )
            
            # Update report
            if success:
                report.status = "completed"
                report.file_path = file_path
                report.file_size_bytes = os.path.getsize(file_path)
                report.completed_at = datetime.utcnow()
            else:
                report.status = "failed"
                report.error_message = "File generation failed"
            
            await db.commit()
            return success
            
        except Exception as e:
            logger.error(f"Error generating report {report_id}: {str(e)}")
            report.status = "failed"
            report.error_message = str(e)
            await db.commit()
            return False
    
    async def _collect_data(self, report: Report, token: str) -> Optional[Dict[str, Any]]:
        """
        Collect data from microservices
        """
        try:
            # Example: Dashboard report
            if report.type == "analytical":
                return await self._get_dashboard_data(report, token)
            
            # Example: Appointments report
            elif report.type == "operational":
                return await self._get_appointments_data(report, token)
            
            # Default structure
            return {
                "summary": f"Reporte generado: {report.name}",
                "tables": [{
                    "title": "Datos del Reporte",
                    "headers": ["Campo", "Valor"],
                    "rows": [
                        ["Tipo", report.type],
                        ["Formato", report.format],
                        ["Fecha", datetime.now().strftime("%Y-%m-%d")]
                    ]
                }]
            }
            
        except Exception as e:
            logger.error(f"Error collecting data: {str(e)}")
            return None
    
    async def _get_dashboard_data(self, report: Report, token: str) -> Dict[str, Any]:
        """
        Get dashboard data from multiple services
        """
        start_date = report.start_date.strftime("%Y-%m-%d") if report.start_date else None
        end_date = report.end_date.strftime("%Y-%m-%d") if report.end_date else None
        
        # Call microservices (simplified)
        appointments_stats = await microservice_client.get_appointments_stats(
            start_date, end_date, token
        ) or {}
        
        return {
            "summary": "Dashboard Ejecutivo - Resumen de métricas del sistema",
            "tables": [{
                "title": "Métricas de Citas",
                "headers": ["Métrica", "Valor"],
                "rows": [
                    ["Total Citas", appointments_stats.get("total", 0)],
                    ["Completadas", appointments_stats.get("completed", 0)],
                    ["Canceladas", appointments_stats.get("cancelled", 0)]
                ]
            }],
            "charts": [{
                "type": "bar",
                "title": "Estado de Citas",
                "labels": ["Completadas", "Canceladas", "Pendientes"],
                "values": [
                    appointments_stats.get("completed", 0),
                    appointments_stats.get("cancelled", 0),
                    appointments_stats.get("pending", 0)
                ]
            }]
        }
    
    async def _get_appointments_data(self, report: Report, token: str) -> Dict[str, Any]:
        """
        Get appointments operational data
        """
        return {
            "summary": "Reporte Operacional de Citas",
            "tables": [{
                "title": "Citas del Período",
                "headers": ["Fecha", "Consultante", "Psicólogo", "Estado"],
                "rows": [
                    ["2024-01-15", "Juan Pérez", "Dr. María López", "Completada"],
                    ["2024-01-16", "Ana García", "Dr. Carlos Ruiz", "Pendiente"]
                ]
            }]
        }
    
    def _get_file_path(self, report: Report) -> str:
        """
        Generate file path for report
        """
        os.makedirs(settings.REPORTS_STORAGE_PATH, exist_ok=True)
        
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{report.format}"
        return os.path.join(settings.REPORTS_STORAGE_PATH, filename)


# Global instance
report_service = ReportService()
