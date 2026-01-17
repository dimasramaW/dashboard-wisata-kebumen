import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# --- 1. KONFIGURASI HALAMAN & CSS ---
st.set_page_config(page_title="Dashboard Analisis Kinerja dan Pemetaan Potensi Objek Wisata Kabupaten Kebumen", layout="wide")

st.markdown("""
<style>
    /* PADDING HALAMAN */
    .block-container {
        padding-top: 3.5rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* GAP ANTAR ELEMEN */
    div[data-testid="stVerticalBlock"] > div {
        gap: 1rem;
    }
    
    div[data-testid="column"] {
        padding: 5px;
    }

    /* --- STYLE JUDUL CHART (CARD STYLE) --- */
    .chart-title {
        font-size: 14px;
        font-weight: 700;
        color: #333333 !important;
        background-color: #ffffff;
        padding: 12px 15px;       
        border-radius: 10px;      
        box-shadow: 0 0 15px rgba(0,0,0,0.08); 
        margin-bottom: 10px;
        margin-top: 5px;
        text-align: center;
        border: none;             
    }

    /* --- STYLE UNTUK GAMBAR GRAFIK --- */
    div[data-testid="stImage"] > img {
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0,0,0,0.08); 
        padding: 1px;
        background-color: white; 
        width: 100% !important;
    }

    /* --- STYLE UNTUK PETA --- */
    iframe {
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0,0,0,0.08); 
        background-color: white;
    }

</style>
""", unsafe_allow_html=True)

# Fungsi Card Panel Kiri
def make_side_card(title, value, unit, color):
    st.markdown(f"""
    <div style="
        background-color: {color}; 
        padding: 15px; 
        border-radius: 10px; 
        color: white; 
        margin-bottom: 15px; 
        box-shadow: 0 0 15px rgba(0,0,0,0.1); 
    ">
        <div style="font-size: 20px; font-weight: bold;">{value}</div>
        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">{title}</div>
        <div style="font-size: 10px; opacity: 0.8; margin-top:2px">{unit}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. LOAD DATA ---
@st.cache_data 
def load_data():
    try:
        df = pd.read_csv('data_wisata_clean_final.csv')
        urutan_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        df['Bulan'] = pd.Categorical(df['Bulan'], categories=urutan_bulan, ordered=True)
        
        koordinat = {
            'Goa Jatijajar': [-7.665, 109.432], 'Goa Petruk': [-7.683, 109.418],
            'PAP Krakal': [-7.595, 109.704], 'Pantai Logending': [-7.733, 109.390],
            'Pantai Petanahan': [-7.787, 109.583], 'Pantai Suwuk': [-7.756, 109.475],
            'Waduk Sempor': [-7.558, 109.489], 'Waduk Wadaslintang': [-7.584, 109.782]
        }
        df['Lat'] = df['Nama_Wisata'].map(lambda x: koordinat.get(x, [None, None])[0])
        df['Long'] = df['Nama_Wisata'].map(lambda x: koordinat.get(x, [None, None])[1])
        return df
    except Exception as e:
        return None

df = load_data()

# --- 3. DASHBOARD LOGIC ---
if df is not None:
    
    with st.sidebar:
        st.header("⚙️ Filter")
        tipe_list = df['Tipe_Wisatawan'].unique().tolist()
        selected_tipe = st.multiselect('User Type:', tipe_list, default=tipe_list)
        df_filtered = df[df['Tipe_Wisatawan'].isin(selected_tipe)]
        st.markdown("---")
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "data_wisata.csv", "text/csv")

    col_panel, col_content = st.columns([1, 5]) 

    # --- DEFINISI DATA DETAIL UNTUK PETA & KPI ---
    info_wisata = {
        'Goa Jatijajar': {'rating': 4.3, 'desc': 'Goa kapur alam dengan sungai bawah tanah.'}, 
        'Goa Petruk': {'rating': 4.4, 'desc': 'Wisata susur goa alami yang menantang.'}, 
        'PAP Krakal': {'rating': 4.1, 'desc': 'Pemandian air panas alami bersejarah.'}, 
        'Pantai Logending': {'rating': 4.2, 'desc': 'Wisata hutan bakau dan muara sungai.'}, 
        'Pantai Petanahan': {'rating': 4.2, 'desc': 'Pantai luas dengan hutan cemara udang.'}, 
        'Pantai Suwuk': {'rating': 4.3, 'desc': 'Pantai keluarga dengan kebun binatang mini.'}, 
        'Waduk Sempor': {'rating': 4.5, 'desc': 'Bendungan dengan pemandangan perbukitan hijau.'}, 
        'Waduk Wadaslintang': {'rating': 4.5, 'desc': 'Waduk raksasa dengan panorama eksotis.'}
    }

    # === PANEL KIRI ===
    with col_panel:
        total_pengunjung = df_filtered['Jumlah_Pengunjung'].sum()
        total_objek = df_filtered['Nama_Wisata'].nunique()
        top_wisata = df_filtered.groupby('Nama_Wisata')['Jumlah_Pengunjung'].sum().idxmax() if not df_filtered.empty else "-"
        
        rata_rating = sum(d['rating'] for d in info_wisata.values()) / len(info_wisata)

        make_side_card(f"{total_pengunjung:,.0f}", "JUMLAH PENGUNJUNG", "Total 2023", "#4FC3F7")
        make_side_card(f"{total_objek}", "JUMLAH OBJEK WISATA", "Objek Aktif", "#29B6F6")
        # PERBAIKAN 1: Menampilkan nama lengkap (tidak di-split)
        make_side_card(top_wisata, "WISATA FAVORIT", "Terfavorit", "#039BE5")
        make_side_card(f"{rata_rating:.1f}", "RATA-RATA RATING", "Kepuasan", "#0277BD")

    # === KONTEN KANAN ===
    with col_content:
        st.subheader("Dashboard Analisis Kinerja dan Pemetaan Potensi Objek Wisata Kabupaten Kebumen")
        
        # --- ROW 1: TREN & MAP ---
        c_tren, c_map = st.columns([1.5, 1])
        
        with c_tren:
            st.markdown('<div class="chart-title">Traffic Wisata Bulanan</div>', unsafe_allow_html=True)
            if not df_filtered.empty:
                tren_data = df_filtered.groupby(['Bulan', 'Nama_Wisata'])['Jumlah_Pengunjung'].sum().reset_index()
                fig, ax = plt.subplots(figsize=(8, 3.1)) 
                sns.lineplot(data=tren_data, x='Bulan', y='Jumlah_Pengunjung', hue='Nama_Wisata', marker='o', ax=ax, legend=False)
                ax.set_xlabel("")
                ax.set_ylabel("")
                ax.tick_params(axis='both', labelsize=8)
                ax.grid(True, alpha=0.3, linestyle='--')
                sns.despine()
                plt.tight_layout(pad=0.5) 
                st.pyplot(fig, use_container_width=True)

        with c_map:
            st.markdown('<div class="chart-title">Peta Sebaran Lokasi</div>', unsafe_allow_html=True)
            map_data = df_filtered.groupby(['Nama_Wisata', 'Lat', 'Long'])['Jumlah_Pengunjung'].sum().reset_index()
            if not map_data.empty:
                m = folium.Map(location=[-7.65, 109.6], zoom_start=10, tiles="CartoDB positron")
                for _, row in map_data.iterrows():
                    color = 'red' if row['Jumlah_Pengunjung'] > 50000 else '#039BE5'
                    
                    # PERBAIKAN 2: Menambahkan Popup HTML Lengkap
                    nama = row['Nama_Wisata']
                    total = row['Jumlah_Pengunjung']
                    detail = info_wisata.get(nama.strip(), {'rating': '-', 'desc': ''})
                    
                    html_popup = f"""
                    <div style="font-family:sans-serif; width:200px">
                        <h5 style="margin-bottom:0px; color:#333">{nama}</h5>
                        <span style="background-color:#2ecc71; color:white; padding:2px 6px; border-radius:3px; font-size:11px;">⭐ {detail['rating']}</span>
                        <p style="font-size:11px; margin-top:5px; color:#555">{detail['desc']}</p>
                        <hr style="margin:5px 0; border-top: 1px solid #eee;">
                        <b style="font-size:11px; color:#333">Total: {total:,.0f}</b>
                    </div>
                    """
                    
                    folium.CircleMarker(
                        [row['Lat'], row['Long']], radius=row['Jumlah_Pengunjung']/30000,
                        color=color, fill=True, fill_color=color, fill_opacity=0.7,
                        popup=folium.Popup(html_popup, max_width=250),
                        tooltip=nama
                    ).add_to(m)
                st_folium(m, height=290, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ROW 2: TIGA GRAFIK SIMETRIS ---
        c1, c2, c3 = st.columns(3)
        FIXED_FIGSIZE = (5, 4) 

        # 1. DONUT CHART
        with c1:
            st.markdown('<div class="chart-title">Kategori Minat</div>', unsafe_allow_html=True)
            if not df_filtered.empty:
                def get_kategori(nama):
                    if 'Pantai' in nama: return 'Pantai'
                    elif 'Goa' in nama: return 'Goa'
                    elif 'Waduk' in nama: return 'Waduk'
                    else: return 'Pemandian'
                df_pie = df_filtered.copy()
                df_pie['Kategori'] = df_pie['Nama_Wisata'].apply(get_kategori)
                data_pie = df_pie.groupby('Kategori')['Jumlah_Pengunjung'].sum().sort_values(ascending=False)
                
                fig_pie, ax_pie = plt.subplots(figsize=FIXED_FIGSIZE)
                colors = sns.color_palette('pastel')[0:len(data_pie)]
                ax_pie.pie(data_pie, labels=data_pie.index, autopct='%1.0f%%', startangle=90, colors=colors, wedgeprops={'width': 0.4}, textprops={'fontsize': 9})
                plt.tight_layout(pad=1.0) 
                st.pyplot(fig_pie, use_container_width=True)

        # 2. STACKED BAR CHART
        with c2:
            st.markdown('<div class="chart-title">Asal Pengunjung</div>', unsafe_allow_html=True)
            if not df_filtered.empty:
                chart_data = df_filtered.pivot_table(index='Nama_Wisata', columns='Tipe_Wisatawan', values='Jumlah_Pengunjung', aggfunc='sum').fillna(0)
                chart_data['Total'] = chart_data.sum(axis=1)
                chart_data = chart_data.sort_values('Total', ascending=True).drop(columns='Total')
                
                fig_bar, ax_bar = plt.subplots(figsize=FIXED_FIGSIZE)
                chart_data.plot(kind='barh', stacked=True, color=['#FFA07A', '#6A5ACD'], ax=ax_bar, width=0.8)
                ax_bar.set_ylabel("")
                ax_bar.set_xlabel("")
                ax_bar.tick_params(labelsize=8)
                ax_bar.legend(loc='lower right', fontsize=7, frameon=False)
                sns.despine(left=True, bottom=True)
                plt.tight_layout(pad=1.0) 
                st.pyplot(fig_bar, use_container_width=True)

        # 3. SCATTER PLOT
        with c3:
            st.markdown('<div class="chart-title">Rating vs Kunjungan</div>', unsafe_allow_html=True)
            if not df_filtered.empty:
                scatter_data = df_filtered.groupby('Nama_Wisata')['Jumlah_Pengunjung'].sum().reset_index()
                # Ambil rating dari info_wisata
                scatter_data['Rating'] = scatter_data['Nama_Wisata'].map(lambda x: info_wisata.get(x.strip(), {}).get('rating', 0))
                
                fig_scat, ax_scat = plt.subplots(figsize=FIXED_FIGSIZE)
                sns.scatterplot(data=scatter_data, x='Rating', y='Jumlah_Pengunjung', s=200, color='#6C63FF', alpha=0.9, ax=ax_scat)
                
                for i in range(scatter_data.shape[0]):
                    ax_scat.text(scatter_data.Rating[i], scatter_data.Jumlah_Pengunjung[i]+5000, 
                                 scatter_data.Nama_Wisata[i], fontsize=7, ha='center', color='#444')
                
                ax_scat.set_xlabel("Rating", fontsize=8)
                ax_scat.set_ylabel("", fontsize=8)
                ax_scat.tick_params(labelsize=8)
                ax_scat.grid(True, linestyle='--', alpha=0.3)
                sns.despine()
                plt.tight_layout(pad=1.0) 
                st.pyplot(fig_scat, use_container_width=True)
