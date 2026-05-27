import pandas as pd
import os

DEFAULT_FILE_PATH = "Dati Excel/Analisi Fitness Adidas Taglie.xlsx"

def list_excel_files(directory="Dati Excel"):
    if not os.path.exists(directory):
        return []
    return sorted(f for f in os.listdir(directory) if f.endswith('.xlsx'))

SIZE_ORDER = [
    '0/3M', '3/6M', '6/9M', '9/12M', '12/18M', '18/24M',
    '2/3A', '3/4A', '4/5A', '5/6A', '6/7A', '7/8A', '9/10A',
    '11/12A', '13/14A', '14/15A', '15/16A',
    'KXXL', 'KXL',
    'XXS', 'XS', 'S', 'SAB', 'M', 'MAB', 'L', 'LAB', 'XL', 'XXL',
    'UNICA'
]

def sort_sizes(sizes):
    ordered = [s for s in SIZE_ORDER if s in sizes]
    remaining = sorted(s for s in sizes if s not in SIZE_ORDER)
    return ordered + remaining

def _taglia_cat_dtype(taglie_values=None):
    if taglie_values is not None:
        all_sizes = set(taglie_values)
        categories = [s for s in SIZE_ORDER if s in all_sizes] + sorted(s for s in all_sizes if s not in SIZE_ORDER)
        return pd.CategoricalDtype(categories=categories, ordered=True)
    return pd.CategoricalDtype(categories=SIZE_ORDER, ordered=True)

def load_data(file_source=None):
    """Carica i dati dai due fogli Excel e standardizza i nomi delle colonne."""
    if file_source is None:
        file_source = DEFAULT_FILE_PATH
    
    if isinstance(file_source, str) and not os.path.exists(file_source):
        raise FileNotFoundError(f"File {file_source} non trovato.")
    
    # Carica fogli (pd.read_excel accetta sia stringhe che BytesIO)
    df_vend = pd.read_excel(file_source, sheet_name='VEND')
    df_acq = pd.read_excel(file_source, sheet_name='ACQ')
    
    # Rinomina colonne per evitare problemi con caratteri speciali (es. Quantit)
    df_vend.rename(columns=lambda x: x.strip(), inplace=True)
    df_acq.rename(columns=lambda x: x.strip(), inplace=True)
    
    # Mappa manuale per le colonne di quantità
    for col in df_vend.columns:
        if "Quantit" in col and "Venduta" in col:
            df_vend.rename(columns={col: "Qta_Venduta"}, inplace=True)
            
    for col in df_acq.columns:
        if "Quantit" in col and "acquistata" in col.lower():
            df_acq.rename(columns={col: "Qta_Acquistata"}, inplace=True)
            
    # Gestione delle date (rinominiamo per avere un campo Data unificato post-join o filtri)
    if 'Data Vendita' in df_vend.columns:
        df_vend['Data'] = pd.to_datetime(df_vend['Data Vendita'], errors='coerce')
    if 'Data Acquisto' in df_acq.columns:
        df_acq['Data'] = pd.to_datetime(df_acq['Data Acquisto'], errors='coerce')

    # Convertiamo tutte le colonne categoriche in stringhe gestendo valori nulli e decimali (es. 42.0 -> 42)
    cat_cols = ['Linea', 'Stagione', 'Taglia', 'Categoria', 'Produttore']
    for col in cat_cols:
        if col in df_vend.columns:
            df_vend[col] = df_vend[col].fillna('N.D. / Unica').astype(str).str.replace(r'\.0$', '', regex=True)
            df_vend[col] = df_vend[col].replace('nan', 'N.D. / Unica')
        if col in df_acq.columns:
            df_acq[col] = df_acq[col].fillna('N.D. / Unica').astype(str).str.replace(r'\.0$', '', regex=True)
            df_acq[col] = df_acq[col].replace('nan', 'N.D. / Unica')

    return df_vend, df_acq

def get_date_reference(df_vend, df_acq):
    dates = pd.concat([
        df_vend[['Data']].dropna(),
        df_acq[['Data']].dropna()
    ]).drop_duplicates().sort_values('Data')
    return dates

def get_date_options(dates, year=None, quarter=None, month=None):
    df = dates.copy()
    years = sorted(df['Data'].dt.year.unique())
    if year is not None:
        df = df[df['Data'].dt.year == year]
    quarters = sorted(df['Data'].dt.quarter.unique())
    if quarter is not None:
        df = df[df['Data'].dt.quarter == quarter]
    months = sorted(df['Data'].dt.month.unique())
    if month is not None:
        df = df[df['Data'].dt.month == month]
    days = sorted(df['Data'].dt.day.unique())
    return years, quarters, months, days

def filter_by_date(df, year=None, quarter=None, month=None, day=None):
    df_filtered = df.copy()
    if year is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.year == year]
    if quarter is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.quarter == quarter]
    if month is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.month == month]
    if day is not None:
        df_filtered = df_filtered[df_filtered['Data'].dt.day == day]
    return df_filtered

def get_filter_options(df_vend, df_acq):
    """Estrae le opzioni uniche per i filtri."""
    # Uniamo le opzioni di acquisti e vendite per avere una lista completa
    options = {}
    cols = ['Linea', 'Categoria', 'Stagione', 'Taglia', 'Produttore']
    
    for col in cols:
        v_opts = set(df_vend[col].dropna().unique()) if col in df_vend.columns else set()
        a_opts = set(df_acq[col].dropna().unique()) if col in df_acq.columns else set()
        combined = list(v_opts.union(a_opts))
        if col == 'Taglia':
            options[col] = sort_sizes(combined)
        else:
            options[col] = sorted(combined)
        
    return options

def filter_dataframe(df, filters):
    """Applica i filtri al dataframe."""
    df_filtered = df.copy()
    for col, values in filters.items():
        if values and len(values) > 0 and col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[col].isin(values)]
    return df_filtered

def merge_and_aggregate(df_vend, df_acq):
    """Aggrega per Taglia e Stagione, e calcola il Sell-Through Rate."""
    all_taglie = set()
    if 'Taglia' in df_vend.columns:
        all_taglie.update(df_vend['Taglia'].dropna().unique())
    if 'Taglia' in df_acq.columns:
        all_taglie.update(df_acq['Taglia'].dropna().unique())
    taglia_dtype = _taglia_cat_dtype(all_taglie)

    # Aggregazione Vendite
    agg_vend = df_vend.groupby('Taglia', observed=True)['Qta_Venduta'].sum().reset_index()
    
    # Aggregazione Acquisti
    agg_acq = df_acq.groupby('Taglia', observed=True)['Qta_Acquistata'].sum().reset_index()
    
    # Merge
    merged = pd.merge(agg_acq, agg_vend, on='Taglia', how='outer').fillna(0)
    merged['Taglia'] = merged['Taglia'].astype(taglia_dtype)
    merged = merged.sort_values('Taglia')
    
    # Se abbiamo anche la Stagione come raggruppamento (per la matrice avanzata)
    # Potremmo voler raggruppare per Taglia e Stagione
    agg_vend_stag = df_vend.groupby(['Taglia', 'Stagione'], observed=True)['Qta_Venduta'].sum().reset_index()
    agg_acq_stag = df_acq.groupby(['Taglia', 'Stagione'], observed=True)['Qta_Acquistata'].sum().reset_index()
    merged_stag = pd.merge(agg_acq_stag, agg_vend_stag, on=['Taglia', 'Stagione'], how='outer').fillna(0)
    merged_stag['Taglia'] = merged_stag['Taglia'].astype(taglia_dtype)
    merged_stag = merged_stag.sort_values('Taglia')
    
    # Calcolo Sell-Through Rate (Venduto / Acquistato)
    merged_stag['Sell_Through_%'] = (merged_stag['Qta_Venduta'] / merged_stag['Qta_Acquistata']) * 100
    # Gestione divisione per zero o NaN
    merged_stag['Sell_Through_%'] = merged_stag['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
    
    return merged_stag, merged

