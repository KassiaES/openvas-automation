"""
Sistema Principal
Orquestra: Scan → Análise → Relatório → Alerta
"""

from scanner.openvas_scan import load_scan_results
from processing.vuln_analysis import analyze_vulns, get_stats
from alerting.alert_console import send_alert, send_summary_alert


def main():

    print("🔒 Sistema de Automação de Vulnerabilidades - Versão Simples")
    print("=" * 60)
    
    # SCANNER - Carregar vulnerabilidades
    print("1️⃣ Executando scan de vulnerabilidades...")
    vulns = load_scan_results()
    
    # ANÁLISE - Processar dados  
    print("\n2️⃣ Analisando dados...")
    df, critical = analyze_vulns(vulns)
    
    # RELATÓRIO - Gerar CSV
    print("\n3️⃣ Gerando relatório...")
    try:
        df.to_csv("reports/report.csv", index=False)
        print("✅ Relatório CSV salvo em: reports/report.csv")
    except Exception as e:
        print(f"❌ Erro ao salvar relatório: {e}")
    
    # ALERTAS - Notificar sobre vulnerabilidades críticas
    print("\n4️⃣ Enviando alertas...")
    send_alert(critical)
    
    # RESUMO - Estatísticas gerais
    print("\n5️⃣ Resumo estatístico...")
    stats = get_stats(df)
    send_summary_alert(stats)
    
    print("\n✅ Pipeline concluído com sucesso!")
    return True


def quick_analysis():

    print("⚡ ANÁLISE RÁPIDA - Apenas vulnerabilidades críticas")
    print("=" * 50)
    
    vulns = load_scan_results()
    df, critical = analyze_vulns(vulns)
    
    if not critical.empty:
        print("\n🚨 VULNERABILIDADES CRÍTICAS ENCONTRADAS:")
        print(critical[['name', 'host', 'severity', 'description']])
        print(f"\n📊 Total: {len(critical)} vulnerabilidades críticas")
    else:
        print("\n✅ Nenhuma vulnerabilidade crítica encontrada!")
    
    return critical


if __name__ == "__main__":
    import sys
    import os
    
    # Criar diretório de reports se não existir
    os.makedirs("reports", exist_ok=True)
    
    # Verificar se foi solicitada análise rápida
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_analysis()
    else:
        main()