# Ringkasan metode https://docs.google.com/presentation/d/1NRoo3JaLD6NnSfvdpuX3OEjBxbMEdbo-7RXBzXfyT5o/edit?usp=sharing 
# ==== packages ====
import streamlit as st
import pickle
from pathlib import Path
import pandas as pd  # pip install pandas openpyxl
import numpy as np
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import time
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import warnings
warnings.filterwarnings("ignore")
from scipy.stats import shapiro, norm, poisson
import matplotlib.pyplot as plt
import plotly.express as px

# ===== NAMA WEB ====
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Stock Calculation Dashboard", page_icon=":bar_chart:", layout="wide")

# ========================= USER AUTHENTICATION ========================
names = ["pupuk indonesia", "data science"]
usernames = ["ppuk2022", "ds2022"]

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboardd", "asdfgh", cookie_expiry_days=16)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.info("Please enter your username and password")

if authentication_status:

# ======================== JUDUL ===========================
    #st.set_page_config(layout="centered", initial_sidebar_state="auto")
    st.markdown("<h3 style='text-align: center;'>STOCK CALCULATION SPAREPART </h3>", unsafe_allow_html=True)

    #Sidebar. Packages custom tampilan
    import os
    from PIL import Image
    from streamlit_option_menu import option_menu

    #Loading
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.005)
        my_bar.progress(percent_complete + 1)

    col1, col2 = st.columns([2,2])

    # ====================================== LOADING DATASET ==================================
    dataset = pd.read_csv("dataset_update_material.csv")

    #======================================= MENU SIDEBAR =====================================
    authenticator.logout("Logout", "sidebar")
    with st.sidebar:
        directory_path = os.path.dirname(__file__)
        image = Image.open(os.path.join(directory_path, 'test2.png'))
        pad1, pad2, pad3 = st.columns([2,8,1])

        with pad2:
            st.image(image, output_format='png', width=170)
        
        #---MENU
        selected = option_menu("", ['Home',"Dataset","Calculator"], 
        icons=['graph', 'graph', 'graph'], menu_icon="cast", default_index=0)
        
    st.subheader("Halo,")
    
    # IF HOME
    if selected == "Home":
        directory_path = os.path.dirname(__file__)
        hc1, hc2 = st.columns([4,4])
        
        with hc1:
            st.markdown("Stok Calculation tool merupakan alat analisis untuk mendapatkan perhitungan stok sparepart optimum terkhusus pada sparepart tipe statis. Alat ini digunakan diharapkan dapat meminimasi downtime mesin akibat dari ketidakfungsian sparepart yang kerusakannya tidak terduga.")
            st.markdown("Penentuan banyaknya stok sparepart berdasarkan service level, failure rate sparepart, dan leadtime pengadaan.")
            st.markdown("**Note**: Calculator Uses in Slow and Non Moving SpareParts SAP Data")
            st.write("Download User Guides [Click](https://drive.google.com/file/d/1kjZIwnPvYDv5zQHMvhIrQKD_I5nJPJI9/view?usp=sharing)")
        with hc2:
            st.markdown("![Alt Text](https://media2.giphy.com/media/l46Cy1rHbQ92uuLXa/giphy.gif)")
    
    # IF DATASET
    elif selected == "Dataset":
        st.info('Untuk mengetahui daftar material silahkan cek data dengan menggunakan menu filter', icon="ℹ️")
        dataset2 = pd.read_csv("dataset display.csv")
        
        clist1 = dataset2['Anper'].unique()
        werks_input0 = st.selectbox("Select a Anak Perusahaan:",options= clist1)
        dataset2 = dataset2[(dataset2["Anper"] == werks_input0)]
        st.write(dataset2) 
        clist2 = dataset2['Material'].unique() 
        ematn_input0 = st.selectbox("Select a Material:",options= clist2,index=0)
        dataset = dataset2[(dataset2["Material"] == ematn_input0)]
        st.write(dataset) 

    # IF CALCULATOR
    # Pada menu calculator terdapat modeling 
    elif selected == "Calculator":
        Simulation1, Simulation2 = st.tabs(["Simulation - Equipment", "Simulation - Material"])
        # ============================= Submenu Simulation - Equipment =================================
        with Simulation1:
            col1, padding, col2 = st.columns((6,1.5,15))
            with col1:
                clist1 = dataset['Anper'].unique()
                werks_input = st.selectbox("Select a Anak Perusahaan:",options= clist1)
                dataset2 = dataset[(dataset["Anper"] == werks_input)]
                clist2 = dataset2['nama_material'].unique() 
                ematn_input = st.selectbox("Select a Material:",options= clist2)
                dataset3 = dataset2[(dataset2["nama_material"] == ematn_input)]
                clist3 = dataset3['EQUNR'].unique()
                equnr_input = st.selectbox("Select a Equipment:",options= clist3)
                sparepart_input = st.number_input("Jumlah Komponen Terpasang",value =1,min_value=1)
                equipment_input = st.number_input("Jumlah Equipment",max_value=24, min_value=1,value =1)
                service_levell = st.number_input("Service Level (%)",max_value=100, min_value=1,value =98)

                ########### filter data untuk perhitungan #############            
                df1 = dataset[(dataset.Anper == werks_input) &(dataset.EQUNR == equnr_input) & (dataset.nama_material == ematn_input)]
                df1["DATAB"]=df1["DATAB"].astype("string")
                datab=df1.iat[0, 6]
                #parameter
                GI_count = df1.MENGE.sum()
                day_operate = df1.operate_day.sum()
                demand_peryear= df1.demand_peryear.sum()
                netpr= df1.NETPR.sum()
                netpr= netpr.astype(int)
                SL= service_levell/100
                
                harga_inputt = st.number_input("Harga Sparepart (IDR)",value=netpr, min_value=0)

                if datab == "na":  
                    leadtime = df1.LEADTIME.sum()/30       
                    a =leadtime.astype(int)
                    lt_sparepart = st.number_input("Leadtime (month) ", value = a, min_value=0)
                    lamda = st.number_input("Failure Rate (λ)",  format="%.5f")

                    # MDOEL/FORMULA --> materi https://docs.google.com/presentation/d/1NRoo3JaLD6NnSfvdpuX3OEjBxbMEdbo-7RXBzXfyT5o/edit?usp=sharing
                    # Opsi 1
                    lamda_t = (sparepart_input*equipment_input*lt_sparepart*lamda)

                else :
                    leadtime = df1.LEADTIME.sum()
                    a= leadtime.astype(int)
                    lt_sparepart2 = st.number_input("Leadtime (day) ",value = a,min_value=0)

                    # MDOEL/FORMULA
                    # Opsi 2
                    mtbf= (((day_operate-GI_count)/(GI_count))*24) 
                    lamda =  1/mtbf          
                    failure_rate2 = st.number_input("Failure Rate (λ)",value = lamda,  format="%.5f")
                    lamda_t = (sparepart_input*equipment_input*lt_sparepart2*failure_rate2)

                hitung = st.button("Hitung")

        #============================ Process Poisson & Stok Optimum (Dilihat Dari Service Level) ==========================
        if hitung:
            with col2:
                if lamda==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                else :
                    # ===== PROCESS POISSON ====== 
                    k  = np.arange(0, 30) #30 merupakan banyaknya x yang dicoba
                    cdf = poisson.cdf(k, lamda_t)
                    y =[service_levell/100] * 30

                    def find_nearest(array, value):
                        array = np.asarray(array)
                        idx = (np.abs(array - value)).argmin()
                        return array[idx]

                    #======= pembulatan jumlah sparepart optimum =========
                    data_op = np.column_stack((k, cdf))
                    data_op = pd.DataFrame(data_op)
                    data_op.rename(columns = {0:'x'}, inplace = True)
                    data_op.rename(columns = {1:'cdf'}, inplace = True)
                    data_op = data_op[(data_op.cdf <1) &(data_op.cdf >SL)]
                    nearest = find_nearest(data_op["cdf"], value=0.10)
                    nearest.round(decimals = 6)
                    data_op = data_op[(data_op.cdf == nearest)]
                    nilai_op = data_op.x.sum()
                    round(nilai_op)
                    cdf_op=data_op.cdf.sum()
                    
                    #====== Biaya ========
                    biaya=harga_inputt*nilai_op

                    #equipment valid from

                    #====== Output =======
                    # Informasi
                    new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Informasi</b>'
                    st.markdown(new_title, unsafe_allow_html=True)

                    if datab == "na": 
                        st.markdown(f"- Leadtime (PR-GR) **{round(lt_sparepart)}** Bulan")
                    else: 
                        datab=df1.DATAB
                        st.markdown(f"- Leadtime (PR-GR) **{round(lt_sparepart2)}** Hari")
                        st.markdown(f"- Eqipment Valid From Date **{df1.iat[0, 6]}**")
                        st.markdown(f"- mtbf adalah **{mtbf}**")
                    st.markdown(f"- Demand sebanyak **{round(GI_count)}** sparepart")
                    st.markdown(f"- lamda t **{lamda_t}**")
                    

                    #Hasil
                    new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Hasil</b>'
                    st.markdown(new_title, unsafe_allow_html=True)

                    if equnr_input == "NONE":  
                        st.success(f"Jika service level sebesar {service_levell} % disarankan stok sebanyak **{round(nilai_op) }** sparepart, dengan total biaya Rp. {round(biaya)}")
                        
                    else:
                        st.success(f"Jika service level sebesar {service_levell} % disarankan stok sebanyak **{round(nilai_op) }** sparepart, dengan total biaya Rp. {round(biaya)}*") 
                        
                                        #=======  GRAFIK  ==========
                    data_op1 = np.column_stack((k, cdf,y))
                    data_op1 = pd.DataFrame(data_op1)
                    data_op1.rename(columns = {0:'Sparepart'}, inplace = True)
                    data_op1.rename(columns = {1:'Cumulative distribution function'}, inplace = True)
                    data_op1.rename(columns = {2:'SL'}, inplace = True)

                    fig=px.line(data_op1, x="Sparepart", y="Cumulative distribution function",width=660, height=450, text="Sparepart")
                    fig.update_traces(textposition="top center",name='Qty Sparepart',showlegend=True)
                    fig.update_layout(font_size=13)
                    fig.add_trace(
                        go.Scatter(
                            x=data_op1['Sparepart'],
                            y=data_op1['SL'],
                            mode="lines",line_dash="dot",line_color="red",name='Service Level',
                            line=go.scatter.Line(color="gray"),
                            showlegend=True)
                    )
                    st.plotly_chart(fig)

        # ============================= Submenu Simulation - Material =================================
        with Simulation2:
            col1, padding, col2 = st.columns((6,1.5,15))
            with col1:
                lamda= st.number_input("Demand Rate",format="%0.5f")
                leadtime= st.number_input("Leadtime (Bulan)",format="%0.5f")
                service_level = st.number_input("Service Level (%)",max_value=100, min_value=0,value =98)
                sparepart_input = st.number_input("Jumlah Komponen Terpasang",max_value=100,value =1,min_value=0)
                equipment_input = st.number_input("Jumlah Equipment",max_value=30, min_value=0,value =1)
                harga_sparepart = st.number_input("Harga Sparepart (IDR)",value =100,min_value=0)

                SL=service_level/100

                hitungg = st.button("Hitung ")     
        
        #============================ Process Poisson & Stok Optimum (Dilihat Dari Service Level) ==========================      
        if hitungg:
            with col2:
                if lamda==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                elif leadtime ==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                elif lamda ==0 and leadtime ==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                else :
                    #======== MODEL / Formula ========
                    # opsi 3
                    lamda_t=(sparepart_input*equipment_input*leadtime*lamda/12)

                    #======== PROCESS POISSON =========
                    k  = np.arange(0, 20) #21 merupakan banyaknya x yang dicoba
                    cdf = poisson.cdf(k, lamda_t)
                    y=[service_level/100] * 20

                    def find_nearest(array, value):
                        array = np.asarray(array)
                        idx = (np.abs(array - value)).argmin()
                        return array[idx]

                    #======== pembulatan jumlah sparepart =======
                    data_op = np.column_stack((k, cdf))
                    data_op = pd.DataFrame(data_op)
                    data_op.rename(columns = {0:'x'}, inplace = True)
                    data_op.rename(columns = {1:'cdf'}, inplace = True)
                    data_op = data_op[(data_op.cdf <1) &(data_op.cdf >SL)]
                    nearest = find_nearest(data_op["cdf"], value=0.10)
                    nearest.round(decimals = 6)
                    data_op = data_op[(data_op.cdf == nearest)]
                    nilai_op = data_op.x.sum()
                    round(nilai_op)
                    
                    cdf_op=data_op.cdf.sum()
                    biaya=harga_sparepart*nilai_op

                    #====== Output =======
                    # Informasi
                    new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Informasi</b>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    st.markdown(f"- Leadtime **{leadtime}** Bulan")
                    st.markdown(f"- Failure Rate **{lamda}**")

                    # Hasil
                    new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Hasil</b>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    st.success(f"Jika service level sebesar {service_level} % disarankan stok sebanyak **{round(nilai_op) }** sparepart, dengan total biaya Rp. {round(biaya)}")

                    #=============  GRAFIK  =============
                    #Plot
                    data_op1 = np.column_stack((k, cdf,y))
                    data_op1 = pd.DataFrame(data_op1)
                    data_op1.rename(columns = {0:'Sparepart'}, inplace = True)
                    data_op1.rename(columns = {1:'Cumulative distribution function'}, inplace = True)
                    data_op1.rename(columns = {2:'SL'}, inplace = True)

                    fig=px.line(data_op1, x="Sparepart", y="Cumulative distribution function",width=660, height=450, text="Sparepart")
                    fig.update_traces(textposition="top center",name='Qty Sparepart',showlegend=True)
                    fig.update_layout(font_size=13)
                    fig.add_trace(
                        go.Scatter(
                            x=data_op1['Sparepart'],
                            y=data_op1['SL'],
                            mode="lines",line_dash="dot",line_color="red",name='Service Level',
                            line=go.scatter.Line(color="gray"),
                            showlegend=True)
                    )
                    st.plotly_chart(fig)
                    st.table(data_op1)
