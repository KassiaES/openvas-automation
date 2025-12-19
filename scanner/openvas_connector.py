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
        'port': 9392,
        'username': 'admin', 
        'password': 'admin',
        'target_hosts': '192.168.1.0/24',
        'mode': 'production'
    }
    get_mode = lambda: 'development'
    is_openvas_configured = lambda: False

class OpenVASConnector:
    """
    Classe para conectar com OpenVAS/GVM e executar scans
    """
    
    def __init__(self):
        self.connection = None
        self.connected = False
        
    def connect(self):
        """Conecta com o OpenVAS/GVM"""
        if not GVM_AVAILABLE:
            raise ImportError("python-gvm não está instalado. Execute: pip install python-gvm")
            
        try:
            # Criar conexão TLS
            self.connection = TLSConnection(
                hostname=OPENVAS_CONFIG['host'],
                port=OPENVAS_CONFIG['port']
            )
            
            self.connected = True
            print(f"✅ Conexão criada para OpenVAS em {OPENVAS_CONFIG['host']}:{OPENVAS_CONFIG['port']}")
            return True
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
            
    def _execute_gmp_command(self, command_func, retries=3):
        """Executa comando GMP com context manager e retry"""
        if not self.connected:
            raise Exception("Não conectado ao OpenVAS")
            
        last_error = None
        
        for attempt in range(retries):
            try:
                with Gmp(connection=self.connection, transform=EtreeTransform()) as gmp:
                    # Autenticar com timeout
                    gmp.authenticate(
                        OPENVAS_CONFIG['username'], 
                        OPENVAS_CONFIG['password']
                    )
                    return command_func(gmp)
                    
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Verificar se é erro de timeout ou conexão
                if any(keyword in error_msg for keyword in ['timeout', 'connection', 'ssl', 'eof']):
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"⚠️ Erro na tentativa {attempt + 1}: {e}")
                        print(f"🔄 Tentando novamente em {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                        
                raise Exception(f"Erro no comando GMP após {retries} tentativas: {e}")
            
    def create_target(self, name, hosts):
        """Cria um target para scan"""
        def _create_target(gmp):
            response = gmp.create_target(name=name, hosts=[hosts])
            target_id = response.get('id')
            print(f"🎯 Target criado: {name} ({target_id})")
            return target_id
        
        try:
            return self._execute_gmp_command(_create_target)
        except Exception as e:
            print(f"❌ Erro ao criar target: {e}")
            return None
            
    def start_scan(self, target_id, scan_name=None):
        """Inicia um scan"""
        if not scan_name:
            scan_name = f"Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def _start_scan(gmp):
            # Usar configuração padrão "Full and fast"
            config_id = OPENVAS_CONFIG.get('scan_config_id', 'daba56c8-73ec-11df-a475-002264764cea')
            scanner_id = OPENVAS_CONFIG.get('scanner_id', '08b69003-5fc2-4037-a479-93b440211c73')
            
            response = gmp.create_task(
                name=scan_name,
                config_id=config_id,
                target_id=target_id,
                scanner_id=scanner_id
            )
            
            task_id = response.get('id')
            print(f"📋 Task criada: {scan_name} ({task_id})")
            
            # Iniciar scan
            gmp.start_task(task_id)
            print(f"🚀 Scan iniciado: {scan_name}")
            return task_id
            
        try:
            return self._execute_gmp_command(_start_scan)
        except Exception as e:
            print(f"❌ Erro ao iniciar scan: {e}")
            return None
            
    def get_task_status(self, task_id):
        """Verifica o status de uma task"""
        def _get_status(gmp):
            tasks = gmp.get_tasks(filter_string=f"uuid={task_id}")
            if hasattr(tasks, 'xpath'):
                task = tasks.xpath('task')[0] if tasks.xpath('task') else None
                if task:
                    status = task.find('status').text
                    progress = task.find('progress')
                    progress_value = progress.text if progress is not None else "0"
                    return status, progress_value
            return "Unknown", "0"
            
        try:
            return self._execute_gmp_command(_get_status)
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
            return "Error", "0"
            
    def wait_for_completion(self, task_id, max_wait=1800):  # 30 minutos
        """Aguarda o scan completar"""
        start_time = time.time()
        print(f"⏳ Aguardando conclusão do scan {task_id}...")
        
        while time.time() - start_time < max_wait:
            status, progress = self.get_task_status(task_id)
            print(f"📊 Status: {status} | Progresso: {progress}%")
            
            if status in ["Done", "Stopped"]:
                print(f"✅ Scan concluído: {status}")
                return True
            elif status == "Running":
                time.sleep(30)  # Aguarda 30 segundos
            else:
                print(f"⚠️ Status inesperado: {status}")
                time.sleep(30)
        
        print("⏰ Timeout aguardando conclusão do scan")
        return False
        
    def get_scan_results(self, task_id):
        """Obtém os resultados do scan"""
        def _get_results(gmp):
            # Obter IDs dos relatórios
            tasks = gmp.get_tasks(filter_string=f"uuid={task_id}")
            if not hasattr(tasks, 'xpath') or not tasks.xpath('task'):
                return []
                
            task = tasks.xpath('task')[0]
            reports = task.xpath('.//report')
            
            if not reports:
                return []
            
            # Pegar último relatório
            report_id = reports[-1].get('id')
            report = gmp.get_report(report_id=report_id)
            
            vulnerabilities = []
            
            # Processar resultados
            if hasattr(report, 'xpath'):
                results = report.xpath('.//result')
                for result in results:
                    try:
                        host_elem = result.find('host')
                        nvt_elem = result.find('nvt')
                        severity_elem = result.find('severity')
                        
                        if all([host_elem is not None, nvt_elem is not None, severity_elem is not None]):
                            vuln = {
                                'id': nvt_elem.get('oid', 'Unknown'),
                                'name': nvt_elem.find('name').text if nvt_elem.find('name') is not None else 'Unknown',
                                'host': host_elem.text,
                                'severity': float(severity_elem.text) if severity_elem.text else 0.0,
                                'description': result.find('description').text if result.find('description') is not None else 'N/A'
                            }
                            vulnerabilities.append(vuln)
                    except Exception as e:
                        print(f"⚠️ Erro ao processar resultado: {e}")
                        continue
            
            print(f"📋 Processados {len(vulnerabilities)} resultados")
            return vulnerabilities
            
        try:
            return self._execute_gmp_command(_get_results)
        except Exception as e:
            print(f"❌ Erro ao obter resultados: {e}")
            return []
            
    def execute_full_scan(self, hosts=None):
        """Executa um scan completo"""
        if not hosts:
            hosts = OPENVAS_CONFIG['target_hosts']
            
        print(f"🎯 Iniciando scan completo para: {hosts}")
        
        # Conectar
        if not self.connect():
            return []
        
        try:
            # Criar target
            target_name = f"AutoTarget_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            target_id = self.create_target(target_name, hosts)
            
            if not target_id:
                return []
            
            # Iniciar scan
            task_id = self.start_scan(target_id)
            
            if not task_id:
                return []
            
            # Aguardar conclusão
            if self.wait_for_completion(task_id):
                # Obter resultados
                results = self.get_scan_results(task_id)
                print(f"✅ Scan concluído: {len(results)} vulnerabilidades encontradas")
                return results
            else:
                print("❌ Scan não foi concluído no tempo esperado")
                return []
                
        except Exception as e:
            print(f"❌ Erro durante scan: {e}")
            return []
        finally:
            self.disconnect()

# Função de conveniência para executar scan rapidamente
def quick_scan(hosts=None):
    """Executa um scan rápido"""
    connector = OpenVASConnector()
    return connector.execute_full_scan(hosts)

def test_connection():
    """Testa a conexão com OpenVAS"""
    print("🧪 Testando conexão com OpenVAS...")
    
    connector = OpenVASConnector()
    
    if connector.connect():
        def _test_auth(gmp):
            version = gmp.get_version()
            return version.get('version', 'Unknown')
        
        try:
            version = connector._execute_gmp_command(_test_auth)
            print(f"✅ OpenVAS conectado! Versão: {version}")
            return True
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return False
        finally:
            connector.disconnect()
    else:
        return False

if __name__ == "__main__":
    # Teste de conexão
    if test_connection():
        print("🎉 OpenVAS está funcionando!")
    else:
        print("❌ Problema na conexão com OpenVAS")