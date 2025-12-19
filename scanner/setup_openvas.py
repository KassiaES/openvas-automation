"""
Setup OpenVAS - Configuração para Conexão Real
Configura credenciais e parâmetros para conectar com OpenVAS/GVM
"""

import os
import sys
from pathlib import Path

def setup_openvas_config():
    """Configuração interativa do OpenVAS"""
    
    print("🔧 CONFIGURAÇÃO DO OPENVAS/GVM")
    print("=" * 50)
    
    # Verificar arquivo .env existente
    env_file = Path('.env')
    current_config = {}
    
    if env_file.exists():
        print("📁 Arquivo .env encontrado - carregando configuração atual...")
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        current_config[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️ Erro ao ler .env: {e}")
    
    print("\n🚀 Configuração do OpenVAS:")
    print("Pressione Enter para manter valor atual (se houver)")
    
    # Configurações do OpenVAS
    configs = {
        'OPENVAS_HOST': 'Host do OpenVAS',
        'OPENVAS_PORT': 'Porta do OpenVAS',
        'OPENVAS_USERNAME': 'Usuário do OpenVAS', 
        'OPENVAS_PASSWORD': 'Senha do OpenVAS',
        'TARGET_HOSTS': 'Hosts para scan (ex: 192.168.1.0/24)',
        'MODE': 'Modo (development/production)'
    }
    
    defaults = {
        'OPENVAS_HOST': 'localhost',
        'OPENVAS_PORT': '9390', 
        'OPENVAS_USERNAME': 'admin',
        'TARGET_HOSTS': '192.168.1.0/24',
        'MODE': 'development'
    }
    
    new_config = {}
    
    for key, description in configs.items():
        current = current_config.get(key, defaults.get(key, ''))
        prompt = f"{description}"
        if current:
            prompt += f" [{current}]"
        prompt += ": "
        
        value = input(prompt).strip()
        if not value and current:
            value = current
            
        new_config[key] = value
    
    # Validações
    if not new_config.get('OPENVAS_PASSWORD'):
        print("⚠️ Senha do OpenVAS é obrigatória para conexão real!")
        new_config['MODE'] = 'development'
    
    # Salvar configuração
    save_config(new_config, current_config)
    
    # Mostrar resumo
    show_summary(new_config)

def save_config(new_config, current_config):
    """Salva configuração no arquivo .env"""
    
    try:
        # Combinar configurações
        final_config = {**current_config, **new_config}
        
        # Salvar no .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("# Configuracao do Sistema de Automacao de Vulnerabilidades\n")
            f.write("# Dados sensiveis - NAO compartilhar\n\n")
            
            # Configurações de email
            email_keys = ['SMTP_SERVER', 'SMTP_PORT', 'EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'EMAIL_DESTINATION']
            if any(key in final_config for key in email_keys):
                f.write("# ========================================\n")
                f.write("# EMAIL CONFIGURATION\n") 
                f.write("# ========================================\n")
                for key in email_keys:
                    if key in final_config:
                        f.write(f"{key}={final_config[key]}\n")
                f.write("\n")
            
            # Configurações do OpenVAS
            f.write("# ========================================\n")
            f.write("# OPENVAS/GVM CONFIGURATION\n")
            f.write("# ========================================\n")
            
            openvas_keys = ['OPENVAS_HOST', 'OPENVAS_PORT', 'OPENVAS_USERNAME', 'OPENVAS_PASSWORD', 
                          'TARGET_HOSTS', 'SCAN_CONFIG_ID', 'SCANNER_ID', 'MODE']
            
            for key in openvas_keys:
                if key in final_config:
                    f.write(f"{key}={final_config[key]}\n")
                    
        print("✅ Configuração salva em .env")
        
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")

def show_summary(config):
    """Mostra resumo da configuração"""
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("=" * 30)
    
    mode = config.get('MODE', 'development')
    print(f"🔧 Modo: {mode.upper()}")
    
    if mode == 'production':
        print(f"🌐 Host: {config.get('OPENVAS_HOST', 'N/A')}")
        print(f"📡 Porta: {config.get('OPENVAS_PORT', 'N/A')}")
        print(f"👤 Usuário: {config.get('OPENVAS_USERNAME', 'N/A')}")
        print(f"🎯 Targets: {config.get('TARGET_HOSTS', 'N/A')}")
        
        if config.get('OPENVAS_PASSWORD'):
            print("🔑 Senha: *** (configurada)")
        else:
            print("⚠️ Senha: NÃO CONFIGURADA")
            
    else:
        print("🧪 Usando dados simulados para aprendizado")
    
    print("\n✅ Configuração concluída!")
    print("Execute 'python main.py' para testar o sistema")

def test_connection():
    """Testa conexão com OpenVAS"""
    
    print("\\n🔍 Testando conexão...")
    
    try:
        # Importar módulo de conexão
        sys.path.append('.')
        from scanner.openvas_connector import OpenVASConnector
        from alerting.email_config import get_mode
        
        mode = get_mode()
        
        if mode != 'production':
            print("ℹ️ Modo development - teste de conexão não necessário")
            return True
            
        connector = OpenVASConnector()
        
        if connector.connect():
            print("✅ Conexão bem-sucedida!")
            connector.disconnect()
            return True
        else:
            print("❌ Falha na conexão")
            return False
            
    except ImportError as e:
        print(f"⚠️ Dependência faltando: {e}")
        print("Execute: pip install python-gvm")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setup do OpenVAS - Sistema de Automação de Vulnerabilidades\\n")
    
    # Verificar se está na pasta correta
    if not os.path.exists('main.py'):
        print("❌ Execute este script na pasta raiz do projeto!")
        sys.exit(1)
    
    # Configurar
    setup_openvas_config()
    
    # Perguntar se quer testar conexão
    if input("\\n🔍 Testar conexão agora? [s/N]: ").lower() == 's':
        test_connection()
        
    print("\\n🎉 Setup concluído!")