"""
Análise de Vulnerabilidades
Usa pandas para analisar dados de vulnerabilidades
"""

import pandas as pd

# Limite para considerar vulnerabilidade crítica
CRITICAL_THRESHOLD = 7.0


def analyze_vulns(vulns):
    """
    Analisa vulnerabilidades usando pandas
    
    Args:
        vulns: Lista de vulnerabilidades
        
    Returns:
        tuple: (dataframe_completo, vulnerabilidades_criticas)
    """
    print("📊 Analisando vulnerabilidades...")
    
    # Converter para DataFrame
    df = pd.DataFrame(vulns)
    
    # Filtrar vulnerabilidades críticas
    critical = df[df["severity"] >= CRITICAL_THRESHOLD]
    
    # Estatísticas simples
    print(f"Total de vulnerabilidades: {len(df)}")
    print(f"Vulnerabilidades críticas (>= {CRITICAL_THRESHOLD}): {len(critical)}")
    
    if len(df) > 0:
        print(f"Severidade média: {df['severity'].mean():.1f}")
        print(f"Severidade máxima: {df['severity'].max():.1f}")
    
    return df, critical


def get_stats(df):
    """
    Obtém estatísticas básicas do DataFrame
    """
    if df.empty:
        return {}
    
    stats = {
        'total': len(df),
        'critical_count': len(df[df["severity"] >= 9.0]),
        'high_count': len(df[df["severity"] >= 7.0]),
        'medium_count': len(df[(df["severity"] >= 4.0) & (df["severity"] < 7.0)]),
        'low_count': len(df[df["severity"] < 4.0]),
        'avg_severity': df['severity'].mean(),
        'max_severity': df['severity'].max(),
        'hosts_affected': df['host'].nunique()
    }
    
    return stats


if __name__ == "__main__":

    from scanner.openvas_scan import load_scan_results
    
    vulns = load_scan_results()
    df, critical = analyze_vulns(vulns)
    
    print("\n📈 Estatísticas:")
    stats = get_stats(df)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🚨 Vulnerabilidades críticas:")
    if not critical.empty:
        print(critical[['name', 'host', 'severity']])
    else:
        print("  Nenhuma vulnerabilidade crítica encontrada!")