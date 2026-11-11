"""Auditoría independiente de Databel; no depende del motor de Power BI."""
from pathlib import Path
import argparse, csv, hashlib, json
from collections import Counter
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://assets.datacamp.com/production/repositories/5993/datasets/d6a32ec1293e10bd44441b4f8b4fe60b9776e0d1/Databel%20-%20Data.csv'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=Path, default=ROOT/'data/Databel - Data.csv')
    args = parser.parse_args()
    data = pd.read_csv(args.csv)
    out = ROOT/'output'; out.mkdir(exist_ok=True)
    assert data['Customer ID'].is_unique
    assert set(data['Churn Label']) == {'Yes', 'No'}
    data['Abandono'] = data['Churn Label'].eq('Yes').astype(int)
    data['Grupo de edad'] = pd.cut(data['Age'], [0, 29, 64, float('inf')], labels=['Menores de 30', '30 a 64', '65 o más'], right=True)
    data['Categoria de abandono'] = data['Churn Category'].fillna('Sin motivo informado')
    data.loc[data['Abandono'].eq(0), 'Categoria de abandono'] = 'No aplica'
    data['Motivo de abandono'] = data['Churn Reason'].fillna('Sin motivo informado')
    churn = data.loc[data['Abandono'].eq(1)]
    with args.csv.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    independent = Counter(row['Churn Label'] for row in rows)
    assert len(rows) == len(data) and independent['Yes'] == int(data['Abandono'].sum())
    stats = {
        'source': URL, 'sha256': hashlib.sha256(args.csv.read_bytes()).hexdigest(),
        'rows': len(data), 'original_columns': len(pd.read_csv(args.csv, nrows=0).columns),
        'unique_customers': data['Customer ID'].nunique(), 'churned': len(churn),
        'retained': len(data)-len(churn), 'churn_rate': len(churn)/len(data),
        'duplicate_rows': int(pd.read_csv(args.csv).duplicated().sum()),
        'churned_missing_reason': int(churn['Churn Reason'].isna().sum()),
        'churned_missing_category': int(churn['Churn Category'].isna().sum()),
        'independent_csv_check': True, 'nulls': pd.read_csv(args.csv).isna().sum().to_dict(),
    }
    dimensions = ['Contract Type','Payment Method','Grupo de edad','State','Group','Intl Plan','Intl Active','Unlimited Data Plan','Customer Service Calls','Number of Customers in Group']
    for dim in dimensions:
        g = data.groupby(dim, observed=True, dropna=False)['Abandono'].agg(clientes='size',bajas='sum').reset_index()
        g['tasa_abandono'] = g['bajas']/g['clientes']
        assert int(g['clientes'].sum()) == len(data) and int(g['bajas'].sum()) == len(churn)
        slug = dim.lower().replace(' ','_')
        g.to_csv(out/f'{slug}.csv', index=False)
    for dim, name in [('Categoria de abandono','motivos_categoria'),('Motivo de abandono','motivos_detalle')]:
        g = churn.groupby(dim).size().rename('bajas').sort_values(ascending=False).reset_index()
        g['porcentaje_de_bajas'] = g['bajas']/len(churn)
        assert int(g['bajas'].sum()) == len(churn)
        g.to_csv(out/f'{name}.csv', index=False)
    plans = data.groupby(['Intl Active','Intl Plan'],dropna=False)['Abandono'].agg(clientes='size',bajas='sum').reset_index()
    plans['tasa_abandono'] = plans['bajas']/plans['clientes']
    plans.to_csv(out/'plan_internacional_cruce.csv',index=False)
    (out/'metricas.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
