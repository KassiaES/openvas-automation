"""
Sistema de Alertas - Versão Simplificada
Envia alertas por email quando vulnerabilidades críticas são encontradas
"""

import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import sys

# Importar configurações
try:
    from .email_config import EMAIL_CONFIG, is_configured
    EMAIL_WORKING = is_configured()
except ImportError:
    try:
        # Fallback para importação absoluta
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from email_config import EMAIL_CONFIG, is_configured
        EMAIL_WORKING = is_configured()
    except ImportError:
        EMAIL_CONFIG = None
        EMAIL_WORKING = False


def send_alert(critical_df):
    """Envia alerta por email ou console"""
    if critical_df.empty:
        print("✅ Nenhuma vulnerabilidade crítica encontrada.")
        return
    
    # Tentar email primeiro
    if EMAIL_WORKING:
        try:
            _send_email(critical_df)
            print(f"📧 ✅ Alerta enviado por email: {len(critical_df)} vulnerabilidades críticas")
            return
        except Exception as e:
            print(f"❌ Erro no email: {e}")
    else:
        # Primeira execução - oferecer configuração
        if EMAIL_CONFIG is None:
            print("\n⚠️  Email não configurado.")
            print("🚨 VULNERABILIDADES CRÍTICAS DETECTADAS!")
            
            try:
                setup = input("\n📧 Configurar email agora? (s/N): ").strip().lower()
                if setup == 's':
                    print("\n🔧 Execute: python alerting/setup_email.py")
                    print("   Depois execute: python main.py novamente")
                    return
            except KeyboardInterrupt:
                pass
    
    # Fallback para console
    _console_alert(critical_df)


def _send_email(critical_df):
    # Email básico
    msg = MIMEText(f"""🚨 ALERTA DE SEGURANÇA

{len(critical_df)} vulnerabilidades críticas encontradas!

Vulnerabilidades:
{critical_df[['name', 'host', 'severity']].to_string()}

⚠️  AÇÃO IMEDIATA NECESSÁRIA!
""")
    
    msg['From'] = EMAIL_CONFIG['email']
    msg['To'] = EMAIL_CONFIG['destination']
    msg['Subject'] = f"🚨 ALERTA - {len(critical_df)} Vulnerabilidades Críticas"
    
    # Anexar CSV
    csv_data = critical_df.to_csv(index=False)
    attachment = MIMEBase('text', 'csv')
    attachment.set_payload(csv_data.encode())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment; filename=vulnerabilidades.csv')
    
    # Criar mensagem completa
    from email.mime.multipart import MIMEMultipart
    full_msg = MIMEMultipart()
    full_msg['From'] = msg['From']
    full_msg['To'] = msg['To']
    full_msg['Subject'] = msg['Subject']
    full_msg.attach(msg)
    full_msg.attach(attachment)
    
    # Enviar
    server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
    server.starttls()
    server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
    server.sendmail(EMAIL_CONFIG['email'], EMAIL_CONFIG['destination'], full_msg.as_string())
    server.quit()


def _console_alert(critical_df):
    """Alerta no console"""
    print(f"\n🚨 ALERTA: {len(critical_df)} vulnerabilidades críticas!")
    print("=" * 50)
    for _, vuln in critical_df.iterrows():
        print(f"• {vuln['name']} | {vuln['host']} | Severidade: {vuln['severity']}")
    print("=" * 50)
    print("🚀 AÇÃO REQUERIDA: Corrija imediatamente!")


def send_summary_alert(stats):
    """Resumo simples"""
    total = stats.get('total', 0)
    critical = stats.get('critical_count', 0)
    
    if critical > 0:
        level = "🔴 CRÍTICO"
    elif stats.get('high_count', 0) > 0:
        level = "🟠 ALTO"
    else:
        level = "🟢 BAIXO"
    
    print(f"\n📊 RESUMO: {total} vulnerabilidades | Risco: {level}")