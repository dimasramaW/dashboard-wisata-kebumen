import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Wisata Kebumen", layout="wide")

# --- 1. LOAD DATA ---
@st.cache_data 
def load_data():
    try:
        # BACA FILE DATA BERSIH
        # Pastikan file 'data_wisata_clean_final.csv' ada di satu folder dengan script ini
        df = pd.read_csv('data_wisata_clean_final.csv')
        
        # Urutkan Bulan (Januari - Desember)
        urutan_bulan = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        df['Bulan'] = pd.Categorical(df['Bulan'], categories=urutan_bulan, ordered=True)
        
        # Koordinat Lokasi (Mapping Hardcoded)
        koordinat = {
            'Goa Jatijajar': [-7.665, 109.432],
            'Goa Petruk': [-7.683, 109.418],
            'PAP Krakal': [-7.595, 109.704],
            'Pantai Logending': [-7.733, 109.390],
            'Pantai Petanahan': [-7.787, 109.583],
            'Pantai Suwuk': [-7.756, 109.475],
            'Waduk Sempor': [-7.558, 109.489],
            'Waduk Wadaslintang': [-7.584, 109.782]
        }
        # Masukkan koordinat ke DataFrame
        df['Lat'] = df['Nama_Wisata'].map(lambda x: koordinat.get(x, [None, None])[0])
        df['Long'] = df['Nama_Wisata'].map(lambda x: koordinat.get(x, [None, None])[1])
        
        return df
    except Exception as e:
        st.error(f"Gagal membaca data: {e}")
        return None

# Panggil fungsi load data
df = load_data()

# Jika data berhasil di-load, jalankan dashboard
if df is not None:
    
    # --- 2. SIDEBAR FILTER ---
    st.sidebar.header("Filter Dashboard")
    
    # Filter Tipe Wisatawan
    tipe_list = df['Tipe_Wisatawan'].unique().tolist()
    selected_tipe = st.sidebar.multiselect('Pilih Tipe Wisatawan:', tipe_list, default=tipe_list)

    # Filter Data Utama
    df_filtered = df[df['Tipe_Wisatawan'].isin(selected_tipe)]
    
    # Tombol Download Data
    st.sidebar.markdown("---")
    st.sidebar.subheader("Unduh Data")
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Data CSV",
        data=csv,
        file_name='data_wisata_filtered.csv',
        mime='text/csv'
    )

    # --- 3. DASHBOARD UTAMA ---
    st.title("🏝️ Dashboard Analisis Wisata Kebumen")
    st.markdown("Analisis interaktif tren kunjungan, sebaran lokasi, dan simulasi pendapatan daerah.")
    
    # --- KPI (ANGKA PENTING) ---
    total_pengunjung = df_filtered['Jumlah_Pengunjung'].sum()
    if not df_filtered.empty:
        top_wisata = df_filtered.groupby('Nama_Wisata')['Jumlah_Pengunjung'].sum().idxmax()
    else:
        top_wisata = "-"
    
    col1, col2 = st.columns(2)
    col1.metric("Total Pengunjung (2023)", f"{total_pengunjung:,.0f}")
    col2.metric("Objek Wisata Terpopuler", top_wisata)
    
    st.divider()

    # --- FITUR BARU: SIMULASI PENDAPATAN ---
    st.subheader("💵 Simulasi Pendapatan Daerah")
    col_input, col_hasil = st.columns(2)
    
    with col_input:
        harga_tiket = st.number_input("Masukkan Estimasi Harga Tiket (Rp):", min_value=0, value=10000, step=1000)
    
    with col_hasil:
        estimasi_pendapatan = total_pengunjung * harga_tiket
        st.metric("Potensi Omzet Tiket", f"Rp {estimasi_pendapatan:,.0f}")
        st.caption("*Angka ini dihitung otomatis: Total Pengunjung x Harga Tiket")

    st.divider()

    # --- PETA & BAR CHART ---
    col_kiri, col_kanan = st.columns([1, 1])

    with col_kiri:
        st.subheader("🗺️ Peta Interaktif (Google Maps Data)")
        
        # 1. Kamus Data Deskripsi & Rating
        info_wisata = {
            'Goa Jatijajar': {'rating': 4.6, 'desc': 'Gua kapur alam luas dengan sungai bawah tanah & diorama legenda.'},
            'Goa Petruk': {'rating': 4.5, 'desc': 'Petualangan susur gua alami (caving) yang menantang.'},
            'PAP Krakal': {'rating': 4.3, 'desc': 'Pemandian air panas alami bersejarah yang menenangkan.'},
            'Pantai Logending': {'rating': 4.3, 'desc': 'Wisata hutan bakau dan perahu menyusuri muara sungai.'},
            'Pantai Petanahan': {'rating': 4.4, 'desc': 'Pantai luas dengan hutan cemara udang yang rimbun.'},
            'Pantai Suwuk': {'rating': 4.4, 'desc': 'Pantai populer keluarga, ada kebun binatang mini & pesawat Boeing 737.'},
            'Waduk Sempor': {'rating': 4.6, 'desc': 'Bendungan indah dengan pemandangan perbukitan hijau & udara sejuk.'},
            'Waduk Wadaslintang': {'rating': 4.6, 'desc': 'Waduk raksasa dengan panorama eksotis mirip danau luar negeri.'}
        }
        
        # 2. Siapkan Data Peta
        map_data = df_filtered.groupby(['Nama_Wisata', 'Lat', 'Long'])['Jumlah_Pengunjung'].sum().reset_index()
        
        if not map_data.empty:
            # Pusatkan Peta
            m = folium.Map(location=[map_data.Lat.mean(), map_data.Long.mean()], zoom_start=11)
            
            for index, row in map_data.iterrows():
                nama = row['Nama_Wisata']
                total = row['Jumlah_Pengunjung']
                
                # Ambil detail dengan aman (pakai .strip() untuk hapus spasi rahasia)
                detail = info_wisata.get(nama.strip(), {'rating': '-', 'desc': 'Deskripsi belum tersedia.'})
                
                # Warna Marker (Merah = Ramai, Biru = Biasa)
                color = 'red' if total > 50000 else 'blue'
                
                # Desain Popup HTML
                html_popup = f"""
                <div style="font-family:sans-serif; width:220px">
                    <h4 style="margin-bottom:0px;">{nama}</h4>
                    <span style="background-color:green; color:white; padding:2px 6px; border-radius:4px; font-size:12px;">
                        ⭐ {detail['rating']}
                    </span>
                    <p style="font-size:12px; margin-top:8px; line-height:1.4;">{detail['desc']}</p>
                    <hr style="margin:5px 0;">
                    <b style="font-size:12px;">Total: {total:,.0f} Pengunjung</b>
                </div>
                """
                
                folium.Marker(
                    [row['Lat'], row['Long']], 
                    popup=folium.Popup(html_popup, max_width=250),
                    tooltip=nama,
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(m)
            
            st_folium(m, height=450)
        else:
            st.warning("Data kosong, silakan atur filter kembali.")

    with col_kanan:
        st.subheader("📊 Peringkat Terlaris")
        if not df_filtered.empty:
            fig, ax = plt.subplots(figsize=(8,6))
            bar_data = df_filtered.groupby('Nama_Wisata')['Jumlah_Pengunjung'].sum().sort_values(ascending=False).reset_index()
            sns.barplot(data=bar_data, y='Nama_Wisata', x='Jumlah_Pengunjung', palette='viridis', ax=ax)
            ax.set_ylabel("") # Hilangkan label sumbu Y biar bersih
            st.pyplot(fig)

    # --- TREN BULANAN ---
    st.subheader("📈 Tren Kunjungan Per Bulan")
    if not df_filtered.empty:
        fig2, ax2 = plt.subplots(figsize=(10,4))
        tren_data = df_filtered.groupby(['Bulan', 'Nama_Wisata'])['Jumlah_Pengunjung'].sum().reset_index()
        sns.lineplot(data=tren_data, x='Bulan', y='Jumlah_Pengunjung', hue='Nama_Wisata', marker='o', ax=ax2)
        plt.legend(bbox_to_anchor=(1, 1))
        plt.grid(True, alpha=0.3)
        st.pyplot(fig2)