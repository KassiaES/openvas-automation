"""
Scanner OpenVAS - Versão Simples para Iniciantes
Carrega dados de vulnerabilidades (mock ou arquivo)
"""

def load_scan_results():
    """
    Simula resultados de scan do OpenVAS
    Em um cenário real, conectaria com a API do OpenVAS
    """
    # Dados simulados de vulnerabilidades
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
            "description": "Directory traversal no servidor web"
        }
    ]
    
    print(f"✅ Scan concluído! {len(vulnerabilidades)} vulnerabilidades encontradas")
    return vulnerabilidades


def load_from_file(filename="scan_results.json"):
    """
    Carrega vulnerabilidades de um arquivo JSON
    Útil para trabalhar com dados reais do OpenVAS
    """
    try:
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Dados carregados de {filename}")
        return data
        
    except FileNotFoundError:
        print(f"❌ Arquivo {filename} não encontrado. Usando dados simulados.")
        return load_scan_results()
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return load_scan_results()


if __name__ == "__main__":
    # Teste do módulo
    vulns = load_scan_results()
    
    print("\n📊 Resumo das vulnerabilidades:")
    for vuln in vulns:
        print(f"- {vuln['name']} | Severidade: {vuln['severity']}")
