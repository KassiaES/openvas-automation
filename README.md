# Sistema de Automação de Vulnerabilidades

Sistema simples para aprendizado de automação de vulnerabilidades e alertas por email.

## O que faz

1. **Scan** - Simula busca de vulnerabilidades (dados fake para aprendizado)
2. **Análise** - Usa pandas para analisar severidade  
3. **Relatório** - Gera CSV com resultados
4. **Alerta** - Envia email ou mostra no console

## Estrutura do projeto

```
OpenVAS/
├── main.py                    # Sistema principal
├── requirements.txt           # Dependências
│
├── alerting/
│   ├── alert_console.py      # Alertas por email/console
│   ├── email_config.py       # Configuração de email
│   └── setup_email.py        # Setup universal de email
│
├── processing/  
│   └── vuln_analysis.py      # Análise com pandas
│
├── scanner/
│   └── openvas_scan.py       # Simulação de scan
│
└── reports/
    └── report.csv             # Relatórios gerados
```

## Como usar

### 1. Instalar dependências
```bash
pip install pandas
```

### 2. Configurar email (opcional)
```bash
python alerting/setup_email.py
```
Suporta Gmail, Outlook, Yahoo e outros provedores.

### 3. Executar sistema
```bash
python main.py
```

### 4. Ver resultados
- **Com vulnerabilidades críticas**: recebe email automaticamente
- **Sistema seguro**: apenas log no console
- **Relatório**: sempre salvo em `reports/report.csv`

## Configuração de email

### Automática (recomendado)
Execute `python alerting/setup_email.py` e siga as instruções.

### Manual
1. Copie `.env.template` para `.env`
2. Configure com seus dados:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_ADDRESS=seu-email@gmail.com
   EMAIL_PASSWORD=sua-senha-app
   EMAIL_DESTINATION=destinatario@empresa.com
   ```

### Provedores suportados
- **Gmail**: Requer senha de app (2FA ativo)
- **Outlook/Hotmail**: Senha normal
- **Yahoo**: Senha de app
- **Outros**: Configuração manual de SMTP

## Para desenvolvedores

### Classificação de severidade
- **9.0-10.0**: Crítica - Alerta por email
- **7.0-8.9**: Alta
- **4.0-6.9**: Média  
- **0.1-3.9**: Baixa

### Estrutura de dados
```python
{
    "id": "vuln_001",
    "name": "CVE-2023-1234 - SQL Injection",
    "host": "192.168.1.10",
    "port": "tcp/80", 
    "severity": 8.5,
    "description": "Descrição da vulnerabilidade"
}
```

### Customização
- **Limite crítico**: Altere `CRITICAL_THRESHOLD` em `vuln_analysis.py`
- **Dados de teste**: Modifique `fake_vulnerabilities` em `openvas_scan.py`
- **Templates de email**: Edite `alert_console.py`

## Segurança

- Dados sensíveis ficam em `.env` (não versionado)
- Templates e código são seguros para GitHub
- Cada desenvolvedor configura suas próprias credenciais
