import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_engine import load_data, get_filter_options, filter_dataframe, merge_and_aggregate, get_date_reference, get_date_options, filter_by_date, list_excel_files

st.set_page_config(page_title="Analisi Taglie | Dashboard", layout="wide", initial_sidebar_state="collapsed")

with open("style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- CARICAMENTO FILE (Upload o Stato) ---
if 'df_vend_raw' not in st.session_state:
    st.session_state.df_vend_raw = None
    st.session_state.df_acq_raw = None
    st.session_state.file_name = None

if st.session_state.df_vend_raw is None:
    st.title("Esplorazione Dati Taglie")
    st.markdown("Carica un file Excel per iniziare l'analisi.")

    col_up1, col_up2 = st.columns(2)

    with col_up1:
        st.markdown("**File dalla cartella Dati Excel**")
        files_disponibili = list_excel_files()
        if files_disponibili:
            sel_file = st.selectbox("", files_disponibili, label_visibility="collapsed", key="file_select")
            if st.button("Analizza file selezionato", type="primary", use_container_width=True):
                try:
                    df_vend_raw, df_acq_raw = load_data(f"Dati Excel/{sel_file}")
                    st.session_state.df_vend_raw = df_vend_raw
                    st.session_state.df_acq_raw = df_acq_raw
                    st.session_state.file_name = sel_file
                    st.success(f"Caricato: {sel_file}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore nel caricamento del file: {e}")
        else:
            st.info("Nessun file .xlsx trovato nella cartella Dati Excel.")

    with col_up2:
        st.markdown("**Oppure carica un file dal computer**")
        uploaded_file = st.file_uploader("", type=['xlsx'], label_visibility="collapsed")

        if uploaded_file is not None:
            try:
                df_vend_raw, df_acq_raw = load_data(uploaded_file)
                st.session_state.df_vend_raw = df_vend_raw
                st.session_state.df_acq_raw = df_acq_raw
                st.session_state.file_name = uploaded_file.name
                st.rerun()
            except Exception as e:
                st.error(f"Errore nel caricamento del file: {e}")

    st.caption("Formato richiesto: file **.xlsx** con fogli **VEND** (Vendite) e **ACQ** (Acquisti).")
    st.stop()

df_vend_raw = st.session_state.df_vend_raw
df_acq_raw = st.session_state.df_acq_raw

filter_opts = get_filter_options(df_vend_raw, df_acq_raw)

# ==========================================
# LAYOUT PRINCIPALE (Bento-Grid)
# ==========================================
st.title("Esplorazione Dati Taglie")
col_title, col_new = st.columns([6, 1])
with col_title:
    st.markdown("Analisi incrociata di Acquisti e Vendite per ottimizzare lo stock.")
    st.caption(f"File: {st.session_state.file_name}")
with col_new:
    if st.button("← Nuova Analisi", use_container_width=True):
        st.session_state.df_vend_raw = None
        st.session_state.df_acq_raw = None
        st.session_state.file_name = None
        st.rerun()

# 3. Filtri Fissi Superiori
st.markdown("### Filtri Ricerca")
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
with f_col1:
    selected_linee = st.multiselect("Linea", filter_opts.get('Linea', []), placeholder="Tutte le Linee")
with f_col2:
    selected_cat = st.multiselect("Categoria", filter_opts.get('Categoria', []), placeholder="Tutte le Categorie")
with f_col3:
    selected_stag = st.multiselect("Stagione", filter_opts.get('Stagione', []), placeholder="Tutte le Stagioni")
with f_col4:
    selected_taglie = st.multiselect("Taglia", filter_opts.get('Taglia', []), placeholder="Tutte le Taglie")
with f_col5:
    selected_prod = st.multiselect("Produttore", filter_opts.get('Produttore', []), placeholder="Tutti i Produttori")

st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# Crea dizionario filtri
filters = {
    'Linea': selected_linee,
    'Categoria': selected_cat,
    'Stagione': selected_stag,
    'Taglia': selected_taglie,
    'Produttore': selected_prod
}

# 4. Applica Filtri (Categoria)
df_vend = filter_dataframe(df_vend_raw, filters)
df_acq = filter_dataframe(df_acq_raw, filters)

# 4.5 Filtri Temporali
st.markdown("### Filtri Temporali")
date_ref = get_date_reference(df_vend_raw, df_acq_raw)
min_d = date_ref['Data'].min().strftime('%d/%m/%Y')
max_d = date_ref['Data'].max().strftime('%d/%m/%Y')
st.caption(f"Periodo disponibile: {min_d} → {max_d}")

d_col1, d_col2, d_col3, d_col4 = st.columns(4)

with d_col1:
    years, _, _, _ = get_date_options(date_ref)
    year_opts = ["Tutti"] + [str(int(y)) for y in years]
    sel_year = st.selectbox("Anno", year_opts, key="year_filter")

year_val = int(sel_year) if sel_year != "Tutti" else None

with d_col2:
    _, q_avail, _, _ = get_date_options(date_ref, year=year_val)
    q_opts = ["Tutti"] + [f"Q{int(q)}" for q in q_avail]
    sel_quarter = st.selectbox("Trimestre", q_opts, key="quarter_filter")

quarter_val = int(sel_quarter[1]) if sel_quarter != "Tutti" else None

with d_col3:
    _, _, m_avail, _ = get_date_options(date_ref, year=year_val, quarter=quarter_val)
    mesi = {1:"Gen",2:"Feb",3:"Mar",4:"Apr",5:"Mag",6:"Giu",
            7:"Lug",8:"Ago",9:"Set",10:"Ott",11:"Nov",12:"Dic"}
    m_opts = ["Tutti"] + [f"{int(m)} - {mesi[m]}" for m in m_avail]
    sel_month = st.selectbox("Mese", m_opts, key="month_filter")

month_val = int(sel_month.split(" - ")[0]) if sel_month != "Tutti" else None

with d_col4:
    _, _, _, d_avail = get_date_options(date_ref, year=year_val, quarter=quarter_val, month=month_val)
    d_opts = ["Tutti"] + [str(int(d)) for d in d_avail]
    sel_day = st.selectbox("Giorno", d_opts, key="day_filter")

day_val = int(sel_day) if sel_day != "Tutti" else None

df_vend = filter_by_date(df_vend, year=year_val, quarter=quarter_val, month=month_val, day=day_val)
df_acq = filter_by_date(df_acq, year=year_val, quarter=quarter_val, month=month_val, day=day_val)

st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# 5. Aggregazione
df_stag, df_tot = merge_and_aggregate(df_vend, df_acq)

# --- SEZIONE 1: KPI (Metriche in evidenza) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    tot_acq = df_tot['Qta_Acquistata'].sum()
    st.metric("Totale Acquistato", f"{int(tot_acq):,}".replace(",", "."))
with col2:
    tot_vend = df_tot['Qta_Venduta'].sum()
    st.metric("Totale Venduto", f"{int(tot_vend):,}".replace(",", "."))
with col3:
    sell_through = (tot_vend / tot_acq * 100) if tot_acq > 0 else 0
    st.metric("Sell-Through %", f"{sell_through:.1f}%")
with col4:
    taglie_attive = df_tot[df_tot['Qta_Acquistata'] > 0]['Taglia'].nunique()
    st.metric("Taglie Analizzate", f"{taglie_attive}")

st.markdown("<br>", unsafe_allow_html=True)

# --- SEZIONE 2: GRAFICI REATTIVI ---
# Colori stile Perplexity (blu notte, slate, accenti chiari)
COLOR_ACQ = "#3b82f6" # Blu 500
COLOR_VEND = "#f59e0b" # Ambra 500

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Andamento per Taglia")
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=df_tot['Taglia'], y=df_tot['Qta_Acquistata'], name='Acquistato', marker_color=COLOR_ACQ))
    fig_bar.add_trace(go.Bar(x=df_tot['Taglia'], y=df_tot['Qta_Venduta'], name='Venduto', marker_color=COLOR_VEND))
    
    fig_bar.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", color="#475569")
    )
    fig_bar.update_yaxes(gridcolor='#f1f5f9')
    fig_bar.update_xaxes(type='category', title_text='')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.subheader("Trend Sell-Through per Taglie")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_tot['Taglia'], y=df_tot['Qta_Acquistata'], mode='lines+markers', name='Acquistato', line=dict(color=COLOR_ACQ, width=2)))
    fig_line.add_trace(go.Scatter(x=df_tot['Taglia'], y=df_tot['Qta_Venduta'], mode='lines+markers', name='Venduto', line=dict(color=COLOR_VEND, width=3)))
    
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", color="#475569")
    )
    fig_line.update_yaxes(gridcolor='#f1f5f9')
    fig_line.update_xaxes(type='category', title_text='')
    st.plotly_chart(fig_line, use_container_width=True)

# --- SEZIONE 2.5: CATEGORIA E PRODUTTORI ---
st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)

cat_vend = df_vend.groupby('Categoria')['Qta_Venduta'].sum().reset_index()
cat_acq = df_acq.groupby('Categoria')['Qta_Acquistata'].sum().reset_index()
cat_agg = pd.merge(cat_acq, cat_vend, on='Categoria', how='outer').fillna(0)
cat_agg = cat_agg.sort_values('Qta_Venduta', ascending=False)

prod_chart_acq = df_acq.groupby('Produttore')['Qta_Acquistata'].sum().reset_index()
prod_chart_vend = df_vend.groupby('Produttore')['Qta_Venduta'].sum().reset_index()
prod_chart = pd.merge(prod_chart_acq, prod_chart_vend, on='Produttore', how='outer').fillna(0)
prod_chart = prod_chart.sort_values('Qta_Acquistata', ascending=False).head(15).reset_index(drop=True)

col_cp1, col_cp2 = st.columns(2)

with col_cp1:
    st.subheader("Andamento per Categoria")

    fig_cat_bar = go.Figure()
    fig_cat_bar.add_trace(go.Bar(
        x=cat_agg['Categoria'], y=cat_agg['Qta_Acquistata'],
        name='Acquistato', marker_color=COLOR_ACQ
    ))
    fig_cat_bar.add_trace(go.Bar(
        x=cat_agg['Categoria'], y=cat_agg['Qta_Venduta'],
        name='Venduto', marker_color=COLOR_VEND
    ))

    fig_cat_bar.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", color="#475569")
    )
    fig_cat_bar.update_yaxes(gridcolor='#f1f5f9', title='Quantità')
    fig_cat_bar.update_xaxes(type='category', title_text='')

    st.plotly_chart(fig_cat_bar, use_container_width=True)

with col_cp2:
    st.subheader("Andamento per Produttore")

    fig_prod_bar = go.Figure()
    fig_prod_bar.add_trace(go.Bar(
        x=prod_chart['Produttore'], y=prod_chart['Qta_Acquistata'],
        name='Acquistato', marker_color=COLOR_ACQ
    ))
    fig_prod_bar.add_trace(go.Bar(
        x=prod_chart['Produttore'], y=prod_chart['Qta_Venduta'],
        name='Venduto', marker_color=COLOR_VEND
    ))

    fig_prod_bar.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", color="#475569")
    )
    fig_prod_bar.update_yaxes(gridcolor='#f1f5f9', title='Quantità')
    fig_prod_bar.update_xaxes(type='category', title_text='', tickangle=45)

    st.plotly_chart(fig_prod_bar, use_container_width=True)

# --- SEZIONE 2.7: VENDITE PER NEGOZIO ---
st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
st.subheader("Vendite per Negozio")

negozi_agg = df_vend.groupby('Negozio')['Qta_Venduta'].sum().reset_index()
negozi_agg = negozi_agg.sort_values('Qta_Venduta', ascending=True)

fig_negozi = go.Figure()
fig_negozi.add_trace(go.Bar(
    x=negozi_agg['Qta_Venduta'],
    y=negozi_agg['Negozio'],
    orientation='h',
    marker_color=COLOR_VEND,
    name='Venduto'
))

fig_negozi.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=20, b=20),
    font=dict(family="Inter, sans-serif", color="#475569")
)
fig_negozi.update_yaxes(gridcolor='#f1f5f9')
fig_negozi.update_xaxes(title='Quantità Venduta', gridcolor='#f1f5f9')

st.plotly_chart(fig_negozi, use_container_width=True)

# --- SEZIONE 3: MATRICE DATI AVANZATA ---
st.subheader("Matrice Taglie")
st.markdown("Esplora i dati per Stagione e Taglia. Clicca sulle intestazioni per ordinare.")

display_df = df_stag.copy()
display_df = display_df[['Taglia', 'Stagione', 'Qta_Acquistata', 'Qta_Venduta', 'Sell_Through_%']]
display_df.rename(columns={
    'Qta_Acquistata': 'Somma Q.tà Acquistata',
    'Qta_Venduta': 'Somma Q.tà Venduta'
}, inplace=True)

def _c_str(val):
    if pd.isna(val):
        return 'color: #d1d5db'
    if val < 30:
        return 'color: #dc2626; font-weight: 600'
    if val < 70:
        return 'color: #d97706; font-weight: 600'
    return 'color: #16a34a; font-weight: 600'

styled = (
    display_df.style
    .map(_c_str, subset=['Sell_Through_%'])
    .format({
        'Somma Q.tà Acquistata': '{:.0f}',
        'Somma Q.tà Venduta': '{:.0f}',
        'Sell_Through_%': '{:.1f}%'
    })
)

st.dataframe(
    styled,
    use_container_width=True,
    height=400
)

# --- SEZIONE 4: MATRICE PRODUTTORI ---
st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
st.subheader("Matrice Produttori")
st.markdown("Esplora i dati per Produttore.")

agg_acq_prod = df_acq.groupby('Produttore')['Qta_Acquistata'].sum().reset_index()
agg_vend_prod = df_vend.groupby('Produttore')['Qta_Venduta'].sum().reset_index()
prod_merged = pd.merge(agg_acq_prod, agg_vend_prod, on='Produttore', how='outer').fillna(0)
prod_merged['Sell_Through_%'] = (prod_merged['Qta_Venduta'] / prod_merged['Qta_Acquistata']) * 100
prod_merged['Sell_Through_%'] = prod_merged['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
prod_merged = prod_merged.sort_values('Qta_Acquistata', ascending=False).reset_index(drop=True)

prod_display = prod_merged.rename(columns={
    'Qta_Acquistata': 'Somma Q.tà Acquistata',
    'Qta_Venduta': 'Somma Q.tà Venduta'
})

prod_styled = (
    prod_display.style
    .map(_c_str, subset=['Sell_Through_%'])
    .format({
        'Somma Q.tà Acquistata': '{:.0f}',
        'Somma Q.tà Venduta': '{:.0f}',
        'Sell_Through_%': '{:.1f}%'
    })
)

st.dataframe(
    prod_styled,
    use_container_width=True,
    height=400
)

# --- SEZIONE 5: MATRICE CATEGORIA ---
st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
st.subheader("Matrice Categoria")
st.markdown("Esplora i dati per Categoria.")

agg_acq_cat = df_acq.groupby('Categoria')['Qta_Acquistata'].sum().reset_index()
agg_vend_cat = df_vend.groupby('Categoria')['Qta_Venduta'].sum().reset_index()
cat_merged = pd.merge(agg_acq_cat, agg_vend_cat, on='Categoria', how='outer').fillna(0)
cat_merged['Sell_Through_%'] = (cat_merged['Qta_Venduta'] / cat_merged['Qta_Acquistata']) * 100
cat_merged['Sell_Through_%'] = cat_merged['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
cat_merged = cat_merged.sort_values('Qta_Acquistata', ascending=False).reset_index(drop=True)

cat_display = cat_merged.rename(columns={
    'Qta_Acquistata': 'Somma Q.tà Acquistata',
    'Qta_Venduta': 'Somma Q.tà Venduta'
})

cat_styled = (
    cat_display.style
    .map(_c_str, subset=['Sell_Through_%'])
    .format({
        'Somma Q.tà Acquistata': '{:.0f}',
        'Somma Q.tà Venduta': '{:.0f}',
        'Sell_Through_%': '{:.1f}%'
    })
)

st.dataframe(
    cat_styled,
    use_container_width=True,
    height=400
)

# --- SEZIONE 6: MATRICE LINEA ---
st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-color: #e2e8f0;'>", unsafe_allow_html=True)
st.subheader("Matrice Linea")
st.markdown("Esplora i dati per Linea.")

agg_acq_linea = df_acq.groupby('Linea')['Qta_Acquistata'].sum().reset_index()
agg_vend_linea = df_vend.groupby('Linea')['Qta_Venduta'].sum().reset_index()
linea_merged = pd.merge(agg_acq_linea, agg_vend_linea, on='Linea', how='outer').fillna(0)
linea_merged['Sell_Through_%'] = (linea_merged['Qta_Venduta'] / linea_merged['Qta_Acquistata']) * 100
linea_merged['Sell_Through_%'] = linea_merged['Sell_Through_%'].replace([float('inf'), -float('inf')], 0).fillna(0)
linea_merged = linea_merged.sort_values('Qta_Acquistata', ascending=False).reset_index(drop=True)

linea_display = linea_merged.rename(columns={
    'Qta_Acquistata': 'Somma Q.tà Acquistata',
    'Qta_Venduta': 'Somma Q.tà Venduta'
})

linea_styled = (
    linea_display.style
    .map(_c_str, subset=['Sell_Through_%'])
    .format({
        'Somma Q.tà Acquistata': '{:.0f}',
        'Somma Q.tà Venduta': '{:.0f}',
        'Sell_Through_%': '{:.1f}%'
    })
)

st.dataframe(
    linea_styled,
    use_container_width=True,
    height=400
)
