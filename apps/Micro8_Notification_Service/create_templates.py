"""
Script para crear templates de notificaciones predeterminados
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import NotificationTemplate, NotificationChannel
from app.config import settings


async def create_default_templates():
    """Create default notification templates"""
    
    # Connect to MongoDB (use localhost for local execution)
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://root:rootpassword@localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[NotificationTemplate]
    )
    
    templates = [
        {
            "name": "email_verification",
            "channel": NotificationChannel.EMAIL,
            "event_type": "user.registered",
            "subject": "Verifica tu email - UCE Psychology",
            "body": """
            <h2>Hola {{user_name}},</h2>
            <p>Gracias por registrarte en el Sistema de Gestión de Consultantes UCE.</p>
            <p>Por favor verifica tu email haciendo clic en el siguiente enlace:</p>
            <a href="{{verification_link}}">Verificar Email</a>
            <p>Si no solicitaste esta cuenta, puedes ignorar este correo.</p>
            <p>Saludos,<br>Equipo UCE Psychology</p>
            """,
            "variables": ["user_name", "verification_link"]
        },
        {
            "name": "welcome_email",
            "channel": NotificationChannel.EMAIL,
            "event_type": "user.verified",
            "subject": "Bienvenido a UCE Psychology",
            "body": """
            <h2>¡Bienvenido {{user_name}}!</h2>
            <p>Tu cuenta ha sido verificada exitosamente.</p>
            <p>Ya puedes acceder a nuestros servicios de psicología.</p>
            <p>Saludos,<br>Equipo UCE Psychology</p>
            """,
            "variables": ["user_name"]
        },
        {
            "name": "appointment_confirmation_email",
            "channel": NotificationChannel.EMAIL,
            "event_type": "appointment.created",
            "subject": "Confirmación de Cita - UCE Psychology",
            "body": """
            <h2>Hola {{patient_name}},</h2>
            <p>Tu cita ha sido confirmada:</p>
            <ul>
                <li><strong>Fecha:</strong> {{appointment_date}}</li>
                <li><strong>Hora:</strong> {{appointment_time}}</li>
                <li><strong>Psicólogo:</strong> {{psychologist_name}}</li>
                <li><strong>Consultorio:</strong> {{room_name}}</li>
            </ul>
            <p>Recibirás recordatorios 48h y 24h antes de tu cita.</p>
            <p>Saludos,<br>Equipo UCE Psychology</p>
            """,
            "variables": ["patient_name", "appointment_date", "appointment_time", "psychologist_name", "room_name"]
        },
        {
            "name": "appointment_confirmation_whatsapp",
            "channel": NotificationChannel.WHATSAPP,
            "event_type": "appointment.created",
            "subject": None,
            "body": """Hola {{patient_name}}, tu cita en UCE Psychology está confirmada:
📅 Fecha: {{appointment_date}}
🕐 Hora: {{appointment_time}}
👨‍⚕️ Psicólogo: {{psychologist_name}}
🏥 Consultorio: {{room_name}}

Recibirás recordatorios antes de tu cita.""",
            "variables": ["patient_name", "appointment_date", "appointment_time", "psychologist_name", "room_name"]
        },
        {
            "name": "appointment_reminder_email",
            "channel": NotificationChannel.EMAIL,
            "event_type": "appointment.reminder",
            "subject": "Recordatorio de Cita - UCE Psychology",
            "body": """
            <h2>Hola {{patient_name}},</h2>
            <p>Te recordamos tu cita programada:</p>
            <ul>
                <li><strong>Fecha:</strong> {{appointment_date}}</li>
                <li><strong>Hora:</strong> {{appointment_time}}</li>
                <li><strong>Psicólogo:</strong> {{psychologist_name}}</li>
            </ul>
            <p>Nos vemos pronto!</p>
            <p>Saludos,<br>Equipo UCE Psychology</p>
            """,
            "variables": ["patient_name", "appointment_date", "appointment_time", "psychologist_name"]
        },
        {
            "name": "supervisor_session_alert",
            "channel": NotificationChannel.INTERNAL,
            "event_type": "clinical.session_recorded",
            "subject": "Nueva sesión clínica para revisar",
            "body": "Un estudiante ha completado una nota de sesión que requiere tu supervisión.",
            "variables": ["category", "priority", "session_note_id", "action_url"]
        },
        {
            "name": "student_feedback_alert",
            "channel": NotificationChannel.INTERNAL,
            "event_type": "supervision.feedback_added",
            "subject": "Nuevo feedback de supervisión",
            "body": "Tu supervisor ha revisado tu sesión clínica y agregado comentarios.",
            "variables": ["category", "priority", "feedback_id", "action_url"]
        }
    ]
    
    for template_data in templates:
        # Check if exists
        existing = await NotificationTemplate.find_one(
            NotificationTemplate.name == template_data["name"]
        )
        
        if existing:
            print(f"✅ Template '{template_data['name']}' already exists, skipping")
            continue
        
        # Create template
        template = NotificationTemplate(**template_data)
        await template.insert()
        print(f"✅ Created template: {template_data['name']}")
    
    print("\n✅ All default templates created successfully!")
    client.close()


if __name__ == "__main__":
    asyncio.run(create_default_templates())
