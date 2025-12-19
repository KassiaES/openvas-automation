"""
Scanner OpenVAS - Versão Híbrida (Simulado + Real)
Carrega dados simulados ou conecta com OpenVAS real
"""

import os
import sys

# Importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from alerting.email_config import get_mode, is_openvas_configured
    from scanner.openvas_connector import run_openvas_scan
    REAL_SCAN_AVAILABLE = True
except ImportError:
    REAL_SCAN_AVAILABLE = False
    get_mode = lambda: 'development'
    is_openvas_configured = lambda: False
    run_openvas_scan = lambda: None

def load_scan_results():
    """
    Carrega resultados de scan - simulado ou real baseado na configuração
    """
    
    # Verificar modo de operação
    mode = get_mode()
    
    if mode == 'production' and REAL_SCAN_AVAILABLE and is_openvas_configured():
        print("🔄 Modo PRODUCTION - Tentando conectar com OpenVAS real...")
        
        try:
            # Tentar scan real
            real_results = run_openvas_scan()
            
            if real_results:
                print(f"✅ Scan real concluído: {len(real_results)} vulnerabilidades")
                return real_results
            else:
                print("❌ OpenVAS não acessível - verifique se está executando")
                print("   - Docker: docker ps (deve mostrar container openvas)")  
                print("   - Acesso: http://localhost:9392")
                print("⚠️ Usando dados simulados como fallback")
                
        except Exception as e:
            print(f"❌ Erro na conexão com OpenVAS: {e}")
            print("💡 Dica: Instale OpenVAS com Docker:")
            print("   docker run -d -p 9392:80 --name openvas greenbone/gsm-ce")
            print("⚠️ Usando dados simulados como fallback")
    
    # Usar dados simulados (modo development ou fallback)
    if mode == 'development':
        print("🧪 Modo DEVELOPMENT - Usando dados simulados para aprendizado")
    
    return get_simulated_vulnerabilities()

def get_simulated_vulnerabilities():
    """
    Retorna vulnerabilidades simuladas para aprendizado
    """
    vulnerabilidades = [
        {
            "id": "vuln_001", 
            "name": "CVE-2023-1234 - SQL Injection",
            "host": "192.168.1.10",
            "port": "tcp/80",
            "severity": 8.5,
            "description": "Vulnerabilidade de SQL Injection no sistema web"
        },
        {
            "id": "vuln_002",
            "name": "CVE-2023-5678 - Cross-Site Scripting",
            "host": "192.168.1.20", 
            "port": "tcp/443",
            "severity": 6.2,
            "description": "XSS refletido na aplicação web"
        },
        {
            "id": "vuln_003",
            "name": "CVE-2023-9999 - Buffer Overflow", 
            "host": "192.168.1.15",
            "port": "tcp/22",
            "severity": 9.1,
            "description": "Buffer overflow no serviço SSH"
        },
        {
            "id": "vuln_004",
            "name": "Senha fraca detectada",
            "host": "192.168.1.25",
            "port": "tcp/21", 
            "severity": 3.4,
            "description": "Senha padrão em serviço FTP"
        },
        {
            "id": "vuln_005",
            "name": "CVE-2023-4567 - Path Traversal",
            "host": "192.168.1.30",
            "port": "tcp/8080",
            "severity": 7.8,
            "description": "Vulnerabilidade de path traversal"
        },
        {
            "id": "vuln_006",
            "name": "SSL/TLS configuração insegura",
            "host": "192.168.1.40",
            "port": "tcp/443",
            "severity": 5.5,
            "description": "Certificado SSL expirado ou configuração insegura"
        }
    ]
    
    print(f"📋 Simulação carregada: {len(vulnerabilidades)} vulnerabilidades")
    return vulnerabilidades

def load_from_file(filename="scan_results.json"):
    """
    Carrega vulnerabilidades de um arquivo JSON
    Útil para trabalhar com dados reais do OpenVAS exportados
    """
    try:
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Dados carregados de {filename}")
        return data
        
    except FileNotFoundError:
        print(f"❌ Arquivo {filename} não encontrado. Usando dados simulados.")
        return get_simulated_vulnerabilities()
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return get_simulated_vulnerabilities()

if __name__ == "__main__":
    # Teste do módulo
    vulns = load_scan_results()
    
    print("\n📊 Resumo das vulnerabilidades:")
    for vuln in vulns:
        print(f"- {vuln['name']} | Severidade: {vuln['severity']}")
