"""
Configuração Universal de Email
Suporta Gmail, Outlook, Yahoo e outros
"""

import smtplib
import getpass
from email.mime.text import MIMEText
import os

# Configurações dos principais provedores
PROVIDERS = {
    'gmail': {
        'name': 'Gmail',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'help': '1. Ative 2FA: https://myaccount.google.com/security\n2. Gere senha de app: https://myaccount.google.com/apppasswords'
    },
    'outlook': {
        'name': 'Outlook/Hotmail',
        'smtp_server': 'smtp-mail.outlook.com', 
        'smtp_port': 587,
        'help': 'Use sua senha normal (sem senha de app)'
    },
    'yahoo': {
        'name': 'Yahoo Mail',
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'help': '1. Ative 2FA\n2. Gere senha de app: https://login.yahoo.com/account/security'
    }
}

def detect_provider(email):
    """Detecta provedor pelo email"""
    email = email.lower()
    if '@gmail.com' in email:
        return 'gmail'
    elif '@outlook.com' in email or '@hotmail.com' in email or '@live.com' in email:
        return 'outlook'  
    elif '@yahoo.com' in email or '@yahoo.com.br' in email:
        return 'yahoo'
    else:
        return None

def setup_email():
    """Configuração universal de email"""
    print("📧 CONFIGURAÇÃO DE EMAIL")
    print("=" * 30)
    
    # Coletar email
    email = input("📧 Seu email: ").strip()
    
    # Detectar provedor
    provider = detect_provider(email)
    
    if provider:
        config = PROVIDERS[provider]
        print(f"\n✅ {config['name']} detectado automaticamente!")
        print(f"\n📋 Instruções para {config['name']}:")
        print(config['help'])
        print()
    else:
        # Provedor não reconhecido - permitir escolha manual
        print(f"\n⚠️  Provedor não reconhecido: {email}")
        print("Escolha seu provedor:")
        print("1️⃣  Gmail")
        print("2️⃣  Outlook/Hotmail") 
        print("3️⃣  Yahoo")
        print("4️⃣  Outro (configuração manual)")
        
        choice = input("\nEscolha (1-4): ").strip()
        
        if choice == "1":
            provider = 'gmail'
        elif choice == "2":
            provider = 'outlook'
        elif choice == "3":
            provider = 'yahoo'
        elif choice == "4":
            # Configuração manual
            smtp_server = input("SMTP Server: ").strip()
            smtp_port = input("SMTP Port (587): ").strip() or "587"
            config = {
                'name': 'Personalizado',
                'smtp_server': smtp_server,
                'smtp_port': int(smtp_port),
                'help': 'Configuração manual'
            }
        else:
            print("❌ Opção inválida!")
            return False
            
        if choice != "4":
            config = PROVIDERS[provider]
            print(f"\n📋 Instruções para {config['name']}:")
            print(config['help'])
            print()
    
    # Coletar senha
    if provider == 'outlook':
        password = getpass.getpass("🔑 Sua senha: ")
    else:
        password = getpass.getpass("🔑 Senha de APP: ").strip().replace(' ', '')
    
    destination = input("📤 Email destino (Enter=mesmo): ").strip() or email
    
    # Testar conexão
    print("\n🧪 Testando configuração...")
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(email, password)
        
        # Enviar teste
        msg = MIMEText("✅ Email configurado com sucesso!\n\nSistema OpenVAS funcionando.")
        msg['From'] = email
        msg['To'] = destination
        msg['Subject'] = "🔧 Teste - Sistema OpenVAS"
        
        server.sendmail(email, destination, msg.as_string())
        server.quit()
        
        print("✅ Email de teste enviado!")
        
        # Salvar configuração
        env_content = f"""# Configuração de Email - LOCAL APENAS
SMTP_SERVER={config['smtp_server']}
SMTP_PORT={config['smtp_port']}
EMAIL_ADDRESS={email}
EMAIL_PASSWORD={password}
EMAIL_DESTINATION={destination}
"""
        
        # Voltar para raiz do projeto (2 níveis acima)
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root_path, '.env'), 'w') as f:
            f.write(env_content)
        
        print("💾 Configuração salva em .env")
        print(f"🎯 Provedor: {config['name']}")
        print("\n🚀 Pronto! Execute: python main.py")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n🔧 Possíveis soluções:")
        if provider == 'gmail':
            print("• Gere nova senha de app")
            print("• Verifique se 2FA está ativo")
        elif provider == 'outlook':
            print("• Verifique email e senha")  
            print("• Tente ativar 'Aplicativos menos seguros'")
        else:
            print("• Verifique credenciais")
            print("• Confirme configurações SMTP")
        return False

if __name__ == "__main__":
    setup_email()