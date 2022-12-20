import streamlit as st

st.set_page_config(layout='wide')
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

#sidebar
import os
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
with st.sidebar:
    directory_path = os.path.dirname(__file__)
    image = Image.open(os.path.join(directory_path, '42832.png'))
    pad1, pad2, pad3 = st.columns([1,6,4])

    with pad2:
        st.image(image, output_format='png', width=170)
    #st.image("https://www.pupuk-indonesia.com/assets/img/logo.png", use_column_width="always")
    
    selected = option_menu("", ['Home',"Calculator"], 
        icons=['graph', 'graph'], menu_icon="cast", default_index=0)

if selected == "Home":
    directory_path = os.path.dirname(__file__)
    st.subheader("Halo,")
    hc1, hc2 = st.columns([4,4])

    with hc1:
        st.markdown("Stok Calculation tools merupakan alat analisis untuk mendapatkan perhitungan stok sparepart optimum terkhusus pada sparepart tipe statis. Alat ini digunakan untuk dapat meminimasi downtime akibat dari ketidakfungsian sparepart yang kerusakannya tidak terduga.")
        st.markdown("Penentuan nilai stok optimum berdasarkan perhitungan proses poisson dan service level perusahaan.")
        st.markdown("**Note**: Products included in the Sparepart Slow and Non Moving")
        st.write("Download User Guide [Click](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")

        clist1 = dataset['Anper'].unique()
        werks_input0 = st.selectbox("Select a Anak Perusahaan:",options= clist1)
        dataset = dataset[(dataset["Anper"] == werks_input0)]
        clist2 = dataset['nama_material'].unique() 
        ematn_input0 = st.selectbox("Select a Material:",options= clist2,index=0)
        dataset = dataset[(dataset["nama_material"] == ematn_input0)]
        st.write(dataset) 

    with hc2:
        st.markdown("![Alt Text](https://media2.giphy.com/media/l46Cy1rHbQ92uuLXa/giphy.gif)")

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
            sparepart_input = st.number_input("Jumlah Komponen Terpasang",value =1,min_value=0)
            equipment_input = st.number_input("Jumlah Equipment",max_value=24, min_value=0,value =1)
            service_levell = st.number_input("Service Level (%)",max_value=100, min_value=0,value =95)

            ########### filter data untuk perhitungan #############            
            df1 = dataset[(dataset.Anper == werks_input) &(dataset.EQUNR == equnr_input) & (dataset.nama_material == ematn_input)]
            GI_count = df1.MENGE.sum()
            day_operate = df1.operate_day.sum()
            demand_peryear=df1.demand_peryear.sum()
            SL=service_levell/100
            netpr=df1.NETPR.sum()
            netpr=netpr.astype(int)
            
            harga_inputt = st.number_input("Harga Sparepart (IDR)",value=netpr, min_value=0)

            if equnr_input == "NONE":  
                leadtime = df1.LEADTIME.sum()/30       
                a =leadtime.astype(int)
                lt_sparepart = st.number_input("Leadtime (month) ",value = a,min_value=0)
                failure_rate1 = st.number_input("Failure Rate",  format="%.5f")
                failure_rate = (sparepart_input*equipment_input*lt_sparepart*failure_rate1)
                #st.markdown(f"- SL **{SL}**,**{cdf}**,**{y}**,failure_rate **{failure_rate}** ")
            else :
                leadtime = df1.LEADTIME.sum()
                a=leadtime.astype(int)
                lt_sparepart2 = st.number_input("Leadtime (day) ",value = a,min_value=0)

                mtbf= (((day_operate-GI_count)/(GI_count))*24)             
                lamda_t = (sparepart_input*equipment_input*lt_sparepart2)/mtbf

                failure_rate2 = st.number_input("Failure Rate",value = lamda_t,  format="%.5f")
                failure_rate = failure_rate2*sparepart_input*equipment_input                
                #st.markdown(f"- SL **{SL}**,**{cdf}**,**{y}**, {mtbf}")
            hitung = st.button("Hitung")

        #================================== === Output ==================================================
        with col2:
                if hitung:
                    SS =((demand_peryear)/350)*leadtime
                    ROP= ((demand_peryear)/350)*leadtime*2

                    #PROCESS POISSON NO LEADTIME
                    k  = np.arange(0, 20) #21 merupakan banyaknya x yang dicoba
                    cdf = poisson.cdf(k, failure_rate)
                    y=[service_levell/100] * 20

                    def find_nearest(array, value):
                        array = np.asarray(array)
                        idx = (np.abs(array - value)).argmin()
                        return array[idx]

                    #========== pembulatan jumlah sparepart optimum ============
                    data_op = np.column_stack((k, cdf))
                    data_op = pd.DataFrame(data_op)
                    data_op.rename(columns = {0:'x'}, inplace = True)
                    data_op.rename(columns = {1:'cdf'}, inplace = True)
                    data_op = data_op[(data_op.cdf <0.999) &(data_op.cdf >SL)]
                    nearest = find_nearest(data_op["cdf"], value=0.10)
                    nearest.round(decimals = 6)
                    data_op = data_op[(data_op.cdf == nearest)]
                    nilai_op = data_op.x.sum()
                    round(nilai_op)
                    cdf_op=data_op.cdf.sum()
                    
                    #Biaya
                    biaya=harga_inputt*nilai_op
                
                    #Output
                    new_title = '<p style="font-family:sans-serif; color:Black; font-size: 16px;">Informasi</p>'
                    st.markdown(new_title, unsafe_allow_html=True)

                    if equnr_input == "NONE": 
                        st.markdown(f"- Leadtime (PR-GR) **{round(lt_sparepart)}** Bulan")
                    else: 
                        st.markdown(f"- Leadtime (PR-GR) **{round(lt_sparepart2)}** Hari")
                    st.markdown(f"- Demand sebanyak **{round(GI_count)}** sparepart")

                    new_title = '<p style="font-family:sans-serif; color:Black; font-size: 16px;">Hasil</p>'
                    st.markdown(new_title, unsafe_allow_html=True)

                    if equnr_input == "NONE":  
                        st.info('This is a purely informational message', icon="ℹ️")
                        st.error('This is an error', icon="🚨")
                        st.warning('This is a warning', icon="⚠️")
                        e = RuntimeError('This is an exception of type RuntimeError')
                        st.exception(e)
                        st.success(f"Jumlah sparepart optimum yang dibutuhkan dalam satu periode sebanyak **{round(nilai_op)} sparepart**, dengan total biaya **Rp. {round(biaya)}**")
                    else:
                        st.success(f"jumlah sparepart optimum yang dibutuhkan dalam satu periode sebanyak **{round(nilai_op)} sparepart**, dengan total biaya **Rp. {round(biaya)}**")
                        st.success(f"Safety Stock adalah **{round(SS)}** sparepart pembulatan dari {round(SS,2)}")
                        st.success(f"Reorder Point adalah **{round(ROP)}** sparepart pembulatan dari {round(ROP,2)}")   

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
            lamda= st.number_input("Failure Rate ",format="%0.5f")
            leadtime= st.number_input("Leadtime (Bulan)", min_value=0,value =0)
            service_level = st.number_input("Service Level (%)",max_value=100, min_value=0,value =96)
            sparepart_input = st.number_input("Jumlah Komponen Terpasang",max_value=100,value =1,min_value=0)
            harga_sparepart = st.number_input("Harga Sparepart (IDR)",value =1,min_value=0)
            equipment_input = st.number_input("Jumlah Equipment",max_value=30, min_value=0,value =1)
            hitungg = st.button("Hitung ✅")
            SL=service_level/100

        # Perhitungan
        with col2:
            if hitungg:

                #menghitung lamda t
                lamda_t=(sparepart_input*equipment_input*leadtime*lamda)

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
                data_op = data_op[(data_op.cdf <0.999) &(data_op.cdf >SL)]
                nearest = find_nearest(data_op["cdf"], value=0.10)
                nearest.round(decimals = 6)
                data_op = data_op[(data_op.cdf == nearest)]
                nilai_op = data_op.x.sum()
                round(nilai_op)
                
                cdf_op=data_op.cdf.sum()
                biaya=harga_sparepart*nilai_op

                new_title = '<p style="font-family:sans-serif; color:Black; font-size: 16px;">Informasi</p>'
                st.markdown(new_title, unsafe_allow_html=True)

                st.markdown(f"- Leadtime **{leadtime}** Bulan")
                st.markdown(f"- Failure Rate **{lamda}**")

                new_title = '<p style="font-family:sans-serif; color:Black; font-size: 16px;">Hasil</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                st.success(f"jumlah sparepart optimum yang dibutuhkan dalam satu periode sebanyak **{round(nilai_op) }** sparepart, dengan total biaya RP. {round(biaya)}")

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
