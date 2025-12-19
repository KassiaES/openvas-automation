"""
OpenVAS Connector - Conexão Real com Greenbone Vulnerability Manager
Conecta com API do OpenVAS para realizar scans reais
"""

import os
import sys
import time
from datetime import datetime

# Importações condicionais
try:
    from gvm.connections import UnixSocketConnection, TLSConnection
    from gvm.protocols.gmp import Gmp
    from gvm.transforms import EtreeTransform
    from gvm.xml import pretty_print
    GVM_AVAILABLE = True
except ImportError:
    GVM_AVAILABLE = False

try:
    import xml.etree.ElementTree as ET
except ImportError:
    ET = None

# Importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from alerting.email_config import OPENVAS_CONFIG, get_mode, is_openvas_configured
except ImportError:
    OPENVAS_CONFIG = {
        'host': 'localhost',
        'port': 9390,
        'username': 'admin', 
        'password': '',
        'target_hosts': '192.168.1.0/24',
        'mode': 'development'
    }
    get_mode = lambda: 'development'
    is_openvas_configured = lambda: False

class OpenVASConnector:
    """
    Classe para conectar com OpenVAS/GVM e executar scans
    """
    
    def __init__(self):
        self.connection = None
        self.gmp = None
        self.connected = False
        
    def connect(self):
        """Conecta com o OpenVAS/GVM"""
        if not GVM_AVAILABLE:
            raise ImportError("python-gvm não está instalado. Execute: pip install python-gvm")
            
        try:
            # Tentar conexão TLS primeiro
            self.connection = TLSConnection(
                hostname=OPENVAS_CONFIG['host'],
                port=OPENVAS_CONFIG['port']
            )
            
            # Usar context manager para conexão
            with Gmp(connection=self.connection, transform=EtreeTransform()) as gmp:
                # Autenticar
                gmp.authenticate(
                    OPENVAS_CONFIG['username'], 
                    OPENVAS_CONFIG['password']
                )
                self.gmp = gmp
            
            self.connected = True
            print(f"✅ Conectado ao OpenVAS em {OPENVAS_CONFIG['host']}:{OPENVAS_CONFIG['port']}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Desconecta do OpenVAS"""
        try:
            if hasattr(self, 'connection') and self.connection:
                self.connection.disconnect()
        except:
            pass
        finally:
            self.connected = False
            print("🔌 Desconectado do OpenVAS")
            
    def create_target(self, name, hosts):
        """Cria um target para scan"""
        try:
            response = self.gmp.create_target(name=name, hosts=[hosts])
            target_id = response.get('id')
            print(f"🎯 Target criado: {name} ({target_id})")
            return target_id
        except Exception as e:
            print(f"❌ Erro ao criar target: {e}")
            return None
            
    def start_scan(self, target_id, scan_name=None):
        """Inicia um scan"""
        if not scan_name:
            scan_name = f"Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        try:
            # Usar configuração padrão "Full and fast"
            config_id = OPENVAS_CONFIG.get('scan_config_id', 'daba56c8-73ec-11df-a475-002264764cea')
            scanner_id = OPENVAS_CONFIG.get('scanner_id', '08b69003-5fc2-4037-a479-93b440211c73')
            
            response = self.gmp.create_task(
                name=scan_name,
                config_id=config_id,
                target_id=target_id,
                scanner_id=scanner_id
            )
            
            task_id = response.get('id')
            print(f"📋 Task criada: {scan_name} ({task_id})")
            
            # Iniciar scan
            self.gmp.start_task(task_id)
            print(f"🚀 Scan iniciado: {task_id}")
            
            return task_id
            
        except Exception as e:
            print(f"❌ Erro ao iniciar scan: {e}")
            return None
            
    def wait_for_scan(self, task_id, timeout=3600):
        """Aguarda conclusão do scan"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.gmp.get_task(task_id)
                status = response.find('task/status').text
                progress = response.find('task/progress').text
                
                print(f"📊 Status: {status} - Progresso: {progress}%")
                
                if status in ['Done', 'Stopped', 'Interrupted']:
                    return status == 'Done'
                    
                time.sleep(30)  # Aguardar 30 segundos
                
            except Exception as e:
                print(f"❌ Erro ao verificar status: {e}")
                return False
                
        print(f"⏰ Timeout: scan não finalizou em {timeout} segundos")
        return False
        
    def get_results(self, task_id):
        """Obtém resultados do scan"""
        try:
            response = self.gmp.get_results(task_id=task_id)
            results = []
            
            for result in response.findall('result'):
                # Extrair dados da vulnerabilidade
                vuln_data = {
                    'id': result.get('id'),
                    'name': result.find('.//name').text if result.find('.//name') is not None else 'Unknown',
                    'host': result.find('host').text if result.find('host') is not None else 'Unknown',
                    'port': result.find('port').text if result.find('port') is not None else 'Unknown',
                    'severity': float(result.find('severity').text) if result.find('severity') is not None else 0.0,
                    'description': result.find('.//description').text if result.find('.//description') is not None else 'No description',
                    'threat': result.find('threat').text if result.find('threat') is not None else 'Unknown'
                }
                
                # Filtrar apenas resultados com severidade > 0
                if vuln_data['severity'] > 0:
                    results.append(vuln_data)
                    
            print(f"📊 Encontradas {len(results)} vulnerabilidades")
            return results
            
        except Exception as e:
            print(f"❌ Erro ao obter resultados: {e}")
            return []

def run_openvas_scan(target_hosts=None):
    """
    Executa scan completo no OpenVAS
    Retorna lista de vulnerabilidades encontradas
    """
    
    # Verificar se está em modo production
    if get_mode() != 'production':
        print("ℹ️ Modo development - usando dados simulados")
        return None
        
    if not is_openvas_configured():
        print("❌ OpenVAS não configurado adequadamente")
        return None
        
    if not target_hosts:
        target_hosts = OPENVAS_CONFIG['target_hosts']
        
    connector = OpenVASConnector()
    
    try:
        # Conectar
        if not connector.connect():
            return None
            
        # Criar target
        target_name = f"Target_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_id = connector.create_target(target_name, target_hosts)
        
        if not target_id:
            return None
            
        # Iniciar scan
        task_id = connector.start_scan(target_id)
        
        if not task_id:
            return None
            
        print("⏳ Aguardando conclusão do scan...")
        print("Isso pode levar alguns minutos ou horas dependendo do target...")
        
        # Aguardar conclusão
        if connector.wait_for_scan(task_id):
            # Obter resultados
            results = connector.get_results(task_id)
            return results
        else:
            print("❌ Scan não finalizou com sucesso")
            return None
            
    finally:
        # Sempre desconectar
        connector.disconnect()

if __name__ == "__main__":
    # Teste de conexão
    results = run_openvas_scan()
    if results:
        print(f"✅ Scan concluído! {len(results)} vulnerabilidades encontradas")
        for vuln in results[:3]:  # Mostrar apenas as 3 primeiras
            print(f"  • {vuln['name']} - Severidade: {vuln['severity']}")
    else:
        print("❌ Scan falhou ou retornou vazio")