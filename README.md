# Sistema de Automação de Vulnerabilidades

Sistema híbrido para aprendizado e uso real de automação de vulnerabilidades com OpenVAS.

## O que faz

1. **Scan** - Dados simulados (aprendizado) ou OpenVAS real (produção)
2. **Análise** - Usa pandas para analisar severidade  
3. **Relatório** - Gera CSV com resultados
4. **Alerta** - Envia email ou mostra no console

## Modos de operação

### 🧪 Development (Padrão)
- Usa dados simulados para aprendizado
- Não precisa OpenVAS instalado
- Ideal para estudar automação

### 🚀 Production  
- Conecta com OpenVAS/GVM real
- Executa scans reais na rede
- Requer OpenVAS configurado

## Estrutura do projeto

```
OpenVAS/
├── main.py                    # Sistema principal
├── requirements.txt           # Dependências
│
├── alerting/
│   ├── alert_console.py      # Alertas por email/console
│   ├── email_config.py       # Configurações (email + OpenVAS)
│   └── setup_email.py        # Setup de email
│
├── processing/  
│   └── vuln_analysis.py      # Análise com pandas
│
├── scanner/
│   ├── openvas_scan.py       # Scanner híbrido
│   ├── openvas_connector.py  # Conexão real com OpenVAS
│   └── setup_openvas.py      # Configuração do OpenVAS
│
└── reports/
    └── report.csv             # Relatórios gerados
```

## Como usar

### 1. Execução imediata (modo básico)
```bash
# Funciona imediatamente - sem configuração!
python main.py
```

### 2. Instalar dependências (para recursos avançados)
```bash
# Dependências básicas
pip install pandas

# Para conexão real com OpenVAS
pip install python-gvm lxml requests
```

### 3. Configurar email (opcional)
```bash
python alerting/setup_email.py
```

### 4. Configurar OpenVAS real (opcional)
```bash
python scanner/setup_openvas.py
```

### 5. Comandos disponíveis
```bash
# Sistema completo
python main.py

# Análise rápida (apenas críticas)  
python main.py --quick
```

### 6. Resultados
- **Com vulnerabilidades críticas**: recebe email automaticamente (se configurado)
- **Sistema seguro**: apenas log no console  
- **Relatório**: sempre salvo em `reports/report.csv`

## Configuração

### Zero-config (padrão)
O sistema funciona **imediatamente** sem configuração:
```bash
python main.py  # Funciona na primeira execução!
```

### Email (opcional)
```bash
# Configuração automática
python alerting/setup_email.py

# Ou manual no arquivo .env
SMTP_SERVER=smtp.gmail.com
EMAIL_ADDRESS=seu-email@gmail.com  
EMAIL_PASSWORD=sua-senha-app
EMAIL_DESTINATION=destinatario@empresa.com
```

### OpenVAS Real (opcional)
```bash
# Configuração automática
python scanner/setup_openvas.py

# Ou manual no arquivo .env
OPENVAS_HOST=localhost
OPENVAS_PORT=9392
OPENVAS_USERNAME=admin
OPENVAS_PASSWORD=sua-senha-openvas
MODE=production
```

### Provedores de email suportados
- **Gmail**: Requer senha de app (2FA ativo)
- **Outlook/Hotmail**: Senha normal
- **Yahoo**: Senha de app
- **Outros**: Configuração manual de SMTP

## Configuração do OpenVAS Real

### Pré-requisitos
- **Docker Desktop instalado**
- **4GB RAM livre**  
- **20-30 minutos** para primeira inicialização

### Instalação
```bash
# Executar OpenVAS
docker run -d -p 9392:9392 --name openvas securecompliance/gvm

# Verificar progresso
docker logs openvas -f

# Configurar conexão
python scanner/setup_openvas.py
```

**⏰ Primeira inicialização demora 20-30 min** (baixa definições CVE)

### Verificar se está pronto
```bash
# Testar interface web
python -c "import requests; print(requests.get('http://localhost:9392').status_code)"
```

## Dicas

- ✅ **Comece** com `python main.py` (funciona sem configuração)
- 📧 **Email opcional** - sistema funciona perfeitamente sem
- 🐳 **OpenVAS opcional** - dados simulados são ótimos para aprender
- ⏰ **Seja paciente** - OpenVAS demora 20-30 min para inicializar

## Para desenvolvedores

### Customização
- **Limite crítico**: `CRITICAL_THRESHOLD` em `vuln_analysis.py`
- **Dados simulados**: `get_simulated_vulnerabilities()` em `openvas_scan.py`
- **Email templates**: `_send_email()` em `alert_console.py`
- **Targets**: `TARGET_HOSTS` no `.env`

### Arquitetura
```
main.py → Scanner → Análise → Relatório → Alertas
```

### Estrutura de dados
```python
{
    "name": "CVE-2023-1234 - SQL Injection", 
    "host": "192.168.1.10",
    "severity": 8.5
}
```

## Segurança

- Dados sensíveis ficam em `.env` (não versionado)
- Templates e código são seguros para GitHub
- Cada desenvolvedor configura suas próprias credenciais
