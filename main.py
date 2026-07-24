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

@app.post("/Topfly Herox odometer & speed analysis")
async def upload_excel_herox_odometer_speed(file: UploadFile):
    df=pd.read_excel(file.file, engine='openpyxl')
    unit_13=df[df['Status'].str.contains('0x252513')]
    unit_14=df[df['Status'].str.contains('0x252514')]
    unit_aux=pd.concat([unit_13,unit_14])
    odometer=[]
    #x_axis_odometer=[]
    speed=[]
    #x_axis_speed=[]
    date_odometer=[]
    date_speed=[]
    raw_odometer=[]
    raw_speed=[]
    x_axis_odometer=[]
    y_axis_odometer=[]
    x_axis_speed=[]
    y_axis_speed=[] 
    unit_odometer=pd.DataFrame()
    unit_speed=pd.DataFrame()

    for i in range(0,unit_aux.shape[0]):
        odometer.append(int(unit_aux.iloc[i,2][96:104],16))
        date_odometer.append(unit_aux.iloc[i,2][106:118])
        raw_odometer.append(unit_aux.iloc[i,2])   

    unit_odometer['Odometer in meters']=odometer
    unit_odometer['Date']=date_odometer
    unit_odometer['Raw data']=raw_odometer

    for i in range(0,unit_aux.shape[0]):
        try:
            speed.append(int(unit_aux.iloc[i,2][142:145]))  
            date_speed.append(unit_aux.iloc[i,2][106:118])
            raw_speed.append(unit_aux.iloc[i,2])        
        except:
            pass

    unit_speed['Speed']=speed
    unit_speed['Date']=date_speed
    unit_speed['Raw data']=raw_speed

    unit_odometer_ordered=unit_odometer.sort_values('Date',ascending=True)
    unit_speed_ordered=unit_speed.sort_values('Date',ascending=True)       

    for i in range(0,unit_odometer_ordered.shape[0]):
        x_axis_odometer.append(i)
        y_axis_odometer.append(unit_odometer_ordered.iloc[i,0])

    for i in range(0,unit_speed_ordered.shape[0]):
        x_axis_speed.append(i)
        y_axis_speed.append(unit_speed_ordered.iloc[i,0])

    fig, ax = plt.subplots(1,2, figsize=(12, 6))

    ax[0].set_xlabel('Sample number')
    ax[0].set_ylabel('Odometer in meters')
    ax[1].set_xlabel('Sample number')
    ax[1].set_ylabel('Speed in Km/h')
    ax[0].plot(x_axis_odometer,y_axis_odometer)
    ax[1].plot(x_axis_speed,y_axis_speed)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")

@app.post("/Torch odometer & speed analysis")
async def upload_excel_torch_odometer_speed(file:UploadFile):
    raw_data=pd.read_excel(file.file, engine='openpyxl')
    raw_data_codes=[]

    for i in range(0,raw_data.shape[0]):
        raw_data_codes.append(raw_data.iloc[i,2][6:8])

    raw_data['Codes']=raw_data_codes

    torch_codes_02=raw_data[raw_data['Codes'].str.contains('02')]
    torch_codes_04=raw_data[raw_data['Codes'].str.contains('04')]
    torch_codes_0204=pd.concat([torch_codes_02,torch_codes_04])    

    ignition_on_interval=[]
    ignition_off_interval=[]
    io=[]
    odometer=[]
    date=[]
    ext_ps=[]
    speed=[]
    #over_speed=[]
    gnss=[]
    #a_code=[]
    #direction=[]
    accum_fuel_consumption=[]
    #instant_fuel_consumption=[]
    rpm=[]
    cool_temp=[]
    #air_in_flow_temp=[]
    engine_load=[]
    remain_fuel_rate=[]

    for i in range(0,torch_codes_0204.shape[0]):
        ignition_on_interval.append(int(torch_codes_0204.iloc[i,2][32:36],16))
        ignition_off_interval.append(int(torch_codes_0204.iloc[i,2][36:40],16))
        io.append(bin(int(torch_codes_0204.iloc[i,2][64:68],16)))
        odometer.append(int(torch_codes_0204.iloc[i,2][72:80],16))
        date.append(torch_codes_0204.iloc[i,2][82:94])
        ext_ps.append((float(int(torch_codes_0204.iloc[i,2][126:130])))/100)
        speed.append(int(torch_codes_0204.iloc[i,2][131:133]))    
        #over_speed.append(torch_codes_0204.iloc[i,2])
        gnss.append(int(torch_codes_0204.iloc[i,2][51:52],16))
        #a_code.append(torch_codes_0204.iloc[])
        #direction.append(torch_codes_0204.iloc[i,2])
        accum_fuel_consumption.append(float(int(torch_codes_0204.iloc[i,2][134:142],16))/1000)
        #instant_fuel_consumption.append(torch_codes_0204.iloc[i,2]) invalid!
        rpm.append(int(torch_codes_0204.iloc[i,2][150:154],16))
        cool_temp.append(int(torch_codes_0204.iloc[i,2][158:160],16))
        #air_in_flow_temp.append(torch_codes_0204.iloc[i,2])
        engine_load.append(int(torch_codes_0204.iloc[i,2][162:164],16))
        remain_fuel_rate.append(torch_codes_0204.iloc[i,2][166:168])

    torch_codes_0204['i_on']=ignition_on_interval
    torch_codes_0204['i_off']=ignition_off_interval
    torch_codes_0204['io']=io
    torch_codes_0204['odometer']=odometer
    torch_codes_0204['date']=date
    torch_codes_0204['ext_ps']=ext_ps
    torch_codes_0204['speed']=speed
    torch_codes_0204['gnss']=gnss
    torch_codes_0204['acc_fuel_c']=accum_fuel_consumption
    torch_codes_0204['rpm']=rpm
    torch_codes_0204['cool_temp']=cool_temp
    torch_codes_0204['remain_fuel']=remain_fuel_rate
    torch_codes_0204['engine_load']=engine_load

    torch_codes_0204_ordered=torch_codes_0204.sort_values('date',ascending=True)

    df=torch_codes_0204_ordered[['i_on','i_off','io','odometer','date','ext_ps','speed','acc_fuel_c','rpm','remain_fuel','gnss','cool_temp','Status','engine_load']]

    odometer_data=[]
    rpm_data=[]
    speed_data=[]
    fuel_data=[]
    x_axis_odo_speed=[]
    x_axis_rpm=[]
    date=[]
    status=[]
    ind_odometer=0
    ind_speed=0

    for i in range(0,df.shape[0]):
        ind_odometer=int(df.iloc[i,3])
        if ind_odometer>80000000:
            status.append(df.iloc[i,12])
            odometer_data.append(int(df.iloc[i,3]))
            #rpm_data.append(int(df.iloc[i,8]))
            speed_data.append(int(df.iloc[i,6]))
            #fuel_data.append((int(df.iloc[i,9],16) & 127))
            date.append(df.iloc[i,4])
            x_axis_odo_speed.append(i)

    for i in range(0,df.shape[0]):
        ind_speed=int(df.iloc[i,8])        
        if ind_speed<65535:
            status.append(df.iloc[i,12])
            rpm_data.append(df.iloc[i,8])
            date.append(df.iloc[i,4])
            x_axis_rpm.append(i) 

    fig, ax = plt.subplots(1,2, figsize=(12, 6))

    ax[0].set_xlabel('Sample number')
    ax[0].set_ylabel('Odometer in meters')
    ax[1].set_xlabel('Sample number')
    ax[1].set_ylabel('Speed in Km/h')
    #ax[2].set_xlabel('Sample number')
    #ax[2].set_ylabel('rpm')
    ax[0].plot(x_axis_odo_speed,odometer_data)
    ax[1].plot(x_axis_odo_speed,speed_data)
    #ax[2].plot(x_axis_rpm,rpm_data)
    """
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0) # Reset buffer pointer to the beginning
    plt.close() # Free up server memory
    return StreamingResponse(buf, media_type="image/png")      
    """

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