import streamlit as st
import pickle
from pathlib import Path

import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Stock Calculation Dashboard", page_icon=":bar_chart:", layout="wide")

# --- USER AUTHENTICATION ---
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

    #st.set_page_config(layout="centered", initial_sidebar_state="auto")
    st.markdown("<h3 style='text-align: center;'>STOCK CALCULATION SPAREPART </h3>", unsafe_allow_html=True)

    #------------------------ packages ------------------
    from pandasql import sqldf
    import pyodbc
    import statistics
    import pandas as pd
    import numpy as np
    # Ignore harmless warnings
    import warnings
    warnings.filterwarnings("ignore")
    from scipy.stats import shapiro, norm, poisson
    #from math import sqrt, ceil, floor
    import datetime
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.express as px
    import plotly.graph_objects as go
    import time

    #sidebar
    import os
    import sys
    from PIL import Image
    from streamlit_option_menu import option_menu


    #Loading
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.005)
        my_bar.progress(percent_complete + 1)

    col1, col2 = st.columns([2,2])


    #----------------------------- loading dataset --------------------------
    dataset = pd.read_csv("dataset_update_material.csv")

    #----------------------------- sidebar ----------------------------------
    authenticator.logout("Logout", "sidebar")
    with st.sidebar:
        directory_path = os.path.dirname(__file__)
        image = Image.open(os.path.join(directory_path, 'test2.png'))
        pad1, pad2, pad3 = st.columns([2,8,1])

        with pad2:
            st.image(image, output_format='png', width=170)
        #st.image("https://www.pupuk-indonesia.com/assets/img/logo.png", use_column_width="always")
        
        selected = option_menu("", ['Home',"Dataset","Calculator"], 
            icons=['graph', 'graph', 'graph'], menu_icon="cast", default_index=0)

    if selected == "Home":
        directory_path = os.path.dirname(__file__)
        st.subheader("Halo,")
        hc1, hc2 = st.columns([4,4])

        with hc1:
            st.markdown("Stok Calculation tool merupakan alat analisis untuk mendapatkan perhitungan stok sparepart optimum terkhusus pada sparepart tipe statis. Alat ini digunakan diharapkan dapat meminimasi downtime mesin akibat dari ketidakfungsian sparepart yang kerusakannya tidak terduga.")
            st.markdown("Penentuan banyaknya stok sparepart berdasarkan service level, failure rate sparepart, dan leadtime pengadaan.")
            st.markdown("**Note**: Calculator Uses in Slow and Non Moving SpareParts SAP Data")
            st.write("Download User Guides [Click](https://drive.google.com/file/d/1kjZIwnPvYDv5zQHMvhIrQKD_I5nJPJI9/view?usp=sharing)")

        with hc2:
            st.markdown("![Alt Text](https://media2.giphy.com/media/l46Cy1rHbQ92uuLXa/giphy.gif)")

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

    elif selected == "Calculator":
        Simulation1, tabSimulasi = st.tabs(["Simulation - Equipment", "Simulation - Material"])
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
                GI_count = df1.MENGE.sum()
                day_operate = df1.operate_day.sum()
                demand_peryear=df1.demand_peryear.sum()
                SL=service_levell/100
                netpr=df1.NETPR.sum()
                netpr=netpr.astype(int)
                
                harga_inputt = st.number_input("Harga Sparepart (IDR)",value=netpr, min_value=0)
                
                df1["DATAB"]=df1["DATAB"].astype("string")
                datab=df1.iat[0, 6]

                if datab == "na":  
                    leadtime = df1.LEADTIME.sum()/30       
                    a =leadtime.astype(int)
                    lt_sparepart = st.number_input("Leadtime (month) ",value = a,min_value=0)
                    lamda = st.number_input("Failure Rate (λ)",  format="%.5f")
                    lamda_t = (sparepart_input*equipment_input*lt_sparepart*lamda)
                    #st.markdown(f"- SL **{SL}**,datab **{datab}** ")
                else :
                    leadtime = df1.LEADTIME.sum()
                    a=leadtime.astype(int)
                    lt_sparepart2 = st.number_input("Leadtime (day) ",value = a,min_value=0)

                    mtbf= (((day_operate-GI_count)/(GI_count))*24) 
                    lamda =  1/mtbf          
                    failure_rate2 = st.number_input("Failure Rate (λ)",value = lamda,  format="%.5f")
                    lamda_t = (sparepart_input*equipment_input*lt_sparepart2*failure_rate2)
                
                    #st.markdown(f"- SL **{SL}**,datab **{df1.iat[0, 6]}** ")
                    #st.table(df1)
                hitung = st.button("Hitung")

            #================================== === Output ==================================================
        if hitung:
            with col2:
                if lamda==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                else :
                        SS =((demand_peryear)/350)*leadtime
                        ROP= ((demand_peryear)/350)*leadtime*2

                        #PROCESS POISSON NO LEADTIME
                        k  = np.arange(0, 30) #21 merupakan banyaknya x yang dicoba
                        cdf = poisson.cdf(k, lamda_t)
                        y=[service_levell/100] * 30

                        def find_nearest(array, value):
                            array = np.asarray(array)
                            idx = (np.abs(array - value)).argmin()
                            return array[idx]

                        #========== pembulatan jumlah sparepart optimum ============
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
                        
                        #Biaya
                        biaya=harga_inputt*nilai_op

                        #equipment valid from

                        #Output
                        new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Informasi</b>'
                        st.markdown(new_title, unsafe_allow_html=True)

                        if datab == "na": 
                            st.markdown(f"- Leadtime (PR-GR) **{round(lt_sparepart)}** Bulan")
                        else: 
                            datab=df1.DATAB
                            st.markdown(f"- Leadtime (PR-GR) **{round(lt_sparepart2)}** Hari")
                            st.markdown(f"- Eqipment Valid From Date **{df1.iat[0, 6]}**")
                        st.markdown(f"- Demand sebanyak **{round(GI_count)}** sparepart")

                        new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Hasil</b>'
                        st.markdown(new_title, unsafe_allow_html=True)

                        if equnr_input == "NONE":  
                            st.success(f"Jumlah stok sparepart optimum sebanyak **{round(nilai_op)} sparepart**, dengan total biaya **Rp. {round(biaya)}**")
                        else:
                            st.success(f"Jumlah stok sparepart optimum sebanyak **{round(nilai_op)} sparepart**, dengan total biaya **Rp. {round(biaya)}**")
                            #st.success(f"Safety Stock adalah **{round(SS)}** sparepart pembulatan dari {round(SS,2)}")
                            #st.success(f"Reorder Point adalah **{round(ROP)}** sparepart pembulatan dari {round(ROP,2)}")   

                        #==================  GRAFIK  ======================
                        #Plot
                        data_op1 = np.column_stack((k, cdf,y))
                        data_op1 = pd.DataFrame(data_op1)
                        data_op1.rename(columns = {0:'Sparepart'}, inplace = True)
                        data_op1.rename(columns = {1:'Cumulative distribution function'}, inplace = True)
                        data_op1.rename(columns = {2:'SL'}, inplace = True)

                        #st.plotly_chart(px.line(data_op1, x="x", y="cdf",width=650, height=450, text="x"))
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

    #====================================================================================
        with tabSimulasi:
            col1, padding, col2 = st.columns((6,1.5,15))
            with col1:
                lamda= st.number_input("Demand Rate",format="%0.5f")
                leadtime= st.number_input("Leadtime (Bulan)", min_value=0,value =0)
                service_level = st.number_input("Service Level (%)",max_value=100, min_value=0,value =98)
                sparepart_input = st.number_input("Jumlah Komponen Terpasang",max_value=100,value =1,min_value=0)
                equipment_input = st.number_input("Jumlah Equipment",max_value=30, min_value=0,value =1)
                harga_sparepart = st.number_input("Harga Sparepart (IDR)",value =100,min_value=0)

                SL=service_level/100

                hitungg = st.button("Hitung ")           
        
        if hitungg:
            # Perhitungan
            with col2:
                if lamda==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                elif leadtime ==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                elif lamda==0 & leadtime ==0:
                    st.info('Silahkan lengkapi kolom, tidak boleh bernilai nol', icon="ℹ️")
                else :
                    #menghitung lamda t
                    lamda_t=(sparepart_input*equipment_input*leadtime*lamda/12)

                    #PROCESS POISSON NO LEADTIME
                    k  = np.arange(0, 20) #21 merupakan banyaknya x yang dicoba
                    cdf = poisson.cdf(k, lamda_t)
                    y=[service_level/100] * 20

                    def find_nearest(array, value):
                        array = np.asarray(array)
                        idx = (np.abs(array - value)).argmin()
                        return array[idx]

                    # pembulatan jumlah sparepart
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

                    new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Informasi</b>'
                    st.markdown(new_title, unsafe_allow_html=True)

                    st.markdown(f"- Leadtime **{leadtime}** Bulan")
                    st.markdown(f"- Failure Rate **{lamda}**")

                    new_title = '<b style="font-family:sans-serif; color:Black; font-size: 16px;">Hasil</b>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    st.success(f"Jika service level sebesar {service_level} % disarankan stok sebanyak **{round(nilai_op) }** sparepart, dengan total biaya Rp. {round(biaya)}")

                    #==================  GRAFIK  ======================
                    #Plot
                    data_op1 = np.column_stack((k, cdf,y))
                    data_op1 = pd.DataFrame(data_op1)
                    data_op1.rename(columns = {0:'Sparepart'}, inplace = True)
                    data_op1.rename(columns = {1:'Cumulative distribution function'}, inplace = True)
                    data_op1.rename(columns = {2:'SL'}, inplace = True)

                    #st.plotly_chart(px.line(data_op1, x="x", y="cdf",width=650, height=450, text="x"))
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
