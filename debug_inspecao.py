import pandas as pd
from pathlib import Path
import warnings
warnings.simplefilter('ignore')

files = [Path('Arquivos/julio-tabela de vencimento.xls'), Path('Arquivos/julio-tabela de vencimento.xlsx')]
for f in files:
    if f.exists():
        print('FILE:', f)
        try:
            if f.suffix.lower() == '.xls':
                df = pd.read_html(str(f))
                df = df[0]
            else:
                df = pd.read_excel(str(f))
            print('  cols:', list(df.columns))
            print('  head:')
            print(df.head(5).to_string())
        except Exception as e:
            print('  ERROR', repr(e))

print('--- PAGAMENTO ---')
for f in [Path('Arquivos/PAGAMENTO_COM_CARGO 10004.xlsx'), Path('Arquivos/ppgg.xlsx')]:
    if f.exists():
        print('FILE:', f)
        try:
            df = pd.read_excel(str(f))
            print('  cols:', list(df.columns))
            print('  head:')
            print(df.head(5).to_string())
        except Exception as e:
            print('  ERROR', repr(e))
