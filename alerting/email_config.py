# Configuração de Email e OpenVAS para Alertas

import os
from pathlib import Path

# Carregar variáveis de ambiente de arquivo .env local
def load_env_file():
    """Carrega variáveis do arquivo .env se existir"""
    # Buscar .env na raiz do projeto (2 níveis acima)
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except UnicodeDecodeError:
            # Tentar com encoding alternativo
            try:
                with open(env_file, 'r', encoding='latin1') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception:
                # Se falhar, ignorar .env
                pass

# Carregar .env se existir
load_env_file()

# Configuração de Email usando variáveis de ambiente
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email': os.getenv('EMAIL_ADDRESS', ''),
    'password': os.getenv('EMAIL_PASSWORD', ''),  # 🔒 Senha de APP
    'destination': os.getenv('EMAIL_DESTINATION', os.getenv('EMAIL_ADDRESS', ''))
}

# Configuração do OpenVAS usando variáveis de ambiente
OPENVAS_CONFIG = {
    'host': os.getenv('OPENVAS_HOST', 'localhost'),
    'port': int(os.getenv('OPENVAS_PORT', '9390')),
    'username': os.getenv('OPENVAS_USERNAME', 'admin'),
    'password': os.getenv('OPENVAS_PASSWORD', ''),
    'target_hosts': os.getenv('TARGET_HOSTS', '192.168.1.0/24'),
    'scan_config_id': os.getenv('SCAN_CONFIG_ID', 'daba56c8-73ec-11df-a475-002264764cea'),
    'scanner_id': os.getenv('SCANNER_ID', '08b69003-5fc2-4037-a479-93b440211c73'),
    'mode': os.getenv('MODE', 'development')  # development ou production
}

def is_configured():
    """Verifica se o email está configurado"""
    required = ['email', 'password']
    return all(EMAIL_CONFIG.get(key) for key in required)

def has_basic_email():
    """Verifica se ao menos o email está configurado"""
    return bool(EMAIL_CONFIG.get('email'))

def is_openvas_configured():
    """Verifica se o OpenVAS está configurado para modo production"""
    if OPENVAS_CONFIG['mode'] == 'development':
        return True  # Em modo development não precisa configurar OpenVAS
    
    required = ['host', 'username', 'password']
    return all(OPENVAS_CONFIG.get(key) for key in required)

def get_mode():
    """Retorna o modo de operação (development/production)"""
    return OPENVAS_CONFIG['mode']

# Teste da configuração
def test_email_config():
    import smtplib
    from email.mime.text import MIMEText
    
    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        
        msg = MIMEText("✅ Configuração funcionando! Sistema pronto.")
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = EMAIL_CONFIG['destination']
        msg['Subject'] = "🔧 Teste - Sistema OpenVAS"
        
        server.sendmail(EMAIL_CONFIG['email'], EMAIL_CONFIG['destination'], msg.as_string())
        server.quit()
        
        print("✅ Email de teste enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_email_config()
