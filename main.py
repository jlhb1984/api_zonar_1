import datetime
import io
import matplotlib
matplotlib.use('Agg') # Tells Matplotlib to run without a GUI monitor
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

app = FastAPI()

no_seatbelt=pd.DataFrame()

@app.get("/Decode Fuel message")
def get_fuel_message(value:str):
    #decoder={'Prefix':x[0:2],'Sender network address':x[2:4],'Command code':x[4:6],'Temperature':x[6:8],'User value of fuel level':x[8:12],'Technological value of fuel level':x[12:16],'CRC':x[16:18]}
    msb=value[10:12]
    lsb=value[8:10]
    measure=msb+lsb
    dec_measure=int(measure,16)
    a=value[8:12]
    return {"N code: ":dec_measure,"Prefix":value[0:2],"Sender network address":value[2:4],"Command code":value[4:6],"Temperature":value[6:8],"User value of fuel level":value[8:12],"Technological value of fuel level":value[12:16],"CRC":value[16:18]}

@app.post("/Linear regression")
async def upload_Excel_epsilon(file: UploadFile):
    df= pd.read_excel(file.file, engine='openpyxl')
    from sklearn.linear_model import LinearRegression
    X = df[["Measured"]]
    y = df["User"]*3.78541    
    model = LinearRegression()
    model.fit(X, y)

    intercept = model.intercept_
    slope = model.coef_[0]
    headers = {
    "X-Status": "regression created",
    "X-Intercept": str(intercept),
    "X-Coefficient": str(slope)
    }

    stats_text = f"Slope (m): {slope:.4f}\nIntercept (b): {intercept:.4f}"    

    fig, ax = plt.subplots(1,2, figsize=(12, 6))
    ax[0].plot(X, y, 'o', label='Data points')    
    ax[0].plot(X, model.predict(X), '-', label='Regression line')    
    ax[0].set_xlabel('N code')
    ax[0].set_title(stats_text)
    ax[0].set_ylabel('Liters')    
    ax[0].legend()
    ax[1].plot(X, df['User'])
    ax[1].plot(X, df['User'], 'o', label='Data points')
    ax[1].set_xlabel('N code')
    ax[1].set_ylabel('Gallons')
    ax[1].set_title('Technician information')
    ax[1].legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")
    #return {"status": "regression created", "intercept": model.intercept_, "coefficient": model.coef_[0]}

@app.post("/Fuel calamp analysis")
async def upload_excel_calamp(file: UploadFile):
    df= pd.read_excel(file.file, engine='openpyxl')
    e0x=df[df["Status"].str.contains('3E0')]
    row_number=e0x.shape[0]

    fs01_dec_value=[]
    fs02_dec_value=[]
    last_index_fs01=[]
    last_index_fs02=[]
    date_fs01_dec_value=[]
    date_fs02_dec_value=[]
    values_dates_fs01=pd.DataFrame()
    values_dates_fs02=pd.DataFrame()

    for i in range(0,row_number):
        e0x_aux=e0x.iloc[i,2]
        aux=e0x_aux.find('3E01')    
        if len(e0x_aux)>0:
            fs01=(e0x_aux[aux:aux+18])
            if len(fs01)>17:
                msb=fs01[10:12]
                lsb=fs01[8:10]
                measure=msb+lsb
                fs01_dec_value.append(int(measure,16))
                date_fs01_dec_value.append(e0x.iloc[i,0])            
                msb=fs01[28:30]
                lsb=fs01[26:28]
                fs01_dec_value.append(int(measure,16))
                date_fs01_dec_value.append(e0x.iloc[i,0]) 
                msb=fs01[46:48]
                lsb=fs01[44:46]
                fs01_dec_value.append(int(measure,16))
                date_fs01_dec_value.append(e0x.iloc[i,0])
                msb=fs01[46:48]
                lsb=fs01[44:46]
                fs01_dec_value.append(int(measure,16))
                date_fs01_dec_value.append(e0x.iloc[i,0])
                msb=fs01[64:66]
                lsb=fs01[62:64]
                last_index_fs01=i

    for i in range(0,row_number):
        e0x_aux=e0x.iloc[i,2]
        aux=e0x_aux.find('3E02')
        if len(e0x_aux)>0:
            fs02=e0x_aux[aux:aux+18]
            if len(fs02)>17:
                msb=fs02[10:12]
                lsb=fs02[8:10]
                measure=msb+lsb
                fs02_dec_value.append(int(measure,16))
                date_fs02_dec_value.append(e0x.iloc[i,0])            
                msb=fs02[28:30]
                lsb=fs02[26:28]
                fs02_dec_value.append(int(measure,16))
                date_fs02_dec_value.append(e0x.iloc[i,0]) 
                msb=fs02[46:48]
                lsb=fs02[44:46]
                fs02_dec_value.append(int(measure,16))
                date_fs02_dec_value.append(e0x.iloc[i,0])
                msb=fs02[46:48]
                lsb=fs02[44:46]
                fs02_dec_value.append(int(measure,16))
                date_fs02_dec_value.append(e0x.iloc[i,0])
                msb=fs02[64:66]
                lsb=fs02[62:64]
                #last_index_fs02=i        
                
    fs01_count=len(fs01_dec_value)
    fs02_count=len(fs02_dec_value)
    values_dates_fs01['Value fs01']=fs01_dec_value
    values_dates_fs01['Dates fs01']=date_fs01_dec_value
    values_dates_fs02['Value fs02']=fs02_dec_value
    values_dates_fs02['Dates fs02']=date_fs02_dec_value

    fs01_x_values=[]
    fs02_x_values=[]

    for i in range(0,fs01_count):
        fs01_x_values.append(i)
        
    for i in range(0,fs02_count):
        fs02_x_values.append(i)

    fig, ax = plt.subplots(1,2, figsize=(12, 6))
    ax[0].set_xlabel('Sample number')
    ax[0].set_ylabel('N code')
    ax[0].set_title('Tank number 1')
    ax[0].plot(fs01_x_values,fs01_dec_value)    
    ax[1].set_xlabel('Sample number')
    ax[1].set_ylabel('N code')
    ax[1].set_title('Tank number 2')
    ax[1].plot(fs02_x_values,fs02_dec_value)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")    

@app.post("/Fuel heroX analysis")
async def upload_excel_herox(file: UploadFile):
    df= pd.read_excel(file.file, engine='openpyxl')
    e0x=df[df['Status'].str.contains('3E0')]
    row_number=e0x.shape[0]
    fs01_dec_value=[]
    fs02_dec_value=[]
    last_index_fs01=[]
    last_index_fs02=[]
    date_fs01_dec_value=[]
    date_fs02_dec_value=[]
    values_dates_fs01=pd.DataFrame()
    values_dates_fs02=pd.DataFrame()

    for i in range(0,row_number):
        e0x_aux=e0x.iloc[i,2]
        aux=e0x_aux.find('3E01')
        if len(e0x_aux)>0:
            fs01=(e0x_aux[aux:aux+18])
            if len(fs01)>17:
                msb=fs01[10:12]
                lsb=fs01[8:10]
                measure=msb+lsb
                fs01_dec_value.append(int(measure,16))
                date_fs01_dec_value.append(e0x.iloc[i,0])
                last_index_fs01=i    

    for i in range(0,row_number):
        e0x_aux=e0x.iloc[i,2]
        aux=e0x_aux.find('3E02')
        if len(e0x_aux)>0:
            fs02=e0x_aux[aux:aux+18]
            if len(fs02)>17:
                msb=fs02[10:12]
                lsb=fs02[8:10]
                measure=msb+lsb
                fs02_dec_value.append(int(measure,16))
                date_fs02_dec_value.append(e0x.iloc[i,0])
                last_index_fs02=i     

    fs01_count=len(fs01_dec_value)
    fs02_count=len(fs02_dec_value)
    #print('El Ncode en decimal es:')
    values_dates_fs01['value']=fs01_dec_value
    values_dates_fs01['date']=date_fs01_dec_value
    values_dates_fs02['value']=fs02_dec_value
    values_dates_fs02['date']=date_fs02_dec_value

    fs01_x_values=[]
    fs02_x_values=[]

    for i in range(0,fs01_count):
        fs01_x_values.append(i)
        
    for i in range(0,fs02_count):
        fs02_x_values.append(i)

    fig, ax = plt.subplots(1,2, figsize=(12, 6))

    ax[0].set_xlabel('Sample number')
    ax[0].set_ylabel('N code')
    ax[0].plot(fs01_x_values,fs01_dec_value)
    ax[0].set_title('Tank number 1')    
    ax[1].set_xlabel('Sample number')
    ax[1].set_ylabel('N code')
    ax[1].plot(fs02_x_values,fs02_dec_value)
    ax[1].set_title('Tank number 2')
    #plt.show()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")      

@app.post("/Waylens analysis")
async def upload_excel_waylens(file: UploadFile):
    df= pd.read_excel(file.file, engine='openpyxl')
    message_number=df['Message'].value_counts()
    vf_camera_events=df[df['Message'].str.contains('CameraEvent')]
    vf_camera_events_number=vf_camera_events['Unnamed: 4'].value_counts()
    vf_camera_events_categories=vf_camera_events['Unnamed: 5'].value_counts()
    vf_no_seatbelt=df[df['Unnamed: 4'].str.contains('NO_SEATBELT')]

    vf_date_time=vf_no_seatbelt[vf_no_seatbelt['Unnamed: 9'].str.contains('time')]
    #vf_date_time['Unnamed: 9']
    aux_date_time=[]
    epoch_date=[]
    vf_date_time['Date']='NaN'
    speed=[]

    for i in range(0,vf_date_time.shape[0]):
        aux_date_time.append(float(vf_date_time.iloc[i,9][5:18])/1000)
        epoch_date.append(datetime.datetime.fromtimestamp(aux_date_time[i]))    
        vf_date_time.iloc[i,103]=str(epoch_date[i])
        speed.append(vf_date_time.iloc[i,19])
    
    no_seatbelt['Date']=epoch_date
    no_seatbelt['Speed']=speed

    return {"Events": vf_camera_events_number.to_dict(), "Categories": vf_camera_events_categories.to_dict(), "message_number": message_number.to_dict()}

@app.post("/PioneerX 100 odometer & speed analysis")
async def upload_excel_pioneer_odometer_speed(file: UploadFile):
    df= pd.read_excel(file.file, engine='openpyxl')
    unit_13=df[df['Status'].str.contains('0x252513')]
    unit_14=df[df['Status'].str.contains('0x252514')]
    unit_aux=pd.concat([unit_13,unit_14])
    unit_aux['Odometer in meters']=0.0
    odometer=[]
    date=[]
    raw=[]
    speed=[]            #added for speed analysis
    unit=pd.DataFrame()

    for i in range(0,unit_aux.shape[0]):
        odometer.append(int(unit_aux.iloc[i,2][96:104],16))
        speed.append(int(unit_aux.iloc[i,2][142:145],16))
        date.append(unit_aux.iloc[i,2][106:118])
        raw.append(unit_aux.iloc[i,2])    

    unit_aux['Odometer in meters']=odometer
    unit_aux['Speed']=speed
    unit_aux['Raw data']=raw
    unit_aux['date']=date

    unit=unit_aux.sort_values('date',ascending=True)

    y_axis_o=[]
    y_axis_s=[]
    x_axis=[]
    date=[]
    raw_data_=[]

    for i in range(0,unit.shape[0]):
        #print(float(fsq694_m_odometer.iloc[i,6][8:15]))
        y_axis_o.append(float(unit.iloc[i,3]))
        y_axis_s.append(float(unit.iloc[i,4]))
        x_axis.append(i)
        date.append(unit.iloc[i,5])
        raw_data_.append(unit.iloc[i,4])   

    fig, ax = plt.subplots(1,2, figsize=(12, 6))
    ax[0].set_xlabel('Sample number')
    ax[0].set_ylabel('Odometer in meters')
    ax[0].plot(x_axis,y_axis_o)
    ax[0].set_title('Odometer vs sample number')
    ax[1].set_xlabel('Sample number')
    ax[1].set_ylabel('Speed in Km/h')
    ax[1].set_title('Speed vs sample number')
    ax[1].plot(x_axis,y_axis_s)
    #plt.show()

    #plt.plot(x_axis,y_axis)                #commented for speed analysis

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")

@app.post("/Calamp odometer & speed analysis")
async def upload_excel_calamp_odometer_speed(file: UploadFile):
    df= pd.read_excel(file.file, engine='openpyxl')
    aux=[]
    aux_miles=[]
    x_axis=[]
    unit_odometer=pd.DataFrame()
    cont=0

    #Speed chart:
    aux_kmh=[]
    unit_speed=pd.DataFrame()

    for i in range (0,df.shape[0]):
        l=len(df.iloc[i,2])
        #print('Len=',l)
        if l<180:
            aux.append(int(df.iloc[i,2][68:76],16))
            aux_miles.append((int(df.iloc[i,2][68:76],16))*0.000621371)
            aux_kmh.append(int(df.iloc[i,2][56:58],16))
            cont=cont+1     

    unit_odometer['Odometer in']=aux
    unit_odometer['Odometer en miles']=aux_miles
    unit_speed['Speed Km-h']=aux_kmh 

    for i in range(0,cont):
        x_axis.append(i)
    
    #plt.plot(x_axis,aux)

    fig, ax = plt.subplots(1,2, figsize=(12, 6))

    ax[0].set_xlabel('Sample number')
    ax[0].set_ylabel('Odometer in meters')
    ax[1].set_xlabel('Sample number')
    ax[1].set_ylabel('Speed in Km/h')
    ax[0].plot(x_axis,aux)
    ax[1].plot(x_axis,aux_kmh)
    ax[0].set_title('Odometer vs sample number')
    ax[1].set_title('Speed vs sample number')
    #plt.show()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")    