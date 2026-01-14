"""
HTTP client for calling other microservices
KISS principle: Simple async HTTP calls with retry logic
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class MicroserviceClient:
    """
    Client to interact with other microservices
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.services = {
            "auth": settings.AUTH_SERVICE_URL,
            "user": settings.USER_SERVICE_URL,
            "patient": settings.PATIENT_SERVICE_URL,
            "appointment": settings.APPOINTMENT_SERVICE_URL,
            "room": settings.ROOM_SERVICE_URL,
            "clinical": settings.CLINICAL_SERVICE_URL,
            "supervision": settings.SUPERVISION_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL
        }
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with error handling
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json
                )
                
                if response.status_code >= 400:
                    logger.error(f"HTTP {response.status_code} from {url}: {response.text}")
                    return None
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Request error to {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling {url}: {str(e)}")
            return None
    
    async def get_users_stats(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get user statistics from User Service"""
        url = f"{self.services['user']}/api/users/stats"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)
    
    async def get_patients_list(self, filters: Dict, token: str) -> Optional[Dict]:
        """Get patients list from Patient Service"""
        url = f"{self.services['patient']}/api/pacientes"
        headers = {"Authorization": f"Bearer {token}"}
        
        return await self._make_request("GET", url, headers=headers, params=filters)
    
    async def get_expedientes_stats(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get expedientes statistics from Patient Service"""
        url = f"{self.services['patient']}/api/expedientes/stats"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)
    
    async def get_appointments_stats(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get appointments statistics from Appointment Service"""
        url = f"{self.services['appointment']}/api/v1/appointments/stats"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)
    
    async def get_rooms_utilization(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get room utilization from Room Service"""
        url = f"{self.services['room']}/api/v1/rooms/utilization"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)
    
    async def get_clinical_sessions_stats(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get clinical sessions statistics from Clinical Service"""
        url = f"{self.services['clinical']}/api/v1/sessions/stats"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)
    
    async def get_supervision_stats(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get supervision statistics from Supervision Service"""
        url = f"{self.services['supervision']}/api/v1/supervision/stats"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)
    
    async def get_notifications_stats(self, start_date: str, end_date: str, token: str) -> Optional[Dict]:
        """Get notifications statistics from Notification Service"""
        url = f"{self.services['notification']}/api/v1/admin/stats"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"start_date": start_date, "end_date": end_date}
        
        return await self._make_request("GET", url, headers=headers, params=params)


# Global instance
microservice_client = MicroserviceClient()
