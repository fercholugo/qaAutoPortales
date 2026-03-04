import requests
import time
import re

# URL base de la API pública de Guerrilla Mail
API_URL = "https://api.guerrillamail.com/ajax.php"


def generar_correo():
    """
    Genera un correo temporal aleatorio usando la API de Guerrilla Mail.
    Retorna una tupla (email, sid_token) para uso posterior en la sesión.
    """
    resp = requests.get(API_URL, params={"f": "get_email_address"})
    data = resp.json()
    email = data["email_addr"]
    sid_token = data["sid_token"]
    print(f"[GuerrillaMailUtil] Correo temporal generado: {email}")
    return email, sid_token


def leer_codigo(sid_token, asunto_busqueda="", espera=60, regex_codigo=r"Tu PIN de acceso es:\s*(\d{6})"):
    """
    Espera y lee el código de verificación del correo temporal.
    - sid_token: token de sesión obtenido al generar el correo.
    - asunto_busqueda: texto parcial del asunto del email esperado.
    - espera: tiempo máximo de espera en segundos (default 60s).
    - regex_codigo: expresión regular para extraer el código del cuerpo del email.
    Retorna el código encontrado o None si no llega en el tiempo esperado.
    """
    intentos = espera // 5
    print(f"[GuerrillaMailUtil] Esperando email (máx {espera}s)...")
    print(f"[GuerrillaMailUtil] sid_token usado: {sid_token}")
    print(f"[GuerrillaMailUtil] Asunto buscado: '{asunto_busqueda}'")
    print(f"[GuerrillaMailUtil] Regex usado: {regex_codigo}")

    for intento in range(intentos):
        try:
            # Obtener lista de emails recibidos
            resp = requests.get(API_URL, params={
                "f": "get_email_list",
                "sid_token": sid_token,
                "offset": 0
            })
            data = resp.json()
            emails = data.get("list", [])
            print(f"[GuerrillaMailUtil] Intento {intento + 1}/{intentos} — emails en bandeja: {len(emails)}")

            # Ordenar emails por fecha descendente (más reciente primero)
            emails_ordenados = sorted(emails, key=lambda x: int(x.get("mail_timestamp", 0)), reverse=True)

            for email in emails_ordenados:
                asunto = email.get("mail_subject", "")
                # Log de todos los emails en bandeja para diagnóstico
                print(f"[GuerrillaMailUtil] Email en bandeja: asunto='{asunto}'")
                # Filtrar por asunto si se especificó
                if asunto_busqueda.lower() in asunto.lower() or not asunto_busqueda:
                    mail_id = email["mail_id"]
                    print(f"[GuerrillaMailUtil] Email coincide con filtro: asunto='{asunto}', id={mail_id}")

                    # Leer el detalle del email
                    detalle = requests.get(API_URL, params={
                        "f": "fetch_email",
                        "sid_token": sid_token,
                        "email_id": mail_id
                    }).json()

                    cuerpo = detalle.get("mail_body", "")
                    # Eliminar tags HTML para facilitar la extracción
                    cuerpo_limpio = re.sub(r"<[^>]+>", " ", cuerpo)
                    print(f"[GuerrillaMailUtil] Cuerpo del email (limpio): {cuerpo_limpio[:300]}")

                    # Extraer el código con regex
                    match = re.search(regex_codigo, cuerpo_limpio)
                    if match:
                        codigo = match.group(1)
                        print(f"[GuerrillaMailUtil] Código extraído: {codigo}")
                        return codigo
                    else:
                        print(f"[GuerrillaMailUtil] Regex no encontró código en el cuerpo.")

        except Exception as e:
            print(f"[GuerrillaMailUtil] Error en intento {intento + 1}: {e}")

        time.sleep(5)

    print("[GuerrillaMailUtil] No se recibió el código en el tiempo esperado.")
    return None
