"""
Script de utilidad para obtener tokens de verificación de la base de datos
Útil para pruebas sin tener que consultar MySQL manualmente
"""

import pymysql
from datetime import datetime
import sys

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Cambia esto a tu password
    'database': 'auth_service_db',
    'charset': 'utf8mb4'
}


def get_latest_verification_token():
    """Obtiene el último token de verificación de email"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        query = """
        SELECT vt.token, u.email, u.nombres, vt.expira_en, vt.usado
        FROM verification_tokens vt
        JOIN users u ON vt.user_id = u.id
        WHERE vt.tipo = 'email_verification'
        ORDER BY vt.created_at DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            token, email, nombres, expira_en, usado = result
            print("\n" + "="*60)
            print("🔑 ÚLTIMO TOKEN DE VERIFICACIÓN DE EMAIL")
            print("="*60)
            print(f"Usuario: {nombres}")
            print(f"Email: {email}")
            print(f"Token: {token}")
            print(f"Expira: {expira_en}")
            print(f"Usado: {'Sí' if usado else 'No'}")
            print("="*60)
            print(f"\nURL para verificar:")
            print(f"http://localhost:8000/api/auth/verify-email/{token}")
            print("="*60 + "\n")
        else:
            print("\n❌ No se encontraron tokens de verificación\n")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("💡 Asegúrate de:")
        print("   1. MySQL está corriendo")
        print("   2. La base de datos existe")
        print("   3. Las credenciales en DB_CONFIG son correctas\n")


def get_latest_password_reset_token():
    """Obtiene el último token de recuperación de contraseña"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        query = """
        SELECT vt.token, u.email, u.nombres, vt.expira_en, vt.usado
        FROM verification_tokens vt
        JOIN users u ON vt.user_id = u.id
        WHERE vt.tipo = 'password_reset'
        ORDER BY vt.created_at DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            token, email, nombres, expira_en, usado = result
            print("\n" + "="*60)
            print("🔑 ÚLTIMO TOKEN DE RECUPERACIÓN DE CONTRASEÑA")
            print("="*60)
            print(f"Usuario: {nombres}")
            print(f"Email: {email}")
            print(f"Token: {token}")
            print(f"Expira: {expira_en}")
            print(f"Usado: {'Sí' if usado else 'No'}")
            print("="*60 + "\n")
        else:
            print("\n❌ No se encontraron tokens de recuperación\n")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def list_all_users():
    """Lista todos los usuarios registrados"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        query = """
        SELECT id, nombres, email, rol, estado, email_verificado
        FROM users
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            print("\n" + "="*80)
            print("👥 USUARIOS REGISTRADOS")
            print("="*80)
            print(f"{'ID':<5} {'Nombre':<25} {'Email':<30} {'Rol':<15}")
            print("-"*80)
            
            for user in results:
                id_, nombres, email, rol, estado, verificado = user
                verificado_icon = "✓" if verificado else "✗"
                print(f"{id_:<5} {nombres:<25} {email:<30} {rol:<15} {verificado_icon}")
            
            print("="*80 + "\n")
        else:
            print("\n❌ No hay usuarios registrados\n")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def main():
    print("\n🔧 UTILIDAD DE TOKENS - AUTH SERVICE")
    print("="*60)
    print("1. Ver último token de verificación de email")
    print("2. Ver último token de recuperación de contraseña")
    print("3. Listar todos los usuarios")
    print("4. Ver todos los tokens")
    print("0. Salir")
    print("="*60)
    
    opcion = input("\nSelecciona una opción: ").strip()
    
    if opcion == "1":
        get_latest_verification_token()
    elif opcion == "2":
        get_latest_password_reset_token()
    elif opcion == "3":
        list_all_users()
    elif opcion == "4":
        get_latest_verification_token()
        get_latest_password_reset_token()
    elif opcion == "0":
        print("\n👋 ¡Hasta luego!\n")
        sys.exit(0)
    else:
        print("\n❌ Opción inválida\n")


if __name__ == "__main__":
    # Si se pasa un argumento, ejecutar directamente
    if len(sys.argv) > 1:
        if sys.argv[1] == "verify":
            get_latest_verification_token()
        elif sys.argv[1] == "reset":
            get_latest_password_reset_token()
        elif sys.argv[1] == "users":
            list_all_users()
        else:
            main()
    else:
        main()
