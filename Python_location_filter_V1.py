import pandas as pd
import streamlit as st
import base64
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

@st.cache(ttl=60*60*24) # Cache results for 24 hours
def get_country(city):
    try:
        geolocator = Nominatim(user_agent="MksGeopyApp1")
        location = geolocator.geocode(city, timeout=10, language='en')
        return location.address.split(', ')[-1]
    except (AttributeError, GeocoderTimedOut):
        return None

def app():
    # Set title and subtitle, additional text
    st.title("Location Filter V2")
    st.subheader("Property of Connected Circles")
    st.write("""This app allows you to filter lists of profiles by seniority. By default, it uses a set of keywords to detect and filter CXO+ level profiles 
    (incl. partners and VPs etc.). It uses 2 sets of keywords, one that is case-sensitive and one that is case insensitive. This avoids errors such as the 
    inclusion of 'aCCOunt managers' when searching for 'CCO'. Both sets of keywords are fully customizable and keywords can be added or removed. Keywords must 
    be separated by a comma, whitespace will be considered a part of a keyword. You can preview the both the labeled and filtered data in the two preview 
    windows below. You can download the data either labeled, filtered or filtered profile URLs only, all as a .csv""")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file to filter", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Clean the location data
        df['Country'] = df['Location'].apply(get_country)
        
        # Remove unnecessary columns
        df = df.drop(columns=['Location', 'Location2'], errors='ignore')

        # Country filter
        countries = st.multiselect('Select countries', sorted(df['Country'].unique()))
        if countries:
            dffiltered = df[df["Country"].isin(countries)]
        else:
            dffiltered = df.copy()

        
        
        # Download link for filtered data
        csv_filtered = dffiltered.to_csv(index=False)
        b64_filtered = base64.b64encode(csv_filtered.encode('utf-8')).decode()
        href_filtered = f'<a href="data:file/csv;base64,{b64_filtered}" download="filtered_data.csv">Download Filtered CSV File</a>'
        
        # Download link for unfiltered data
        csv_unfiltered = df.to_csv(index=False)
        b64_unfiltered = base64.b64encode(csv_unfiltered.encode('utf-8')).decode()
        href_unfiltered = f'<a href="data:file/csv;base64,{b64_unfiltered}" download="unfiltered_data.csv">Download Unfiltered Labeled CSV File</a>'
        
        # Download link for filtered data URLs only, no header
        url_col = dffiltered["Profile url"].dropna().astype(str)
        csv_url = url_col.to_csv(index=False, header=False)
        b64_url = base64.b64encode(csv_url.encode('utf-8')).decode()
        href_url = f'<a href="data:file/csv;base64,{b64_url}" download="profile_urls.csv">Download Filtered Profile URLs only CSV File</a>'


##### DISPLAY OF RESULTS #####
        
        # Display both filtered and unfiltered data in two windows with links to download each below
        col1, col2 = st.beta_columns(2)
        with col1:
            st.write("Unfiltered Data")
            st.write(df)
            st.markdown(href_unfiltered, unsafe_allow_html=True)
        with col2:
            st.write("Filtered Data")
            st.write(dffiltered)
            st.markdown(href_filtered, unsafe_allow_html=True)
            
        # Display the link to download profile URLs of filtered data only
        st.markdown(href_url, unsafe_allow_html=True)

if __name__ == "__main__":
    app()
