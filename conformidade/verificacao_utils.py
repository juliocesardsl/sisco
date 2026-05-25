"""Lógica de verificação de conformidade - refatorada do exemplo.py para Django"""
from typing import Dict, List, Tuple
import re
import unicodedata
import logging
import sys
import datetime
from io import BytesIO

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def debug_print(msg):
    """Print com flush garantido para aparecer no console Django"""
    print(msg)
    sys.stdout.flush()


def flatten_and_clean_columns(df):
    """Limpa headers multilinhas/complexos para strings simples"""
    df.columns = [
        ' '.join(
            str(col).split() if isinstance(col, str) else [str(col)]
        ).strip() if col != '' else f'Unnamed_{i}'
        for i, col in enumerate(df.columns)
    ]
    return df


def _repair_mojibake(s):
    """Tenta corrigir cabeçalhos corrompidos por codificação Latin1/UTF-8."""
    if not isinstance(s, str):
        return s
    if 'Ã' in s or 'Â' in s:
        try:
            return s.encode('latin1').decode('utf-8')
        except Exception:
            return s
    return s

STATUS_DESCRIPTION_MAP = {
    '1': '1 - INCLUÍDO NO MÊS',
    '2': '2 - NORMAL',
    '3': '3 - AFASTADO',
    '4': '4 - DESLIGADO NO MÊS',
    '8': '8 - CEDIDO',
}


def normalize_status_description(value):
    """Mapeia código numérico para descrição de status e mantém texto original se já estiver presente."""
    if value is None:
        return ''

    if isinstance(value, float) and value.is_integer():
        value = str(int(value))
    s = str(value).strip()
    if s == '':
        return ''

    match = re.match(r'^\s*(\d+)\s*(?:-|–)?\s*(.*)$', s)
    if match:
        code = match.group(1)
        if code in STATUS_DESCRIPTION_MAP:
            return STATUS_DESCRIPTION_MAP[code]
        return s

    cleaned = re.sub(r'\.0+$', '', s)
    if cleaned.isdigit() and cleaned in STATUS_DESCRIPTION_MAP:
        return STATUS_DESCRIPTION_MAP[cleaned]

    return s


def extract_status_code(value):
    """Extrai apenas o número do status, preservando texto se não houver número."""
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    s = str(value).strip()
    if s == '':
        return ''
    match = re.match(r'^\s*(\d+)\b', s)
    if match:
        return match.group(1)
    return s


def normalize(s):
    """Normaliza string removendo acentos, espaços extras"""
    if not isinstance(s, str):
        return ""
    s = _repair_mojibake(s)
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    return s


def format_raw_value(value):
    """Preserva valores brutos do Excel sem modificar o formato sempre que possível."""
    if value is None:
        return ''
    try:
        import pandas as pd
        if pd.isna(value):
            return ''
    except Exception:
        pass

    if isinstance(value, datetime.datetime):
        if value.time() == datetime.time(0, 0):
            return value.strftime('%d/%m/%Y')
        return value.strftime('%d/%m/%Y %H:%M:%S')

    if isinstance(value, datetime.date):
        return value.strftime('%d/%m/%Y')

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value).strip()


def _column_tokens(col):
    """Converte o nome da coluna em tokens normalizados para comparação flexível."""
    normalized = normalize(col)
    return set(token for token in re.sub(r'[^a-z0-9]+', ' ', normalized).split() if token)


COLUMN_ALIASES = {
    'ano': {'ano', 'anorefer'},
    'referencia': {'referencia', 'refer', 'ref', 'anorefer'},
    'ref': {'ref', 'refer', 'referencia', 'anorefer'},
    'mes': {'mes', 'mesrefer', 'mês'},
    'carga': {'carga', 'cargahoraria', 'ch'},
    'horaria': {'horaria', 'horario', 'cargahoraria'},
    'valor': {'valor', 'vl', 'vlrubrica'},
    'nome': {'nome', 'nomecompleto', 'nomedo'},
    'servidor': {'servidor', 'nome', 'nomecompleto', 'nomedo'},
    'descricao': {'descricao', 'descrio', 'desc'},
    'desc': {'desc', 'descricao', 'descrio', 'rubrica'},
    'prov': {'prov', 'rubrica', 'desc', 'provdesc', 'idprovdesc', 'cdprovdesc'},
    'empresa': {'empresa', 'emp'},
    'matricula': {'matricula', 'matr'},
    'orgao': {'orgao', 'orga', 'org', 'unidade', 'lotacao', 'lotac'},
    'cpf': {'cpf', 'documento', 'cpfdocumento'},
    'cargo': {'cargo'},
    'funcional': {'funcional', 'funcao'},
    'status': {'status', 'dcstatus'},
    'frequencia': {'frequencia'},
    'situacao': {'situacao', 'situacaofuncional'},
    'data': {'data', 'datadevigencia'},
    'vigencia': {'vigencia', 'vigencia', 'vigencia'},
}


def _matches_word(col_norm, col_clean, col_tokens, word):
    aliases = COLUMN_ALIASES.get(word, {word})
    return (
        word in col_norm
        or word in col_clean
        or any(alias in col_tokens for alias in aliases)
    )


def find_by_words(df, words, debug=False):
    """Encontra coluna que contém todas as palavras, aceitando aliases do formato novo."""
    words = [normalize(w) for w in words]

    if debug:
        print(f"  [DEBUG find_by_words] Procurando: {words}")

    # Prioridade: manter compatibilidade com o cabeçalho clássico "PROV/DESC"
    if any(w in ['prov', 'desc'] for w in words):
        if 'PROV/DESC' in df.columns:
            if debug:
                print(f"  [DEBUG] Coluna 'PROV/DESC' encontrada (prioritária)")
            return 'PROV/DESC'

    for col in df.columns:
        col_norm = normalize(col)
        col_clean = ''.join(c for c in col_norm if c.isalnum())
        col_tokens = _column_tokens(col)
        if all(_matches_word(col_norm, col_clean, col_tokens, w) for w in words):
            if debug:
                print(f"  [DEBUG] Match flexível encontrado: '{col}'")
            return col

    if len(words) == 1:
        word = words[0]
        for col in df.columns:
            col_norm = normalize(col)
            col_clean = ''.join(c for c in col_norm if c.isalnum())
            col_tokens = _column_tokens(col)
            if _matches_word(col_norm, col_clean, col_tokens, word):
                if debug:
                    print(f"  [DEBUG] Match por palavra única encontrado: '{col}'")
                return col

    if debug:
        print(f"  [DEBUG] Nenhuma coluna encontrada!")
    return None


def _read_uploaded_excel(file):
    import pandas as pd

    if hasattr(file, 'temporary_file_path'):
        return read_excel_flexible(file.temporary_file_path())

    content = file.read()
    try:
        file.seek(0)
    except Exception:
        pass

    try:
        return pd.read_excel(BytesIO(content))
    except Exception:
        # Fallback to the flexible reader that can detect HTML / engine issues
        return read_excel_flexible(BytesIO(content))


def _normalize_value_column(series):
    import pandas as pd
    import numpy as np

    def parse_value(val):
        if pd.isna(val) or val == '' or str(val).strip() == '':
            return 0.0

        # Se já é numérico, retornar diretamente
        if isinstance(val, (int, float)):
            return float(val)

        # Converter para string e limpar espaços
        s = str(val).strip()

        # Remover caracteres de moeda comuns
        s = s.replace('R$', '').replace('$', '').replace('€', '').replace('£', '').strip()

        # Tentar conversão direta primeiro
        try:
            # Substituir vírgula por ponto se for formato brasileiro simples
            if ',' in s and s.count(',') == 1 and '.' not in s:
                return float(s.replace(',', '.'))
            # Formato americano
            elif '.' in s and ',' not in s:
                return float(s)
            # Formato com milhares brasileiro: 1.234,56
            elif ',' in s and '.' in s:
                # Verificar se é formato brasileiro com separador de milhares
                parts = s.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Remover pontos dos milhares
                    integer_part = parts[0].replace('.', '')
                    return float(f"{integer_part}.{parts[1]}")
        except ValueError:
            pass

        # Método alternativo: extrair apenas dígitos e pontuar
        digits = ''.join(c for c in s if c.isdigit())
        if not digits:
            return 0.0

        # Se tem exatamente 2 dígitos, assumir que é centavos: 00 -> 0.00
        if len(digits) == 2:
            return float(f"0.{digits}")
        # Se tem mais, assumir que os últimos 2 são centavos
        elif len(digits) > 2:
            return float(f"{digits[:-2]}.{digits[-2:]}")
        else:
            return float(digits)

    return series.apply(parse_value)


def _parse_extrator_for_rubrica(file, rubrica):
    import pandas as pd

    df_extrator = _read_uploaded_excel(file)
    df_extrator = flatten_and_clean_columns(df_extrator)

    col_prov = find_by_words(df_extrator, ['prov', 'desc'])
    if not col_prov:
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if any(term in col_norm for term in ['prov', 'desc', 'rubrica', 'ar', 'funcao']):
                col_prov = col
                break

    col_empresa = (find_by_words(df_extrator, ['empresa']) or 
                   find_by_words(df_extrator, ['cod', 'empresa']) or 
                   find_by_words(df_extrator, ['codigo', 'empresa']) or
                   find_by_words(df_extrator, ['cod_empresa']) or
                   find_by_words(df_extrator, ['código']))
    col_cargo = (find_by_words(df_extrator, ['cargo']) or
                 find_by_words(df_extrator, ['funcao']) or
                 find_by_words(df_extrator, ['cbo']) or
                 find_by_words(df_extrator, ['referencia']))
    if not col_cargo:
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if any(term in col_norm for term in ['cargo', 'funcao', 'cbo', 'referencia', 'cargo']):
                col_cargo = col
                break

    col_matricula = (find_by_words(df_extrator, ['matricula']) or
                     find_by_words(df_extrator, ['matr']) or
                     find_by_words(df_extrator, ['mat']))
    if not col_matricula:
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if any(term in col_norm for term in ['matricula', 'matr', 'mat']):
                col_matricula = col
                break

    col_valor_extrator = find_by_words(df_extrator, ['valor'])
    if not col_valor_extrator:
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if 'valor' in col_norm:
                col_valor_extrator = col
                break

    if not col_prov or not col_empresa or not col_cargo or not col_matricula or not col_valor_extrator:
        faltantes = []
        if not col_prov:
            faltantes.append('PROV/DESC')
        if not col_empresa:
            faltantes.append('EMPRESA')
        if not col_cargo:
            faltantes.append('CARGO')
        if not col_matricula:
            faltantes.append('MATRICULA')
        if not col_valor_extrator:
            faltantes.append('VALOR')
        raise Exception(f"Colunas obrigatórias não encontradas no EXTRATOR: {', '.join(faltantes)}\nColunas disponíveis: {df_extrator.columns.tolist()}")

    df_extrator[col_valor_extrator] = _normalize_value_column(df_extrator[col_valor_extrator])

    # Tentar diferentes formas de filtrar a rubrica
    rubrica_str = str(rubrica).strip()

    # Primeiro tentar filtro exato
    filtro = df_extrator[col_prov].astype(str).str.strip() == rubrica_str
    df_filtrado = df_extrator[filtro].copy()

    # Se não encontrou, tentar filtro por contém
    if df_filtrado.empty:
        filtro = df_extrator[col_prov].astype(str).str.contains(rubrica_str, case=False, na=False)
        df_filtrado = df_extrator[filtro].copy()

    # Se ainda não encontrou, tentar apenas com números (código da rubrica)
    if df_filtrado.empty and rubrica_str.isdigit():
        filtro = df_extrator[col_prov].astype(str).str.contains(r'\b' + rubrica_str + r'\b', case=False, na=False)
        df_filtrado = df_extrator[filtro].copy()

    if df_filtrado.empty:
        raise Exception(f"Rubrica '{rubrica_str}' não encontrada no arquivo de extrator informado.\nValores disponíveis na coluna {col_prov}: {df_extrator[col_prov].unique().tolist()[:20]}")

    group_cols = [col_empresa, col_matricula]
    resumo = df_filtrado.groupby(group_cols, dropna=False, as_index=False)[col_valor_extrator].mean()
    resumo = resumo.rename(columns={col_empresa: 'empresa', col_matricula: 'matricula', col_valor_extrator: 'valor'})
    resumo['empresa'] = resumo['empresa'].astype(str).str.strip().str.zfill(3)
    resumo['matricula'] = resumo['matricula'].astype(str).str.strip()

    return resumo


def _parse_extrator_for_rubrica_detailed(file, rubrica):
    import pandas as pd

    df_extrator = _read_uploaded_excel(file)
    df_extrator = flatten_and_clean_columns(df_extrator)

    col_prov = find_by_words(df_extrator, ['prov', 'desc'])
    if not col_prov:
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if any(term in col_norm for term in ['rubrica', 'ar', 'funcao', 'prov', 'desc']):
                col_prov = col
                break

    col_empresa = (find_by_words(df_extrator, ['empresa']) or 
                   find_by_words(df_extrator, ['cod', 'empresa']) or 
                   find_by_words(df_extrator, ['codigo', 'empresa']) or
                   find_by_words(df_extrator, ['cod_empresa']) or
                   find_by_words(df_extrator, ['código']))
    col_matricula = find_by_words(df_extrator, ['matricula', 'matrícula'])
    col_valor_extrator = find_by_words(df_extrator, ['valor'])

    # Additional detail columns
    col_nome_servidor = find_by_words(df_extrator, ['nome', 'servidor'])
    col_cpf = find_by_words(df_extrator, ['cpf']) or find_by_words(df_extrator, ['documento']) or find_by_words(df_extrator, ['cpf/documento'])
    col_situacao_funcional = find_by_words(df_extrator, ['situacao', 'funcional']) or find_by_words(df_extrator, ['situação', 'funcional'])
    col_status = find_by_words(df_extrator, ['status'])
    col_descricao_status = find_by_words(df_extrator, ['DESCRIÃ‡ÃƒO', 'status']) or find_by_words(df_extrator, ['DESCRIÃ‡ÃƒO', 'status'])
    col_cargo = find_by_words(df_extrator, ['cargo'])
    col_descricao_cargo = find_by_words(df_extrator, ['descricao', 'cargo']) or find_by_words(df_extrator, ['descrição', 'cargo'])
    col_data_admissao = find_by_words(df_extrator, ['data', 'admissao']) or find_by_words(df_extrator, ['data', 'admissão'])
    col_data_ingresso_ref_salarial = find_by_words(df_extrator, ['data', 'ingresso', 'referencia', 'salarial']) or find_by_words(df_extrator, ['data', 'ingresso', 'ref', 'salarial'])
    col_data_afastamento = find_by_words(df_extrator, ['data', 'afastamento'])
    col_motivo_afastamento = find_by_words(df_extrator, ['motivo', 'afastamento'])
    col_motivo_desligamento = find_by_words(df_extrator, ['motivo', 'desligamento']) or find_by_words(df_extrator, ['motivo', 'demissão'])
    col_carga_horaria = find_by_words(df_extrator, ['carga', 'horaria'])
    col_carga_horaria_secundaria = find_by_words(df_extrator, ['carga', 'horaria', 'secundaria']) or find_by_words(df_extrator, ['carga', 'horária', 'secundária'])
    col_ref_vertical = find_by_words(df_extrator, ['ref', 'salarial', 'vertical'])
    col_ref_horizontal = find_by_words(df_extrator, ['ref', 'salarial', 'horizontal'])
    col_prov_desc = find_by_words(df_extrator, ['prov', 'desc'])
    col_valor_mes_anterior = (find_by_words(df_extrator, ['valor', 'mes', 'anterior']) or 
                              find_by_words(df_extrator, ['valor', 'mês', 'anterior']) or
                              find_by_words(df_extrator, ['valor', 'anterior']))
    col_valor_mes_atual = (find_by_words(df_extrator, ['valor', 'mes', 'atual']) or 
                           find_by_words(df_extrator, ['valor', 'mês', 'atual']) or
                           find_by_words(df_extrator, ['valor', 'atual']))
    col_valor_vencimento = (find_by_words(df_extrator, ['valor', 'vencimento']) or 
                            find_by_words(df_extrator, ['vencimento']))
    col_valor_total_recebido = (find_by_words(df_extrator, ['valor', 'total', 'recebido']) or
                                find_by_words(df_extrator, ['valor', 'recebido']) or
                                find_by_words(df_extrator, ['total', 'recebido']) or
                                find_by_words(df_extrator, ['recebido']))
    col_frequencia = (find_by_words(df_extrator, ['frequencia']) or 
                      find_by_words(df_extrator, ['frequência']))

    if not col_prov or not col_empresa or not col_matricula or not col_valor_extrator:
        faltantes = []
        if not col_prov:
            faltantes.append('PROV/DESC')
        if not col_empresa:
            faltantes.append('EMPRESA')
        if not col_matricula:
            faltantes.append('MATRICULA')
        if not col_valor_extrator:
            faltantes.append('VALOR')
        raise Exception(f"Colunas obrigatórias não encontradas no EXTRATOR: {', '.join(faltantes)}")

    df_extrator[col_valor_extrator] = _normalize_value_column(df_extrator[col_valor_extrator])

    rubrica_str = str(rubrica).strip()
    filtro = df_extrator[col_prov].astype(str).str.strip() == rubrica_str
    df_filtrado = df_extrator[filtro].copy()
    if df_filtrado.empty:
        df_filtrado = df_extrator[df_extrator[col_prov].astype(str).str.contains(rubrica_str, case=False, na=False)].copy()
    if df_filtrado.empty:
        raise Exception(f"Rubrica '{rubrica_str}' não encontrada no arquivo de extrator informado.")

    def make_column(col_name, default=''):
        if col_name and col_name in df_filtrado.columns:
            return df_filtrado[col_name].apply(format_raw_value)
        return pd.Series([default] * len(df_filtrado), index=df_filtrado.index)

    df_filtrado['empresa'] = df_filtrado[col_empresa].astype(str).str.strip().replace('.0', '', regex=False)
    df_filtrado['matricula'] = df_filtrado[col_matricula].astype(str).str.strip().replace('.0', '', regex=False)
    df_filtrado['valor'] = df_filtrado[col_valor_extrator]
    df_filtrado['nome_servidor'] = make_column(col_nome_servidor)
    df_filtrado['cpf'] = make_column(col_cpf)
    df_filtrado['situacao_funcional'] = make_column(col_situacao_funcional)
    df_filtrado['status_servidor'] = make_column(col_status).apply(extract_status_code)
    df_filtrado['descricao_status'] = make_column(col_descricao_status).apply(normalize_status_description)
    df_filtrado['cargo'] = make_column(col_cargo)
    df_filtrado['descricao_cargo'] = make_column(col_descricao_cargo)
    df_filtrado['descricao_status'] = df_filtrado['descricao_status'].where(
        df_filtrado['descricao_status'] != '',
        df_filtrado['status_servidor'].apply(normalize_status_description)
    )
    df_filtrado['data_admissao'] = make_column(col_data_admissao)
    df_filtrado['data_ingresso_ref_salarial'] = make_column(col_data_ingresso_ref_salarial)
    df_filtrado['data_afastamento'] = make_column(col_data_afastamento)
    df_filtrado['motivo_afastamento'] = make_column(col_motivo_afastamento)
    df_filtrado['motivo_desligamento'] = make_column(col_motivo_desligamento)
    df_filtrado['carga_horaria'] = make_column(col_carga_horaria)
    df_filtrado['carga_horaria_secundaria'] = make_column(col_carga_horaria_secundaria)
    df_filtrado['ref_vertical'] = make_column(col_ref_vertical)
    df_filtrado['ref_horizontal'] = make_column(col_ref_horizontal)
    df_filtrado['prov_desc'] = make_column(col_prov_desc)
    df_filtrado['valor_mes_anterior'] = make_column(col_valor_mes_anterior)
    df_filtrado['valor_mes_atual'] = make_column(col_valor_mes_atual)
    df_filtrado['valor_vencimento'] = make_column(col_valor_vencimento)
    df_filtrado['valor_total_recebido'] = make_column(col_valor_total_recebido)
    df_filtrado['frequencia'] = make_column(col_frequencia)

    campos_agregacao = {
        'valor': 'mean',
        'nome_servidor': 'first',
        'cpf': 'first',
        'situacao_funcional': 'first',
        'status_servidor': 'first',
        'descricao_status': 'first',
        'cargo': 'first',
        'descricao_cargo': 'first',
        'data_admissao': 'first',
        'data_ingresso_ref_salarial': 'first',
        'data_afastamento': 'first',
        'motivo_afastamento': 'first',
        'motivo_desligamento': 'first',
        'carga_horaria': 'first',
        'carga_horaria_secundaria': 'first',
        'ref_vertical': 'first',
        'ref_horizontal': 'first',
        'prov_desc': 'first',
        'valor_mes_anterior': 'first',
        'valor_mes_atual': 'first',
        'valor_vencimento': 'first',
        'valor_total_recebido': 'first',
        'frequencia': 'first',
    }

    resumo = df_filtrado.groupby(['empresa', 'matricula'], dropna=False, as_index=False).agg(campos_agregacao)
    resumo['empresa'] = resumo['empresa'].astype(str).str.strip().str.zfill(3)
    resumo['matricula'] = resumo['matricula'].astype(str).str.strip()
    return resumo


def comparar_extrator_por_mes(file_anterior, file_atual, rubrica):
    try:
        resumo_anterior = _parse_extrator_for_rubrica_detailed(file_anterior, rubrica)
        resumo_atual = _parse_extrator_for_rubrica_detailed(file_atual, rubrica)
    except Exception as e:
        return {'erro': str(e)}

    merged = resumo_anterior.merge(
        resumo_atual,
        on=['empresa', 'matricula'],
        how='outer',
        suffixes=('_anterior', '_atual')
    )
    merged = merged.fillna({
        'valor_anterior': 0,
        'valor_atual': 0,
        'nome_servidor_anterior': '',
        'nome_servidor_atual': '',
        'cpf_anterior': '',
        'cpf_atual': '',
        'situacao_funcional_anterior': '',
        'situacao_funcional_atual': '',
        'status_servidor_anterior': '',
        'status_servidor_atual': '',
        'descricao_status_anterior': '',
        'descricao_status_atual': '',
        'cargo_anterior': '',
        'cargo_atual': '',
        'descricao_cargo_anterior': '',
        'descricao_cargo_atual': '',
        'data_admissao_anterior': '',
        'data_admissao_atual': '',
        'data_ingresso_ref_salarial_anterior': '',
        'data_ingresso_ref_salarial_atual': '',
        'data_afastamento_anterior': '',
        'data_afastamento_atual': '',
        'motivo_afastamento_anterior': '',
        'motivo_afastamento_atual': '',
        'motivo_desligamento_anterior': '',
        'motivo_desligamento_atual': '',
        'carga_horaria_anterior': '',
        'carga_horaria_atual': '',
        'carga_horaria_secundaria_anterior': '',
        'carga_horaria_secundaria_atual': '',
        'ref_vertical_anterior': '',
        'ref_vertical_atual': '',
        'ref_horizontal_anterior': '',
        'ref_horizontal_atual': '',
        'prov_desc_anterior': '',
        'prov_desc_atual': '',
        'valor_mes_anterior_anterior': '',
        'valor_mes_anterior_atual': '',
        'valor_mes_atual_anterior': '',
        'valor_mes_atual_atual': '',
        'valor_vencimento_anterior': '',
        'valor_vencimento_atual': '',
        'valor_total_recebido_anterior': '',
        'valor_total_recebido_atual': '',
        'frequencia_anterior': '',
        'frequencia_atual': '',
    })

    def pick(row, key):
        for suffix in ('_atual', '_anterior'):
            value = row.get(f'{key}{suffix}')
            formatted = format_raw_value(value)
            if formatted:
                return formatted
        return ''

    comparacao = []
    for _, row in merged.iterrows():
        valor_anterior = float(row['valor_anterior'] or 0)
        valor_atual = float(row['valor_atual'] or 0)
        diferenca = round(valor_atual - valor_anterior, 2)
        variacao_pct = None
        if valor_anterior != 0:
            variacao_pct = round((diferenca / valor_anterior) * 100, 2)

        status = 'sem-variacao'
        if valor_anterior == 0 and valor_atual != 0:
            status = 'novo'
        elif valor_anterior != 0 and valor_atual == 0:
            status = 'removido'
        elif valor_anterior != 0 and valor_atual > valor_anterior:
            status = 'aumento'
        elif valor_anterior != 0 and valor_atual < valor_anterior:
            status = 'reducao'

        item = {
            'empresa': row['empresa'],
            'matricula': row['matricula'],
            'nome_servidor': pick(row, 'nome_servidor'),
            'cpf': pick(row, 'cpf'),
            'situacao_funcional': pick(row, 'situacao_funcional'),
            'status_servidor': pick(row, 'status_servidor'),
            'descricao_status': pick(row, 'descricao_status'),
            'cargo': pick(row, 'cargo'),
            'descricao_cargo': pick(row, 'descricao_cargo'),
            'data_admissao': pick(row, 'data_admissao'),
            'data_ingresso_ref_salarial': pick(row, 'data_ingresso_ref_salarial'),
            'data_afastamento': pick(row, 'data_afastamento'),
            'motivo_afastamento': pick(row, 'motivo_afastamento'),
            'motivo_desligamento': pick(row, 'motivo_desligamento'),
            'carga_horaria': pick(row, 'carga_horaria'),
            'carga_horaria_secundaria': pick(row, 'carga_horaria_secundaria'),
            'ref_vertical': pick(row, 'ref_vertical'),
            'ref_horizontal': pick(row, 'ref_horizontal'),
            'prov_desc': pick(row, 'prov_desc'),
            'valor_mes_anterior': pick(row, 'valor_mes_anterior'),
            'valor_mes_atual': pick(row, 'valor_mes_atual'),
            'valor_vencimento': pick(row, 'valor_vencimento'),
            'valor_total_recebido': pick(row, 'valor_total_recebido'),
            'frequencia': pick(row, 'frequencia'),
            'valor_anterior': valor_anterior,
            'valor_atual': valor_atual,
            'diferenca': diferenca,
            'variacao_pct': variacao_pct,
            'status': status,
        }
        comparacao.append(item)

    comparacao = sorted(comparacao, key=lambda x: (x['empresa'], x['matricula']))

    return {
        'comparacao': comparacao,
    }


def extract_year(s):
    """Extrai ano de 4 dígitos"""
    if not isinstance(s, str):
        s = str(s)
    match = re.search(r'\b(20\d{2}|19\d{2})\b', s)
    return int(match.group(1)) if match else None


def extract_number(s):
    """Extrai número inteiro"""
    if not isinstance(s, (int, float)):
        s = str(s)
        match = re.search(r'\d+', s.replace('.', '').replace(',', ''))
        return int(match.group(0)) if match else 0
    return int(s)


def normalize_reference(value):
    """Normaliza referências para comparação.

    Remove o sufixo A final em referências como S3A ou 25A, e também trunca
    sequências numéricas maiores que duas casas.
    """
    if value is None:
        return ''
    s = str(value).strip().upper()
    if s == '':
        return ''

    # Trata representações numéricas como 2.0 ou 3,0 corretamente
    s = s.replace(',', '.')
    num_match = re.fullmatch(r'(\d+)(?:\.0+)?', s)
    if num_match:
        digits = num_match.group(1)
        return digits[:2] if len(digits) > 2 else digits

    s = re.sub(r'[^A-Z0-9]', '', s)

    # Remove o sufixo A final apenas em referências curtas como S3A ou 25A.
    if len(s) == 3 and s.endswith('A'):
        return s[:-1]

    def _truncate_digits(match):
        digits = match.group(0)
        return digits[:2]

    return re.sub(r'\d{3,}', _truncate_digits, s)


def norm_num(x):
    """Normaliza número para comparação"""
    try:
        import pandas as pd
        if pd.isna(x):
            return None
    except ImportError:
        pass
    try:
        x = float(str(x).replace(',', '.'))
        return round(x, 2)
    except:
        return None


def parse_int_value(value):
    """Converte valor para inteiro preservando casos como '30,0' e '40.0'."""
    if value is None:
        return None
    try:
        s = str(value).strip().replace(',', '.')
        return int(float(s))
    except Exception:
        try:
            match = re.search(r'\d+', str(value))
            return int(match.group(0)) if match else None
        except Exception:
            return None


def parse_month_value(value):
    """Converte valores de mês para inteiro de 1 a 12."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return int(value)
        except Exception:
            return None
    s = str(value).strip().lower()
    if s == '':
        return None
    # Extrai dígitos simples como 1, 01 ou 12
    digits = re.search(r'\d+', s)
    if digits:
        try:
            month = int(digits.group(0))
            return month if 1 <= month <= 12 else None
        except Exception:
            pass
    # Normaliza nomes de mês
    meses = {
        'janeiro': 1, 'jan': 1,
        'fevereiro': 2, 'fev': 2,
        'março': 3, 'marco': 3, 'mar': 3,
        'abril': 4, 'abr': 4,
        'maio': 5,
        'junho': 6, 'jun': 6,
        'julho': 7, 'jul': 7,
        'agosto': 8, 'ago': 8,
        'setembro': 9, 'set': 9,
        'outubro': 10, 'out': 10,
        'novembro': 11, 'nov': 11,
        'dezembro': 12, 'dez': 12,
    }
    cleaned = re.sub(r'[^a-z]', '', s)
    return meses.get(cleaned)


def find_alternate_carga_match(df_vencimento, col_refv_vertical, col_refv_horizontal,
                               col_ano_vencimento, col_carga_vencimento,
                               col_valor_vencimento, ref_v, ref_h, ano,
                               carga_horaria, valor_extrator):
    """Procura no VENCIMENTO um valor que corresponda a outra carga horária."""
    if valor_extrator is None:
        return None

    mask_alt = (
        (df_vencimento[col_refv_vertical].astype(str).apply(normalize_reference) == ref_v) &
        (df_vencimento[col_refv_horizontal].astype(str).apply(normalize_reference) == ref_h) &
        (df_vencimento[col_ano_vencimento].astype(str).str.replace(',', '') == str(ano))
    )

    df_alternativa = df_vencimento[mask_alt].copy()
    if df_alternativa.empty:
        return None

    for _, row_alt in df_alternativa.iterrows():
        carga_alt = parse_int_value(row_alt[col_carga_vencimento])
        if carga_alt is None or carga_alt == carga_horaria:
            continue

        valor_alt = norm_num(row_alt[col_valor_vencimento])
        if valor_alt is None:
            continue

        if abs(valor_alt - valor_extrator) <= 0.01:
            return {
                'carga': carga_alt,
                'valor': valor_alt,
            }

    return None


def parse_vigencia_date(value):
    """Converte DATA DE VIGÊNCIA para datetime, suportando formatos compactos como 1092014."""
    import pandas as pd

    if value is None:
        return pd.NaT
    s = str(value).strip()
    if s == '':
        return pd.NaT

    # Tenta converter diretamente com dayfirst
    try:
        parsed = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if not pd.isna(parsed):
            return parsed
    except Exception:
        pass

    # Remove tudo que não for dígito e tenta parsear como ddmmaaaa
    digits = ''.join(c for c in s if c.isdigit())
    if len(digits) in (7, 8):
        digits = digits.zfill(8)
        try:
            return pd.to_datetime(digits, format='%d%m%Y', errors='coerce')
        except Exception:
            pass

    return pd.NaT


def read_excel_flexible(filepath):
    """
    Lê arquivo Excel com suporte a múltiplos formatos (.xls, .xlsx)
    Tenta diferentes engines automaticamente
    Detecta e tenta ler HTML se arquivo for HTML em vez de Excel
    """
    import pandas as pd
    
    filepath_str = str(filepath).lower()
    
    # Verifica se o arquivo é HTML (pode ter extensão .xls/.xlsx mas ser HTML)
    try:
        with open(filepath, 'rb') as f:
            first_bytes = f.read(100)
            if b'<html' in first_bytes.lower() or b'<?xml' in first_bytes[:50].lower():
                debug_print(f"  ℹ Arquivo detectado como HTML/XML, tentando ler tabelas...")
                try:
                    # Tenta ler a primeira tabela HTML
                    tables = pd.read_html(filepath)
                    if tables:
                        debug_print(f"  ✓ Sucesso ao ler tabela HTML (encontradas {len(tables)} tabelas)")
                        return tables[0]  # Retorna a primeira tabela
                except Exception as html_err:
                    debug_print(f"  ✗ Falha ao ler como HTML: {str(html_err)[:80]}")
                    raise Exception(
                        f"Arquivo {filepath} é HTML em vez de Excel real.\n"
                        f"Possível causa: arquivo baixado de página web que retornou HTML.\n"
                        f"Solução: Salve o arquivo diretamente do Excel ou exporte em formato .xlsx válido."
                    )
    except Exception as e:
        if "Arquivo" in str(e) and "HTML" in str(e):
            raise e  # Re-raise nossas mensagens de erro
        # Continua com tentativa normal de leitura
        pass
    
    # Tenta com engine apropriado baseado na extensão
    # IMPORTANTE: xlrd < 2.0 suporta .xls | openpyxl suporta .xlsx
    engines = []
    if filepath_str.endswith('.xlsx'):
        engines = ['openpyxl']  # openpyxl é obrigatório para .xlsx
    elif filepath_str.endswith('.xls'):
        engines = ['xlrd']  # xlrd < 2.0 é necessário para .xls
    else:
        # Se extensão desconhecida, tenta com base no arquivo
        engines = ['openpyxl', 'xlrd']
    
    last_error = None
    for engine in engines:
        try:
            debug_print(f"  Tentando ler com engine: {engine}")
            df = pd.read_excel(filepath, engine=engine)
            debug_print(f"  ✓ Sucesso com engine: {engine}")
            return df
        except Exception as e:
            last_error = e
            debug_print(f"  ✗ Falha com {engine}: {str(e)[:80]}")
            continue
    
    # Se chegou aqui, nenhum engine funcionou
    raise Exception(f"Não foi possível ler o arquivo {filepath}. Formatos suportados: .xls, .xlsx. Erro: {str(last_error)}")


def processar_verificacao(file_vencimento, file_extrator, rubrica: str, ano: int, carga_horaria: int) -> Dict:
    """
    Processa dois arquivos Excel comparando conformidade de pagamentos.
    
    FLUXO:
    1. Filtrar EXTRATOR por: PROV/DESC = rubrica, ANO REFERENCIA = ano, CARGA HORARIA = carga_horaria
    2. Para cada pessoa no EXTRATOR filtrado:
       - Obter REF SALARIAL VERTICAL e REF SALARIAL HORIZONTAL
       - Procurar no VENCIMENTO por REFERENCIA DE VENCIMENTO VERTICAL e HORIZONTAL
       - Comparar VALOR DO VENCIMENTO com VALOR (EXTRATOR)
    3. Retornar lista com pessoas, valores esperados, valores encontrados e status
    
    Args:
        file_vencimento: Arquivo VENCIMENTO (tabela de valores por referência)
        file_extrator: Arquivo EXTRATOR (folha de pagamento com pessoas)
        rubrica: PROV/DESC a filtrar
        ano: ANO REFERENCIA a filtrar
        carga_horaria: CARGA HORARIA a filtrar
        
    Returns:
        Dict com resultados: sucesso, resultados[], total, corretos, incorretos
    """
    try:
        import pandas as pd
    except ImportError as e:
        return {'erro': f'Pandas não foi configurado: {str(e)}. Reinstale com: pip install -r requirements.txt'}
    
    try:
        # Lê os arquivos com suporte a .xls e .xlsx
        debug_print(f"\n📂 Lendo arquivo VENCIMENTO: {file_vencimento}")
        df_vencimento = read_excel_flexible(file_vencimento)
        
        debug_print(f"\n📂 Lendo arquivo EXTRATOR: {file_extrator}")
        df_extrator = read_excel_flexible(file_extrator)
        
    except Exception as e:
        return {'erro': f'Erro ao ler arquivos: {str(e)}. Certifique-se de que são arquivos válidos .xls ou .xlsx'}

    # Limpa headers
    df_vencimento = flatten_and_clean_columns(df_vencimento)
    df_extrator = flatten_and_clean_columns(df_extrator)

    debug_print(f"\n{'='*80}")
    debug_print(f"=== ANÁLISE DETALHADA DOS ARQUIVOS ===")
    debug_print(f"{'='*80}")
    
    debug_print(f"\n📊 ARQUIVO VENCIMENTO:")
    debug_print(f"  Shape: {df_vencimento.shape}")
    debug_print(f"  Colunas: {df_vencimento.columns.tolist()}")
    debug_print(f"  Primeiras 2 linhas:")
    debug_print(df_vencimento.head(2).to_string())
    
    debug_print(f"\n📊 ARQUIVO EXTRATOR (ppgg.xlsx):")
    debug_print(f"  Shape: {df_extrator.shape}")
    debug_print(f"  Colunas: {df_extrator.columns.tolist()}")
    debug_print(f"  Primeiras 2 linhas:")
    debug_print(df_extrator.head(2).to_string())
    
    debug_print(f"\n{'='*80}")

    # ENCONTRA COLUNAS
    # EXTRATOR
    col_nome_servidor = find_by_words(df_extrator, ['nome', 'servidor'])
    col_prov = find_by_words(df_extrator, ['prov', 'desc'], debug=True) 
    
    # FALLBACK: Se não encontrou coluna de rubrica, tenta alternativas
    if not col_prov:
        debug_print("\n⚠️ RUBRICA NÃO ENCONTRADA - Tentando alternativas...")
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if any(term in col_norm for term in ['rubrica', 'ar', 'funcao', 'prov', 'desc']):
                debug_print(f"  Usando alternativa: '{col}'")
                col_prov = col
                break
    
    col_ano_extrator = find_by_words(df_extrator, ['ano', 'referencia'])
    col_mes_extrator = find_by_words(df_extrator, ['mes', 'referencia']) or find_by_words(df_extrator, ['mes'])
    col_carga_extrator = find_by_words(df_extrator, ['carga', 'horaria'])
    col_ref_vertical = find_by_words(df_extrator, ['ref', 'salarial', 'vertical'])
    col_ref_horizontal = find_by_words(df_extrator, ['ref', 'salarial', 'horizontal'])
    col_valor_extrator = find_by_words(df_extrator, ['valor'])
    col_frequencia = find_by_words(df_extrator, ['frequencia'])  # Para rubrica 10502
    col_empresa = (find_by_words(df_extrator, ['empresa']) or 
                   find_by_words(df_extrator, ['cod', 'empresa']) or 
                   find_by_words(df_extrator, ['codigo', 'empresa']) or
                   find_by_words(df_extrator, ['cod_empresa']) or
                   find_by_words(df_extrator, ['código']))
    col_orgao = (find_by_words(df_extrator, ['orgao']) or
                 find_by_words(df_extrator, ['unidade']) or
                 find_by_words(df_extrator, ['lotacao']) or
                 find_by_words(df_extrator, ['lotação']))
    if not col_orgao:
        for col in df_extrator.columns:
            col_norm = normalize(col)
            if any(term in col_norm for term in ['orgao', 'org', 'órg', 'unidade', 'lotac']):
                col_orgao = col
                break
    col_cpf = find_by_words(df_extrator, ['cpf']) or find_by_words(df_extrator, ['documento']) or find_by_words(df_extrator, ['cpf/documento'])
    col_matricula = find_by_words(df_extrator, ['matricula', 'matrícula'])

    # Additional columns for detailed server information
    col_situacao_funcional = find_by_words(df_extrator, ['situacao', 'funcional']) or find_by_words(df_extrator, ['situação', 'funcional'])
    col_status = find_by_words(df_extrator, ['status'])
    col_descricao_status = find_by_words(df_extrator, ['descricao', 'status']) or find_by_words(df_extrator, ['descrição', 'status'])
    col_cargo = find_by_words(df_extrator, ['cargo']) or find_by_words(df_extrator, ['funcao'])
    col_descricao_cargo = find_by_words(df_extrator, ['descricao', 'cargo']) or find_by_words(df_extrator, ['descrição', 'cargo'])
    col_data_admissao = find_by_words(df_extrator, ['data', 'admissao']) or find_by_words(df_extrator, ['data', 'admissão'])
    col_data_ingresso_ref_salarial = find_by_words(df_extrator, ['data', 'ingresso', 'referencia', 'salarial']) or find_by_words(df_extrator, ['data', 'ingresso', 'ref', 'salarial'])
    col_data_afastamento = find_by_words(df_extrator, ['data', 'afastamento'])
    col_motivo_afastamento = find_by_words(df_extrator, ['motivo', 'afastamento'])
    col_motivo_desligamento = find_by_words(df_extrator, ['motivo', 'desligamento']) or find_by_words(df_extrator, ['motivo', 'demissão'])
    col_carga_horaria = find_by_words(df_extrator, ['carga', 'horaria'])
    col_carga_horaria_secundaria = find_by_words(df_extrator, ['carga', 'horaria', 'secundaria']) or find_by_words(df_extrator, ['carga', 'horária', 'secundária'])
    col_prov_desc = find_by_words(df_extrator, ['prov', 'desc'])
    col_valor_mes_anterior = find_by_words(df_extrator, ['valor', 'mes', 'anterior']) or find_by_words(df_extrator, ['valor', 'mês', 'anterior'])
    col_valor_mes_atual = find_by_words(df_extrator, ['valor', 'mes', 'atual']) or find_by_words(df_extrator, ['valor', 'mês', 'atual'])

    # VENCIMENTO  
    col_refv_vertical = find_by_words(df_vencimento, ['referencia', 'vencimento', 'vertical'])
    col_refv_horizontal = find_by_words(df_vencimento, ['referencia', 'vencimento', 'horizontal'])
    col_ano_vencimento = find_by_words(df_vencimento, ['ano', 'referencia'])
    col_carga_vencimento = find_by_words(df_vencimento, ['carga', 'horaria'])
    col_valor_vencimento = find_by_words(df_vencimento, ['valor', 'vencimento']) or find_by_words(df_vencimento, ['valor'])
    col_data_vigencia = find_by_words(df_vencimento, ['data', 'vigencia', 'DATA DE VIGENCIA'])

    debug_print(f"\n=== COLUNAS ENCONTRADAS ===")
    debug_print(f"EXTRATOR:")
    debug_print(f"  Nome Servidor: {col_nome_servidor}")
    debug_print(f"  PROV/DESC: {col_prov}")
    debug_print(f"  Ano: {col_ano_extrator}")
    debug_print(f"  Mês: {col_mes_extrator}")
    debug_print(f"  Carga: {col_carga_extrator}")
    debug_print(f"  Ref Vertical: {col_ref_vertical}")
    debug_print(f"  Ref Horizontal: {col_ref_horizontal}")
    debug_print(f"  Valor: {col_valor_extrator}")
    debug_print(f"  Frequência: {col_frequencia} (para rubrica 10502)")
    debug_print(f"  Empresa: {col_empresa}")
    debug_print(f"  Orgão: {col_orgao}")
    debug_print(f"  CPF: {col_cpf}")
    debug_print(f"  Matrícula: {col_matricula}")
    debug_print(f"  Situação Funcional: {col_situacao_funcional}")
    debug_print(f"  Status: {col_status}")
    debug_print(f"  Descrição Status: {col_descricao_status}")
    debug_print(f"  Cargo: {col_cargo}")
    debug_print(f"  Descrição Cargo: {col_descricao_cargo}")
    debug_print(f"  Data Admissão: {col_data_admissao}")
    debug_print(f"  Data Ingresso Ref Salarial: {col_data_ingresso_ref_salarial}")
    debug_print(f"  Data Afastamento: {col_data_afastamento}")
    debug_print(f"  Motivo Afastamento: {col_motivo_afastamento}")
    debug_print(f"  Motivo Desligamento: {col_motivo_desligamento}")
    debug_print(f"  Carga Horária: {col_carga_horaria}")
    debug_print(f"  Carga Horária Secundária: {col_carga_horaria_secundaria}")
    debug_print(f"  PROV/DESC: {col_prov_desc}")
    debug_print(f"  Valor Mês Anterior: {col_valor_mes_anterior}")
    debug_print(f"  Valor Mês Atual: {col_valor_mes_atual}")
    debug_print(f"VENCIMENTO:")
    debug_print(f"  Ref Vertical: {col_refv_vertical}")
    debug_print(f"  Ref Horizontal: {col_refv_horizontal}")
    debug_print(f"  Ano: {col_ano_vencimento}")
    debug_print(f"  Carga: {col_carga_vencimento}")
    debug_print(f"  Valor: {col_valor_vencimento}")
    debug_print(f"  DATA DE VIGENCIA: {col_data_vigencia}")

    # INFORMAÇÕES SOBRE OS ARQUIVOS (APÓS ENCONTRAR COLUNAS)
    print(f"\n=== INFORMAÇÕES SOBRE OS ARQUIVOS ===")
    print(f"VENCIMENTO: {df_vencimento.shape[0]} linhas, {df_vencimento.shape[1]} colunas")
    if col_ano_vencimento:
        anos_venc = sorted(pd.to_numeric(df_vencimento[col_ano_vencimento], errors='coerce').dropna().unique().astype(int).tolist())
        print(f"  Anos disponíveis: {anos_venc}")
    if col_carga_vencimento:
        cargas_venc = sorted(pd.to_numeric(df_vencimento[col_carga_vencimento], errors='coerce').dropna().unique().astype(int).tolist())
        print(f"  Cargas disponíveis: {cargas_venc}")
    
    print(f"\nEXTRATOR: {df_extrator.shape[0]} linhas, {df_extrator.shape[1]} colunas")
    if col_prov:
        print(f"  Rubricas (PROV/DESC) disponíveis: {df_extrator[col_prov].unique().tolist()[:20]}")
    if col_ano_extrator:
        anos_ext = sorted(pd.to_numeric(df_extrator[col_ano_extrator], errors='coerce').dropna().unique().astype(int).tolist())
        print(f"  Anos disponíveis: {anos_ext}")
    if col_carga_extrator:
        cargas_ext = sorted(pd.to_numeric(df_extrator[col_carga_extrator], errors='coerce').dropna().unique().astype(int).tolist())
        print(f"  Cargas disponíveis: {cargas_ext}")
    
    print(f"\n⚠️ ATENÇÃO: Você procura: rubrica={rubrica}, ano={ano}, carga={carga_horaria}\n")

    # AVISO se coluna EMPRESA não for encontrada
    if not col_empresa:
        print(f"\n⚠️ AVISO: Coluna EMPRESA não foi encontrada no EXTRATOR!")
        print(f"   Colunas disponíveis: {df_extrator.columns.tolist()}")
        print(f"   O sistema tentou procurar por: 'empresa', 'cod_empresa', 'código'")
        print(f"   Se você tem uma coluna com empresa/código, renomeie para um desses nomes.")
    else:
        print(f"\n✓ Coluna EMPRESA encontrada: {col_empresa}")
        print(f"  Exemplos de valores: {df_extrator[col_empresa].dropna().unique().tolist()[:5]}")

    # VALIDAÇÕES
    erros = []
    if not col_nome_servidor:
        erros.append("Coluna NOME DO SERVIDOR não encontrada")
    if not col_prov:
        erros.append("Coluna PROV/DESC não encontrada")
    if not col_ano_extrator:
        erros.append("Coluna ANO REFERENCIA (EXTRATOR) não encontrada")
    if not col_carga_extrator:
        erros.append("Coluna CARGA HORARIA (EXTRATOR) não encontrada")
    if not col_ref_vertical or not col_ref_horizontal:
        erros.append("Colunas REF SALARIAL VERTICAL/HORIZONTAL não encontradas")
    if not col_valor_extrator:
        erros.append("Coluna VALOR (EXTRATOR) não encontrada")
    if not col_refv_vertical or not col_refv_horizontal:
        erros.append("Colunas REFERENCIA DE VENCIMENTO VERTICAL/HORIZONTAL não encontradas")
    if not col_ano_vencimento:
        erros.append("Coluna ANO REFERENCIA (VENCIMENTO) não encontrada")
    if not col_carga_vencimento:
        erros.append("Coluna CARGA HORARIA (VENCIMENTO) não encontrada")
    if not col_valor_vencimento:
        erros.append("Coluna VALOR (VENCIMENTO) não encontrada")
    
    if erros:
        msgs = " | ".join(erros)
        debug_print(f"\n❌ ERROS NA DETECÇÃO DE COLUNAS:")
        debug_print(f"{msgs}")
        debug_print(f"\nColunas disponíveis no EXTRATOR:")
        debug_print(f"{df_extrator.columns.tolist()}")
        debug_print(f"\nColunas disponíveis no VENCIMENTO:")
        debug_print(f"{df_vencimento.columns.tolist()}")
        return {'erro': msgs}
    
    # AVISO sobre coluna de data de vigência
    if not col_data_vigencia:
        debug_print(f"\n⚠️ AVISO: Coluna DATA DE VIGÊNCIA não encontrada no VENCIMENTO.")
        debug_print(f"   Quando houver múltiplos registros, será usado o primeiro encontrado.")
        debug_print(f"   Para usar o valor mais recente, certifique-se de que há uma coluna 'DATA DE VIGENCIA' no arquivo.")

    # PASSO 1: FILTRAR EXTRATOR
    debug_print(f"\n{'='*80}")
    debug_print(f"=== FILTRANDO EXTRATOR ===")
    debug_print(f"{'='*80}")
    debug_print(f"Antes de filtros: {len(df_extrator)} linhas")
    
    # Filtro por Rubrica
    debug_print(f"\n--- FILTRO RUBRICA ---")
    debug_print(f"Coluna usada: {col_prov}")
    debug_print(f"Todos valores únicos em {col_prov}: {df_extrator[col_prov].unique().tolist()}")
    debug_print(f"Procurando: '{rubrica}' (tipo: {type(rubrica).__name__})")
    
    # Converter para string, remover espaços e verificar
    df_extrator_prov = df_extrator[col_prov].astype(str).str.strip()
    debug_print(f"Primeiros 20 valores após str().strip(): {df_extrator_prov.head(20).tolist()}")
    
    # Preparar rubrica para busca
    rubrica_str = str(rubrica).strip()
    debug_print(f"\nRubrica procurada: '{rubrica_str}'")
    
    # Testar diferentes tipos de match
    debug_print(f"\nTestando diferentes tipos de match:")
    mask_exato = df_extrator_prov == rubrica_str
    debug_print(f"  Igualdade exata (==): {mask_exato.sum()} matches")
    
    mask_contains = df_extrator_prov.str.contains(rubrica_str, case=False, na=False)
    debug_print(f"  Contains (case-insensitive): {mask_contains.sum()} matches")
    
    mask_contains_case = df_extrator_prov.str.contains(rubrica_str, case=True, na=False)
    debug_print(f"  Contains (case-sensitive): {mask_contains_case.sum()} matches")
    
    # Tenta primeiro igualdade exata (com strip)
    df_extrator_filtrado = df_extrator[mask_exato]
    debug_print(f"\nApós filtro rubrica={rubrica_str}: {len(df_extrator_filtrado)} linhas")
    
    # Se não encontrou, tenta contains (mais flexível)
    if len(df_extrator_filtrado) == 0:
        debug_print(f"\n⚠️ AVISO: Nenhum registro com rubrica exata '{rubrica_str}'")
        debug_print(f"   Tentando com contains (case-insensitive)...")
        df_extrator_filtrado = df_extrator[mask_contains]
        debug_print(f"   Encontrados: {len(df_extrator_filtrado)} linhas")
    
    # Se ainda não encontrou, tenta contains case-sensitive
    if len(df_extrator_filtrado) == 0:
        debug_print(f"\n   Tentando com contains (case-sensitive)...")
        df_extrator_filtrado = df_extrator[mask_contains_case]
        debug_print(f"   Encontrados: {len(df_extrator_filtrado)} linhas")
    
    if len(df_extrator_filtrado) == 0:
        debug_print(f"\n❌ Nenhum registro encontrado com rubrica='{rubrica_str}'")
        rubricas_disponiveis = df_extrator_prov.unique().tolist()[:50]
        debug_print(f"   Rubricas disponíveis: {rubricas_disponiveis}")
        return {'erro': f'Rubrica "{rubrica_str}" não encontrada. Disponíveis: {rubricas_disponiveis}'}
    
    df_extrator = df_extrator_filtrado
    
    # Filtro por Ano
    debug_print(f"\n--- FILTRO ANO ---")
    debug_print(f"Coluna usada: {col_ano_extrator}")
    debug_print(f"Valores crus em {col_ano_extrator}: {df_extrator[col_ano_extrator].head(20).tolist()}")
    debug_print(f"Procurando: {ano} (tipo: {type(ano).__name__})")
    
    try:
        df_extrator_ano = df_extrator[col_ano_extrator].astype(str).str.strip().str.replace(',', '').astype(float).astype(int)
        debug_print(f"Valores após conversão para int: {df_extrator_ano.unique().tolist()}")
    except Exception as e:
        debug_print(f"Erro na conversão: {e}, tentando extract...")
        df_extrator_ano = df_extrator[col_ano_extrator].astype(str).str.extract(r'(\d+)')[0].astype(int)
        debug_print(f"Valores após extract: {df_extrator_ano.unique().tolist()}")
    
    debug_print(f"\nComparando:")
    debug_print(f"  Procura-se: {ano} (tipo: {type(ano).__name__})")
    debug_print(f"  Disponíveis: {sorted(df_extrator_ano.unique().tolist())}")
    
    mask_ano = df_extrator_ano == ano
    debug_print(f"Matches encontrados: {mask_ano.sum()} linhas")
    df_extrator = df_extrator[mask_ano]
    debug_print(f"Após filtro ano={ano}: {len(df_extrator)} linhas")
    
    if len(df_extrator) == 0:
        debug_print(f"❌ Nenhum registro encontrado com ano={ano}")
        anos_disponiveis = sorted(df_extrator_ano.unique().astype(int).tolist())
        debug_print(f"   Anos disponíveis: {anos_disponiveis}")
        return {'erro': f'Ano {ano} não encontrado em EXTRATOR. Anos disponíveis: {anos_disponiveis}. Use um dos anos disponíveis!'}
    
    # Tenta extrair Mês da coluna do EXTRATOR, se disponível
    mes_referencia = None
    if col_mes_extrator and col_mes_extrator in df_extrator.columns:
        mes_values = df_extrator[col_mes_extrator].dropna().apply(parse_month_value)
        mes_values = mes_values.dropna().unique().tolist()
        if len(mes_values) == 1:
            mes_referencia = int(mes_values[0])
            debug_print(f"  Mês de referência extraído do EXTRATOR: {mes_referencia}")
        elif len(mes_values) > 1:
            mes_referencia = int(mes_values[0])
            debug_print(f"  Múltiplos meses encontrados em {col_mes_extrator}: {mes_values}. Usando o primeiro: {mes_referencia}")
        else:
            debug_print(f"  Coluna {col_mes_extrator} encontrada, mas não foi possível extrair mês válido.")

    # Filtro por Carga Horária
    debug_print(f"\n--- FILTRO CARGA HORÁRIA ---")
    debug_print(f"Coluna usada: {col_carga_extrator}")
    debug_print(f"Todos valores únicos em {col_carga_extrator}: {df_extrator[col_carga_extrator].unique().tolist()}")
    debug_print(f"Procurando: {carga_horaria} (tipo: {type(carga_horaria).__name__})")
    
    try:
        df_extrator_carga = df_extrator[col_carga_extrator].astype(str).str.strip().str.replace(',', '').astype(float).astype(int)
        debug_print(f"Valores após conversão para int: {df_extrator_carga.unique().tolist()}")
    except Exception as e:
        debug_print(f"Erro na conversão: {e}, tentando extract...")
        df_extrator_carga = df_extrator[col_carga_extrator].astype(str).str.extract(r'(\d+)')[0].astype(int)
        debug_print(f"Valores após extract: {df_extrator_carga.unique().tolist()}")
    
    mask_carga = df_extrator_carga == carga_horaria
    debug_print(f"Matches encontrados: {mask_carga.sum()} linhas")
    df_extrator = df_extrator[mask_carga]
    debug_print(f"Após filtro carga={carga_horaria}: {len(df_extrator)} linhas")

    if df_extrator.empty:
        debug_print(f"❌ Nenhum registro encontrado com carga={carga_horaria}")
        cargas_disponiveis = sorted(pd.to_numeric(
            read_excel_flexible(file_extrator)[col_carga_extrator], 
            errors='coerce'
        ).dropna().unique().astype(int).tolist())
        debug_print(f"   Cargas disponíveis: {cargas_disponiveis}")
        return {'erro': f'Carga horária {carga_horaria} não encontrada em EXTRATOR. Cargas disponíveis: {cargas_disponiveis}'}
    
    debug_print(f"\n{'='*80}")
    debug_print(f"✅ FILTROS APLICADOS COM SUCESSO!")
    debug_print(f"  Rubrica: {rubrica}")
    debug_print(f"  Ano: {ano}")
    debug_print(f"  Carga: {carga_horaria}")
    debug_print(f"  Total de registros para processar: {len(df_extrator)}")
    debug_print(f"{'='*80}\n")

    # PASSO 2: COMPARAR PESSOAS
    debug_print(f"\n=== COMPARANDO VALORES ===")
    resultados = []
    corretos = 0
    incorretos = 0
    verificar = 0

    for idx, row_extrator in df_extrator.iterrows():
        nome_servidor = row_extrator[col_nome_servidor]
        ref_v_raw = row_extrator[col_ref_vertical]
        ref_h_raw = row_extrator[col_ref_horizontal]
        ref_v = normalize_reference(ref_v_raw)
        ref_h = normalize_reference(ref_h_raw)
        valor_extrator = norm_num(row_extrator[col_valor_extrator])
        frequencia = norm_num(row_extrator[col_frequencia]) if col_frequencia else None
        
        # Extrai EMPRESA preservando zeros à esquerda
        if col_empresa:
            empresa_raw = str(row_extrator[col_empresa]).strip()
            # Remove ".0" se for número, depois preserva zeros à esquerda
            empresa = empresa_raw.replace('.0', '') if empresa_raw.endswith('.0') else empresa_raw
            # Garante zeros à esquerda (mínimo 3 dígitos para códigos como 007)
            if empresa.isdigit():
                empresa = empresa.zfill(3)
        else:
            empresa = ''
        
        # Extrai CPF preservando formato completo
        if col_cpf and col_cpf in df_extrator.columns:
            cpf = str(row_extrator[col_cpf]).strip()
            # Remove ".0" se for número
            cpf = cpf.replace('.0', '') if cpf.endswith('.0') else cpf
            cpf = cpf if cpf and cpf.lower() != 'nan' else ''
        else:
            cpf = ''
        
        matricula = str(row_extrator[col_matricula]).strip() if col_matricula else ''

        # Extrai órgão, se disponível
        if col_orgao and col_orgao in df_extrator.columns:
            orgao_raw = str(row_extrator[col_orgao]).strip()
            orgao = orgao_raw if orgao_raw and orgao_raw.lower() != 'nan' else ''
        else:
            orgao = ''

        valor_esperado = None

        # Busca o valor esperado no VENCIMENTO
        # Precisa que REFERENCIA DE VENCIMENTO VERTICAL = ref_v
        #                  REFERENCIA DE VENCIMENTO HORIZONTAL = ref_h
        #                  ANO REFERENCIA = ano
        #                  CARGA HORARIA = carga_horaria
        
        mascara = (
            (df_vencimento[col_refv_vertical].astype(str).apply(normalize_reference) == ref_v) &
            (df_vencimento[col_refv_horizontal].astype(str).apply(normalize_reference) == ref_h) &
            (df_vencimento[col_ano_vencimento].astype(str).str.replace(',', '') == str(ano)) &
            (df_vencimento[col_carga_vencimento].astype(str).str.replace(',', '') == str(carga_horaria))
        )
        
        registros_encontrados = df_vencimento[mascara]
        
        # Se encontrou múltiplos registros e há coluna de data de vigência,
        # ordena por data de vigência descendente para pegar o mais recente
        if not registros_encontrados.empty and col_data_vigencia and col_data_vigencia in registros_encontrados.columns:
            try:
                # Tenta converter para datetime e ordenar
                registros_encontrados = registros_encontrados.copy()
                registros_encontrados['data_vigencia_parsed'] = registros_encontrados[col_data_vigencia].apply(parse_vigencia_date)
                registros_encontrados = registros_encontrados.sort_values(
                    'data_vigencia_parsed', 
                    ascending=False, 
                    na_position='last'
                )
                debug_print(f"  [DATA VIGÊNCIA] Ordenando {len(registros_encontrados)} registros por data de vigência")
                debug_print(f"    Data mais recente: {registros_encontrados.iloc[0]['data_vigencia_parsed']}")
            except Exception as e:
                debug_print(f"  [AVISO] Erro ao ordenar por data de vigência: {e}. Usando primeiro registro encontrado.")
        
        alternate_carga_match = find_alternate_carga_match(
            df_vencimento,
            col_refv_vertical,
            col_refv_horizontal,
            col_ano_vencimento,
            col_carga_vencimento,
            col_valor_vencimento,
            ref_v,
            ref_h,
            ano,
            carga_horaria,
            valor_extrator,
        )

        if registros_encontrados.empty:
            valor_vencimento = None
            if alternate_carga_match:
                status = 'INCORRETO'
                diferenca_absoluta = None
                diferenca_percentual = None
                justificativa = (
                    f'Carga horária divergente: recebeu como {alternate_carga_match["carga"]}h ' 
                    f'(R$ {valor_extrator}) em vez de {carga_horaria}h.'
                )
                incorretos += 1
            else:
                status = 'INCORRETO'
                valor_vencimento = None
                diferenca_absoluta = None
                diferenca_percentual = None
                incorretos += 1
        else:
            valor_vencimento = norm_num(registros_encontrados.iloc[0][col_valor_vencimento])
            
            # Calcula diferença
            if valor_vencimento and valor_extrator:
                justificativa = None
                valor_esperado = None
                
                # Regra de baixa frequência para qualquer rubrica
                if frequencia is not None and frequencia <= 1 and valor_extrator != 0:
                    valor_esperado_alt_30 = round(valor_extrator * 30, 2)
                    valor_esperado_alt_31 = round(valor_extrator * 31, 2)
                    ratio = valor_vencimento / valor_extrator if valor_extrator != 0 else None
                    if ratio is not None and abs(ratio - 30) <= 0.1:
                        status = 'CORRETO'
                        justificativa = f'Baixa frequência: R$ {valor_extrator} × 30 ≈ R$ {valor_esperado_alt_30} ✓'
                        corretos += 1
                    elif ratio is not None and abs(ratio - 31) <= 0.1:
                        status = 'CORRETO'
                        justificativa = f'Baixa frequência: R$ {valor_extrator} × 31 ≈ R$ {valor_esperado_alt_31} ✓'
                        corretos += 1
                
                if justificativa is None:
                    # REGRA ESPECIAL PARA RUBRICA 10502
                    # Quando rubrica = 10502, o valor do extrator deve ser igual a:
                    # valor_vencimento × (frequencia / 100)
                    if str(rubrica).strip() == '10502' and col_frequencia:
                        if frequencia is not None:
                            valor_esperado = round(valor_vencimento * (frequencia / 100), 2)
                            diferenca_absoluta = abs(valor_extrator - valor_esperado)
                            diferenca_percentual = (diferenca_absoluta / valor_esperado * 100) if valor_esperado != 0 else 0
                            diferenca_percentual = round(diferenca_percentual, 2)
                            diferenca_absoluta = round(diferenca_absoluta, 2)
                            
                            debug_print(f"\n[RUBRICA 10502] {nome_servidor}:")
                            debug_print(f"  Valor Vencimento: {valor_vencimento}")
                            debug_print(f"  Frequência: {frequencia}%")
                            debug_print(f"  Valor Esperado: {valor_vencimento} × {frequencia/100} = {valor_esperado}")
                            debug_print(f"  Valor Extrator: {valor_extrator}")
                            debug_print(f"  Diferença: {diferenca_absoluta} ({diferenca_percentual}%)")
                            
                            # Compara valores
                            if valor_extrator == valor_esperado:
                                status = 'CORRETO'
                                justificativa = f'Rubrica 10502: R$ {valor_vencimento} × {frequencia}% = R$ {valor_esperado} ✓'
                                corretos += 1
                            elif diferenca_absoluta is not None and diferenca_absoluta <= 0.01:
                                # Tolerância para arredondamento: até R$ 0.01 de diferença é considerado CORRETO
                                status = 'CORRETO'
                                justificativa = f'Rubrica 10502: R$ {valor_vencimento} × {frequencia}% = R$ {valor_esperado} (diferença de R$ {diferenca_absoluta} dentro da tolerância de arredondamento) ✓'
                                corretos += 1
                            elif diferenca_percentual is not None and diferenca_percentual < 0.5:
                                status = 'VERIFICAR (Valores muito próximos)'
                                justificativa = f'Rubrica 10502: R$ {valor_vencimento} × {frequencia}% = R$ {valor_esperado}, mas recebeu R$ {valor_extrator} (diferença: {diferenca_percentual}%)'
                                verificar += 1
                            else:
                                status = 'INCORRETO'
                                justificativa = f'Rubrica 10502: Esperado R$ {valor_esperado} (R$ {valor_vencimento} × {frequencia}%), mas recebeu R$ {valor_extrator}'
                                incorretos += 1
                        else:
                            # Se não conseguiu obter frequência, marca como incorreto
                            status = 'INCORRETO'
                            justificativa = 'Rubrica 10502: Frequência não encontrada'
                            incorretos += 1
                            diferenca_absoluta = None
                            diferenca_percentual = None
                    else:
                        # Comparação normal para outras rubricas
                        diferenca_absoluta = abs(valor_extrator - valor_vencimento)
                        diferenca_percentual = (diferenca_absoluta / valor_vencimento * 100) if valor_vencimento != 0 else 0
                        diferenca_percentual = round(diferenca_percentual, 2)
                        diferenca_absoluta = round(diferenca_absoluta, 2)
                        
                        # Compara valores
                        if valor_extrator == valor_vencimento:
                            status = 'CORRETO'
                            justificativa = f'Valor confere com vencimento: R$ {valor_vencimento} ✓'
                            corretos += 1
                        elif diferenca_absoluta is not None and diferenca_absoluta <= 0.01:
                            # Tolerância para arredondamento: até R$ 0.01 de diferença é considerado CORRETO
                            status = 'CORRETO'
                            justificativa = f'Valor confere com vencimento (diferença de R$ {diferenca_absoluta} dentro da tolerância) ✓'
                            corretos += 1
                        elif diferenca_percentual is not None and diferenca_percentual < 0.5:
                            # Valores muito próximos (< 0.5% de diferença) - marcar para verificação
                            status = 'VERIFICAR (Valores muito próximos)'
                            justificativa = f'Diferença de R$ {diferenca_absoluta} ({diferenca_percentual}%) em relação ao esperado R$ {valor_vencimento}'
                            verificar += 1
                        else:
                            status = 'INCORRETO'
                            justificativa = f'Esperado R$ {valor_vencimento}, mas recebeu R$ {valor_extrator}'
                            incorretos += 1

                if alternate_carga_match and status != 'CORRETO':
                    status = 'INCORRETO'
                    justificativa = (
                        f'Carga horária divergente: recebeu como {alternate_carga_match["carga"]}h '
                        f'(R$ {valor_extrator}) em vez de {carga_horaria}h.'
                    )
            else:
                diferenca_absoluta = None
                diferenca_percentual = None
                status = 'INCORRETO'
                justificativa = 'Valores inválidos para comparação'
                incorretos += 1

        resultado = {
            'empresa': empresa,
            'orgao': orgao,
            'cpf': cpf,
            'matricula': matricula,
            'nome_servidor': nome_servidor,
            'situacao_funcional': format_raw_value(row_extrator[col_situacao_funcional]) if col_situacao_funcional and col_situacao_funcional in df_extrator.columns else '',
            'status_servidor': format_raw_value(row_extrator[col_status]) if col_status and col_status in df_extrator.columns else '',
            'descricao_status': format_raw_value(row_extrator[col_descricao_status]) if col_descricao_status and col_descricao_status in df_extrator.columns else '',
            'cargo': format_raw_value(row_extrator[col_cargo]) if col_cargo and col_cargo in df_extrator.columns else '',
            'descricao_cargo': format_raw_value(row_extrator[col_descricao_cargo]) if col_descricao_cargo and col_descricao_cargo in df_extrator.columns else '',
            'data_admissao': format_raw_value(row_extrator[col_data_admissao]) if col_data_admissao and col_data_admissao in df_extrator.columns else '',
            'data_ingresso_ref_salarial': format_raw_value(row_extrator[col_data_ingresso_ref_salarial]) if col_data_ingresso_ref_salarial and col_data_ingresso_ref_salarial in df_extrator.columns else '',
            'data_afastamento': format_raw_value(row_extrator[col_data_afastamento]) if col_data_afastamento and col_data_afastamento in df_extrator.columns else '',
            'motivo_afastamento': format_raw_value(row_extrator[col_motivo_afastamento]) if col_motivo_afastamento and col_motivo_afastamento in df_extrator.columns else '',
            'motivo_desligamento': format_raw_value(row_extrator[col_motivo_desligamento]) if col_motivo_desligamento and col_motivo_desligamento in df_extrator.columns else '',
            'carga_horaria': format_raw_value(row_extrator[col_carga_horaria]) if col_carga_horaria and col_carga_horaria in df_extrator.columns else '',
            'carga_horaria_secundaria': format_raw_value(row_extrator[col_carga_horaria_secundaria]) if col_carga_horaria_secundaria and col_carga_horaria_secundaria in df_extrator.columns else '',
            'ref_vertical': ref_v,
            'ref_horizontal': ref_h,
            'prov_desc': format_raw_value(row_extrator[col_prov_desc]) if col_prov_desc and col_prov_desc in df_extrator.columns else '',
            'valor_mes_anterior': norm_num(row_extrator[col_valor_mes_anterior]) if col_valor_mes_anterior and col_valor_mes_anterior in df_extrator.columns else None,
            'valor_mes_atual': norm_num(row_extrator[col_valor_mes_atual]) if col_valor_mes_atual and col_valor_mes_atual in df_extrator.columns else None,
            'valor_vencimento': valor_vencimento,
            'valor_total_recebido': valor_extrator,
            'frequencia': frequencia,
            'valor_calculado': (
                valor_esperado if valor_esperado is not None else 
                valor_vencimento if valor_vencimento is not None else 
                (alternate_carga_match['valor'] if alternate_carga_match else None)
            ),
            'status': status,
            'diferenca_absoluta': diferenca_absoluta,
            'diferenca_percentual': diferenca_percentual,
            'justificativa': justificativa,
        }
        resultados.append(resultado)
        if diferenca_percentual is not None:
            debug_print(f"{nome_servidor}: {status}")
            debug_print(f"  → {justificativa}")
        else:
            debug_print(f"{nome_servidor}: {status}")
            debug_print(f"  → {justificativa}")

    debug_print(f"\n=== RESUMO ===")
    debug_print(f"Total: {len(resultados)}")
    debug_print(f"Corretos: {corretos}")
    debug_print(f"Verificar: {verificar}")
    debug_print(f"Incorretos: {incorretos}")
    debug_print(f"=== FIM ===\n")

    return {
        'sucesso': True,
        'resultados': resultados,
        'total': len(resultados),
        'corretos': corretos,
        'verificar': verificar,
        'incorretos': incorretos,
        'mes_referencia': mes_referencia,
    }
