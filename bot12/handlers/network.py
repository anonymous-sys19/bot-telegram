# handlers/network.py
from telegram.ext import CommandHandler
import requests
import nmap
import os
from bot12.utils.chat_history import save_history
# from bot12.config import IP_API_KEY, WHOIS_API_KEY # Importar directamente las claves desde config para uso, aunque provienen de ENV

async def scan(update, context):
    try:
        # Aquí se obtiene la clave de la API de IP desde las variables de entorno
        # No se usa aquí, pero se mantiene la estructura por si la necesitas en el futuro en esta función.
        # IP_API_KEY_ENV = os.getenv("IP_API_KEY") # Esto ya se cargaría en config.py si se necesitara directamente aquí

        nm = nmap.PortScanner()
        target = context.args[0] if context.args else "127.0.0.1"
        
        # Validar formato IP básico para evitar errores de Nmap
        if not all(part.isdigit() and 0 <= int(part) <= 255 for part in target.split('.')) and target != "localhost":
            await update.message.reply_text("Formato de IP inválido. Por favor, usa una IP válida (ej. 192.168.1.1) o 'localhost'.")
            save_history(update.message.chat_id, f"Error scan: IP inválida {target}")
            return

        await update.message.reply_text(f"🔍 Escaneando {target}... Esto puede tardar.")
        
        # Opciones de Nmap para ser más específico y evitar escaneos amplios no deseados
        # '-T4': Más rápido que el default
        # '-F': Escaneo rápido (menos puertos)
        # '-p 22,23,80,443,8080': Puertos comunes, puedes expandirlo
        nm.scan(target, arguments='-T4 -F -p 22,23,80,443,8080') # Escanea puertos comunes por defecto
        
        if not nm.all_hosts():
            await update.message.reply_text(f"No se encontraron hosts accesibles o puertos abiertos en {target} en los puertos especificados.")
            save_history(update.message.chat_id, f"Escaneo: {target} - No se encontraron hosts/puertos")
            return

        scan_results = []
        for host in nm.all_hosts():
            scan_results.append(f"Host: {host} ({nm[host].hostname()})")
            scan_results.append(f"Estado: {nm[host].state()}")
            for proto in nm[host].all_protocols():
                scan_results.append(f"Protocolo: {proto}")
                lport = nm[host][proto].keys()
                for port in sorted(lport):
                    scan_results.append(f"Puerto: {port}\tEstado: {nm[host][proto][port]['state']}\tServicio: {nm[host][proto][port]['name']}")
            scan_results.append("-" * 20) # Separador
        
        if scan_results:
            result_text = "\n".join(scan_results)
            await update.message.reply_text(f"🔍 Escaneo de {target}:\n```\n{result_text}\n```", parse_mode='MarkdownV2')
            save_history(update.message.chat_id, f"Escaneo exitoso: {target}")
        else:
            await update.message.reply_text(f"No se obtuvieron resultados de escaneo para {target}. Posiblemente Nmap no detectó nada o no está instalado/configurado correctamente.")
            save_history(update.message.chat_id, f"Escaneo vacío/error Nmap para: {target}")

    except nmap.PortScannerError as e:
        await update.message.reply_text(f"Error de Nmap. Asegúrate de que Nmap esté instalado y en tu PATH, y que tengas permisos. 😿 ({e})")
        save_history(update.message.chat_id, f"Error Nmap: {str(e)}")
    except IndexError:
        await update.message.reply_text("Uso: `/scan <IP>` (ej. `/scan 192.168.1.1`)\nRecuerda que Nmap debe estar instalado.")
        save_history(update.message.chat_id, "Uso incorrecto /scan")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado en escaneo. 😿 ({e})")
        save_history(update.message.chat_id, f"Error scan (inesperado): {str(e)}")


async def ipinfo(update, context):
    try:
        ip = context.args[0] if context.args else "8.8.8.8"
        # Validar formato IP
        if not all(part.isdigit() and 0 <= int(part) <= 255 for part in ip.split('.')):
            await update.message.reply_text("Formato de IP inválido. Por favor, usa una IP válida (ej. 8.8.8.8).")
            save_history(update.message.chat_id, f"Error ipinfo: IP inválida {ip}")
            return
            
        url = f"https://api.iplocate.io/api/lookup/{ip}?apikey={os.getenv('IP_API_KEY')}" # Acceso a la clave desde ENV
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        result = (
            f"🌐 IP: {ip}\n"
            f"Ciudad: {data.get('city', 'N/A')}\n"
            f"Región: {data.get('subdivision', 'N/A')}\n"
            f"País: {data.get('country', 'N/A')}\n"
            f"Coordenadas: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}\n"
            f"ISP: {data.get('org', 'N/A')}"
        )
        await update.message.reply_text(result)
        save_history(update.message.chat_id, f"Consulta IP: {ip}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error de red al consultar IP. Verifica la API Key y conexión. 😿 ({e})")
        save_history(update.message.chat_id, f"Error ipinfo (red): {str(e)}")
    except IndexError:
        await update.message.reply_text("Uso: `/ipinfo <IP>` (ej. `/ipinfo 8.8.8.8`)")
        save_history(update.message.chat_id, "Uso incorrecto /ipinfo")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado al consultar IP. 😿 ({e})")
        save_history(update.message.chat_id, f"Error ipinfo (inesperado): {str(e)}")

async def whois(update, context):
    try:
        if not context.args:
            await update.message.reply_text("Uso: `/whois <dominio>`")
            return
        domain = context.args[0]
        # Validación básica de dominio
        if "." not in domain or domain.startswith(".") or domain.endswith("."):
            await update.message.reply_text("Formato de dominio inválido. Ejemplo: `google.com`.")
            save_history(update.message.chat_id, f"Error whois: dominio inválido {domain}")
            return

        url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={os.getenv('WHOIS_API_KEY')}&domainName={domain}&outputFormat=JSON" # Acceso a la clave desde ENV
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "WhoisRecord" not in data or not data["WhoisRecord"]:
            await update.message.reply_text(f"No se encontró información WHOIS para '{domain}'. Posiblemente no existe o la API no pudo consultarlo.")
            save_history(update.message.chat_id, f"WHOIS no encontrado para: {domain}")
            return
            
        record = data["WhoisRecord"]
        
        registrant_info = record.get('registrant', {})
        admin_info = record.get('administrativeContact', {})
        tech_info = record.get('technicalContact', {})

        result = (
            f"🌍 **Dominio**: {record.get('domainName', 'N/A')}\n"
            f"**Registrador**: {record.get('registrarName', 'N/A')}\n"
            f"**ID del Registrador**: {record.get('registrarIANAID', 'N/A')}\n"
            f"**Estado del Dominio**: {', '.join(record.get('domainStatus', ['N/A']))}\n"
            f"**Fecha de Creación**: {record.get('createdDate', 'N/A')}\n"
            f"**Fecha de Actualización**: {record.get('updatedDate', 'N/A')}\n"
            f"**Fecha de Expiración**: {record.get('expiresDate', 'N/A')}\n\n"
            f"**Propietario (Registrante)**:\n"
            f"  Organización: {registrant_info.get('organization', 'N/A')}\n"
            f"  Nombre: {registrant_info.get('name', 'N/A')}\n"
            f"  Email: {registrant_info.get('email', 'N/A')}\n"
            f"  País: {registrant_info.get('country', 'N/A')}\n\n"
            f"**Contacto Administrativo**:\n"
            f"  Organización: {admin_info.get('organization', 'N/A')}\n"
            f"  Email: {admin_info.get('email', 'N/A')}\n\n"
            f"**Contacto Técnico**:\n"
            f"  Organización: {tech_info.get('organization', 'N/A')}\n"
            f"  Email: {tech_info.get('email', 'N/A')}"
        )
        await update.message.reply_text(result, parse_mode='Markdown')
        save_history(update.message.chat_id, f"Consulta WHOIS: {domain}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error de red al consultar WHOIS. Verifica la API Key y conexión. 😿 ({e})")
        save_history(update.message.chat_id, f"Error whois (red): {str(e)}")
    except IndexError:
        await update.message.reply_text("Uso: `/whois <dominio>`")
        save_history(update.message.chat_id, "Uso incorrecto /whois")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado al consultar WHOIS. 😿 ({e})")
        save_history(update.message.chat_id, f"Error whois (inesperado): {str(e)}")

def register_network_handlers(application):
    application.add_handler(CommandHandler("scan", scan))
    application.add_handler(CommandHandler("ipinfo", ipinfo))
    application.add_handler(CommandHandler("whois", whois))