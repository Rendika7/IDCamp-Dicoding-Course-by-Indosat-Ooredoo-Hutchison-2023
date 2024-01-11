import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
# Pengaturan awal
sns.set(style='dark')
st.set_option('deprecation.showPyplotGlobalUse', False)
import datetime
st.set_page_config(page_title="Air Quality Dashboard", layout="wide", initial_sidebar_state="auto")

# Membuat data frame sederhana
df = pd.read_csv('Air-quality-dataset.csv')

st.sidebar.markdown(
    "<div align='center'>"
    "<img src='https://cdn.dribbble.com/users/10034599/avatars/normal/44422246eca88299fb1c5a8c054e92ca.jpg?1664083716' width='200'>"
    "</div>",
    unsafe_allow_html=True
)


with st.sidebar:
    # Menambahkan logo perusahaan 
    name = st.text_input(label='Nama lengkap', value='')
    st.write('Nama: ', name)
  
    number = st.number_input(label='Umur')
    st.write('Umur: ', int(number), ' tahun')

    date = st.date_input(label='Tanggal lahir', min_value= datetime.date(1900, 1, 1))
    st.write('Tanggal lahir:', date)
    # Mengambil start_date & end_date dari date_input






# Judul dashboard
st.title('Dashboard Air-Quality')

col1, col2 = st.columns(2)

with col1:   
    # Checking NaN
    st.subheader('Checking NaN Values')
    total = df.isnull().sum().sort_values(ascending=False)
    percent = (df.isnull().sum()/len(df)).sort_values(ascending=False)
    missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
    missing_data['Percent'] = missing_data['Percent']*100

    # Menampilkan data frame
    st.write('Missing Data - DataFrame:', missing_data)


with col2: 
    st.subheader('Hello World - Hope U Like It')


with col1:
# Duplicated Checking
    Duplicated = df.duplicated().sum()

    st.metric(label="Data Duplicated", value= Duplicated, delta="NaN Values")




# Assuming df is your DataFrame
outliers_data = []

for column in df.columns:
    if df[column].dtype in ['int64', 'float64']:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR
        column_outliers = df[(df[column] < lower_fence) | (df[column] > upper_fence)]
        
        outliers_data.append({
            "Nama Kolom": column,
            "Outliers Count": len(column_outliers),
        })

# Create a new DataFrame for the outliers
outliers_df = pd.DataFrame(outliers_data)
outliers_df = outliers_df.sort_values(by = 'Outliers Count', ascending=False)
outliers_df['Outliers Percentage'] = outliers_df['Outliers Count'] * 100 / df.shape[0]
with col2:
    st.write('outliers - DataFrame:', outliers_df)
    
# Cleaning data
# Dropping NaN
ukuran_awal = df.shape
df = df.dropna(axis=0)
ukuran_clean = df.shape
# Drop outliers for each column
for column in outliers_df['Nama Kolom']:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_fence = Q1 - 1.5 * IQR
    upper_fence = Q3 + 1.5 * IQR
    
    df = df[(df[column] >= lower_fence) & (df[column] <= upper_fence)]
with col2:
    st.metric(label="Data yang dibuang", value= ukuran_awal[0] - ukuran_clean[0], delta="Dirty Data")

df = df.reset_index(drop = True).drop(columns = 'No')

# Gabungkan kolom 'year', 'month', dan 'day' menjadi satu kolom datetime
df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

# Hapus kolom 'year', 'month', dan 'day' yang tidak diperlukan lagi
df = df.drop(['year', 'month', 'day'], axis=1)
df = df.drop(columns = "Unnamed: 0")
# Tampilkan nilai kolom 'date' tanpa bagian jamnya
df['date'] = df['date'].dt.strftime('%Y-%m-%d')




st.write('Cleaned Dataframe:', df)








# Fungsi untuk mengambil data pada tanggal dan stasiun tertentu
def get_specific_date_data(df, date, station):
    return df[(df['date'] == date) & (df['station'] == station)]

# Menampilkan judul
st.title('Visualisasi Tingkat Polusi Udara')

# Mendapatkan tanggal dan stasiun dari user
selected_date = st.date_input("Pilih Tanggal", pd.to_datetime('2013-03-01'))
selected_date = str(selected_date)
st.write(selected_date)

selected_station = st.selectbox("Pilih Stasiun", df['station'].unique())

# Mendapatkan data berdasarkan tanggal dan stasiun yang dipilih
specific_date_data = df[(df['date'] == selected_date) & (df['station'] == selected_station)]

# Membuat plot Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(specific_date_data['hour'], specific_date_data['PM2.5'], marker='o', linestyle='-', color='Red')
ax.set_xlabel('Jam')
ax.set_ylabel('Nilai')
ax.set_title(f'Tingkat Polusi Udara pada {selected_date} di Stasiun {selected_station}')
ax.tick_params(axis='x', rotation=45)

# Menampilkan plot di Streamlit
st.pyplot(fig)






st.set_option('deprecation.showPyplotGlobalUse', False)

# Fungsi untuk membuat heatmap korelasi
def generate_correlation_heatmap(data):
    correlation = data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].corr(method='pearson')
    plt.figure(figsize=(10, 8))
    heatmap = sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Heatmap Korelasi antara PM2.5, PM10, SO2, NO2, CO, dan O3')
    st.pyplot()

# Menampilkan judul
st.title('Heatmap Korelasi antara PM2.5, PM10, SO2, NO2, CO, dan O3')

# Menjalankan fungsi untuk membuat heatmap
generate_correlation_heatmap(df)




# Filter baris untuk jam 0:00 hingga 6:00
filtered_data = df[(df['hour'] >= 0) & (df['hour'] <= 6)]
# Hitung rata-rata nilai PM2.5 dan PM10
avg_pm25 = filtered_data['PM2.5'].mean()
avg_pm10 = filtered_data['PM10'].mean()


# Menampilkan judul
st.title('Rata rata nilai PM2.5 dan PM10 antara jam 0:00 hingga 6:00 pagi')

col1, col2 = st.columns(2)

with col1:
    st.subheader('Jam 0:00 hingga 6:00')
    st.metric(label="PM2.5", value= avg_pm25, delta="µm")
    
with col2:
    st.subheader('Jam 0:00 hingga 6:00')
    st.metric(label="PM10", value= avg_pm10, delta="µm")
    
    
    
    
    
    
    
    
# Judul dashboard
st.title('Scatter Plot Visualizer')




# Pilihan stasiun dan kolom untuk dibandingkan
stations = df['station'].unique()
selected_station = st.selectbox('Pilih Stasiun', stations, key='station_key')
column_list = df.columns.tolist()
selected_columns = st.multiselect('Pilih Kolom', column_list)

# Filter data berdasarkan stasiun yang dipilih
filtered_data = df[df['station'] == selected_station]

# Plot scatter plot menggunakan kolom yang dipilih oleh pengguna
if selected_columns:
    plt.figure(figsize=(8, 6))
    plt.scatter(filtered_data[selected_columns[0]], filtered_data[selected_columns[1]], alpha=0.5)
    plt.title(f'Scatter Plot {selected_columns[0]} vs {selected_columns[1]} di {selected_station}')
    plt.xlabel(selected_columns[0])
    plt.ylabel(selected_columns[1])
    plt.grid(True)
    st.pyplot(plt)
else:
    st.write('Silakan pilih dua kolom untuk memvisualisasikan scatter plot.')
    
    
    









# Streamlit app
st.title('Average Levels per Station')

# Get column names for selection
columns = df.columns.tolist()

# Select columns for visualization
selected_columns = st.selectbox('Select columns', columns)
selected_columns = [selected_columns]

if selected_columns:
    # Calculate average values for selected columns per station
    average_data = df.groupby('station')[selected_columns].mean().reset_index()

    # Sorting based on the first selected column
    sorted_average_data = average_data.sort_values(by=selected_columns[0], ascending=False)

    # Display bar chart using Altair
    import altair as alt
    bars = alt.Chart(sorted_average_data).mark_bar().encode(
        x=alt.X('station', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(selected_columns[0]),  # Using the first selected column for the Y-axis
        tooltip=['station'] + selected_columns
    ).properties(width=alt.Step(80))

    text = bars.mark_text(
        align='center',
        baseline='bottom',
        color = 'white',
        dy=-5  # Adjust the position of the text label
    ).encode(
        text=alt.Text(selected_columns[0], format=".2f")
    )

    chart = (bars + text).properties(height=400)
    st.altair_chart(chart)
    
    
    
    