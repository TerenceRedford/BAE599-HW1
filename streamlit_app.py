import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os
import numpy as np
import calendar
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Terence's Enzyme Research Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .profile-container {
        text-align: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_climate_data():
    """Load the climate data from CSV file"""
    try:
        return pd.read_csv('climate_data.csv')
    except Exception as e:
        st.error(f"Error loading climate data: {e}")
        return None

def get_weather_data(city, country_code):
    """Get historical humidity data from climate data CSV"""
    try:
        # Load the climate data
        climate_df = load_climate_data()
        if climate_df is None:
            return None
            
        # Get data for the selected city
        city_data = climate_df[climate_df['City'] == city]
        if city_data.empty:
            st.error(f"No data available for {city}")
            return None
        
        # Get current month (1-12)
        current_month = datetime.now().month
        
        # Get the monthly values (columns are named Jan, Feb, etc.)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_values = [city_data[month] for month in months]
        
        # Get the current, previous, and next month's values
        current_month_idx = current_month - 1  # 0-based index
        monthly_humidity = monthly_values[current_month_idx]
        prev_month_humidity = monthly_values[current_month_idx-1 if current_month_idx > 0 else 11]
        next_month_humidity = monthly_values[(current_month_idx+1) % 12]
        
        # Calculate daily values for the month
        daily_humidity = []
        dates = []
        
        # Get the number of days in the current month
        year = datetime.now().year
        month = datetime.now().month
        _, days_in_month = calendar.monthrange(year, month)
        
        for day in range(1, days_in_month + 1):
            # Calculate the progression through the month (0 to 1)
            progress = (day - 1) / (days_in_month - 1)
            
            # Interpolate between months for smoother transitions
            if progress < 0.2:  # First fifth of the month
                humidity = prev_month_humidity * (0.2 - progress) / 0.2 + monthly_humidity * progress / 0.2
            elif progress > 0.8:  # Last fifth of the month
                humidity = monthly_humidity * (1 - progress) / 0.2 + next_month_humidity * (progress - 0.8) / 0.2
            else:  # Middle of the month
                humidity = monthly_humidity
            
            daily_humidity.append(round(humidity, 1))
            dates.append(datetime(year, month, day).strftime('%Y-%m-%d'))
        
        return {
            'current_humidity': round(monthly_humidity, 1),
            'daily_humidity': daily_humidity,
            'dates': dates,
            'annual_average': city_data['Annual_Avg'],
            'latitude': city_data['Latitude'],
            'longitude': city_data['Longitude']
        }
    except Exception as e:
        st.error(f"Error processing climate data: {e}")
        return None

def show_humidity_analysis():
    """Display humidity analysis section"""
    st.markdown('<h2 class="section-header">🌤️ Global Humidity Analysis</h2>', unsafe_allow_html=True)
    st.markdown("*Historical climate data analysis for enzyme research applications*")
    
    # Load available cities and countries
    climate_df = load_climate_data()
    if climate_df is None:
        return
    
    # Create selection columns
    col1, col2 = st.columns(2)
    
    with col1:
        countries = climate_df[['Country_Code']].drop_duplicates()
        selected_country = st.selectbox(
            "🌍 Select Country:",
            options=countries['Country_Code'].tolist(),
            index=0
        )
    
    with col2:
        cities = climate_df[climate_df['Country_Code'] == selected_country]['City'].tolist()
        selected_city = st.selectbox(
            "🏙️ Select City:",
            options=cities,
            index=0
        )
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #e1e4e8; margin-bottom: 1rem; font-size: 0.9rem; color: #2c3e50;'>
        📊 Data Source: World Bank Climate Data<br>
        • Historical monthly averages from weather stations<br>
        • 30-year climate normals (1991-2020)<br>
        • Daily variations modeled from monthly patterns<br>
        • Data compiled from national meteorological services
    </div>
    """, unsafe_allow_html=True)
    
    # Country and city selection
    col1, col2 = st.columns(2)
    
    # Define countries and their major cities
    country_cities = {
        'US': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
        'GB': ['London', 'Manchester', 'Birmingham', 'Glasgow', 'Liverpool'],
        'DE': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt'],
        'FR': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
        'JP': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Kobe'],
        'AU': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
        'CA': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
        'IN': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata'],
        'CN': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu'],
        'BR': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'],
        'ZA': ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Port Elizabeth']
    }
    
    country_names = {
        'US': 'United States', 'GB': 'United Kingdom', 'DE': 'Germany', 
        'FR': 'France', 'JP': 'Japan', 'AU': 'Australia',
        'CA': 'Canada', 'IN': 'India', 'CN': 'China', 'BR': 'Brazil',
        'ZA': 'South Africa'
    }
    
    with col1:
        selected_country = st.selectbox(
            "🌍 Select Country:",
            options=list(country_names.keys()),
            format_func=lambda x: country_names[x],
            index=0
        )
    
    with col2:
        selected_city = st.selectbox(
            "🏙️ Select City:",
            options=country_cities[selected_country],
            index=0
        )
    
    if st.button("🔍 Get Humidity Data", type="primary"):
        with st.spinner(f"Fetching humidity data for {selected_city}, {country_names[selected_country]}..."):
            weather_data = get_weather_data(selected_city, selected_country)
            
            if weather_data:
                # Defensive checks for valid humidity data
                if (weather_data['current_humidity'] is None or
                    not isinstance(weather_data['current_humidity'], (int, float)) or
                    not weather_data['daily_humidity'] or
                    any([h is None or not isinstance(h, (int, float)) for h in weather_data['daily_humidity']])):
                    st.warning("Humidity data is missing or invalid for this city.")
                else:
                    # Display current humidity
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            label="🌡️ Current Humidity",
                            value=f"{weather_data['current_humidity']}%",
                            delta=None
                        )
                    with col2:
                        avg_humidity = np.mean(weather_data['daily_humidity'])
                        st.metric(
                            label="📊 30-Day Average",
                            value=f"{avg_humidity:.1f}%",
                            delta=f"{weather_data['current_humidity'] - avg_humidity:.1f}% vs avg"
                        )
                    with col3:
                        if len(weather_data['daily_humidity']) >= 7:
                            humidity_trend = "↗️ Rising" if weather_data['daily_humidity'][-1] > weather_data['daily_humidity'][-7] else "↘️ Falling"
                            st.metric(
                                label="📈 7-Day Trend",
                                value=humidity_trend,
                                delta=f"{abs(weather_data['daily_humidity'][-1] - weather_data['daily_humidity'][-7]):.1f}%"
                            )
                        else:
                            st.metric(
                                label="📈 7-Day Trend",
                                value="N/A",
                                delta=None
                            )
                
                # Humidity trend chart
                st.markdown("### 📅 30-Day Humidity Trend")
                
                df_humidity = pd.DataFrame({
                    'Date': pd.to_datetime(weather_data['dates']),
                    'Humidity (%)': weather_data['daily_humidity']
                })
                
                fig_humidity = px.line(
                    df_humidity, 
                    x='Date', 
                    y='Humidity (%)',
                    title=f"Humidity Trend for {selected_city}, {country_names[selected_country]}",
                    line_shape='spline'
                )
                
                fig_humidity.add_hline(
                    y=weather_data['current_humidity'], 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text="Current Humidity"
                )
                
                st.plotly_chart(fig_humidity, use_container_width=True)
                
                # Environmental insights
                st.markdown("### 🔬 Environmental Research Insights")
                
                if weather_data['current_humidity'] > 70:
                    st.success(f"🌿 **High Humidity Environment**: {selected_city} currently has {weather_data['current_humidity']}% humidity. This is ideal for studying hygrophilic enzymes and moisture-dependent biochemical processes.")
                elif weather_data['current_humidity'] < 40:
                    st.warning(f"🏜️ **Low Humidity Environment**: {selected_city} has {weather_data['current_humidity']}% humidity. Consider this for enzyme stability studies under dry conditions.")
                else:
                    st.info(f"⚖️ **Moderate Humidity**: {selected_city} shows {weather_data['current_humidity']}% humidity, providing balanced conditions for most enzyme research applications.")
                
                # Download humidity data
                csv_humidity = df_humidity.to_csv(index=False)
                st.download_button(
                    label="📥 Download Humidity Data",
                    data=csv_humidity,
                    file_name=f"humidity_data_{selected_city}_{selected_country}.csv",
                    mime="text/csv"
                )

def main():
    # Main header
    st.markdown('<h1 class="main-header">🧬 Enzyme Research Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### *An Interactive Analysis of Industrial and Biological Enzymes*")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile section
        st.markdown('<div class="profile-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">� Personal Profile</h2>', unsafe_allow_html=True)
        
        # Display profile image
        try:
            image_path = "Terence.Redford.jpg"
            if os.path.exists(image_path):
                image = Image.open(image_path)
                st.image(image, width=200)
            else:
                st.info("Profile image not found. Please ensure 'Terence.Redford.jpg' is in the current directory.")
        except Exception as e:
            st.error(f"Error loading image: {e}")
        
        st.markdown("""
        **Name:** Terence Redford  
        **Course:** BAE AI Class  
        **Research Focus:** Enzymology & Biocatalysis  
        **Project:** Industrial Enzyme Analysis Dashboard  
        **Specialization:** Food and Bioprocess Engineering
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Dataset overview
        st.markdown('<h2 class="section-header">🧪 Enzyme Dataset Overview</h2>', unsafe_allow_html=True)
        
        # Load the dataset
        try:
            df = pd.read_csv("enzyme_dataset.tsv", sep='\t')
            
            # Display basic statistics
            col2a, col2b, col2c, col2d = st.columns(4)
            
            with col2a:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Total Enzymes", len(df))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2b:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Enzyme Classes", df['Classification'].nunique())
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2c:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Avg Km Value", f"{df['Km_Value'].mean():.2f} mM")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2d:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("Max Temp", f"{df['Temperature_Optimum'].max()}°C")
                st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            st.info("Please ensure 'enzyme_dataset.tsv' is in the current directory.")
            return
    
    # Sidebar for filtering
    st.sidebar.markdown("## 🔬 Filter Options")
    
    # Classification filter
    classifications = ['All'] + list(df['Classification'].unique())
    selected_class = st.sidebar.selectbox("Select Enzyme Classification:", classifications)
    
    # Temperature range filter
    temp_range = st.sidebar.slider("Temperature Range (°C):", 
                                  min_value=int(df['Temperature_Optimum'].min()), 
                                  max_value=int(df['Temperature_Optimum'].max()),
                                  value=(int(df['Temperature_Optimum'].min()), int(df['Temperature_Optimum'].max())))
    
    # pH range filter
    ph_range = st.sidebar.slider("pH Range:",
                                min_value=float(df['pH_Optimum'].min()),
                                max_value=float(df['pH_Optimum'].max()),
                                value=(float(df['pH_Optimum'].min()), float(df['pH_Optimum'].max())),
                                step=0.5)
    
    # Molecular weight filter
    mw_threshold = st.sidebar.number_input("Min Molecular Weight (Da):", 
                                          min_value=0, 
                                          max_value=int(df['Molecular_Weight'].max()),
                                          value=0)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_class != 'All':
        filtered_df = filtered_df[filtered_df['Classification'] == selected_class]
    
    filtered_df = filtered_df[(filtered_df['Temperature_Optimum'] >= temp_range[0]) & 
                             (filtered_df['Temperature_Optimum'] <= temp_range[1])]
    filtered_df = filtered_df[(filtered_df['pH_Optimum'] >= ph_range[0]) & 
                             (filtered_df['pH_Optimum'] <= ph_range[1])]
    filtered_df = filtered_df[filtered_df['Molecular_Weight'] >= mw_threshold]
    
    # Main content area
    st.markdown('<h2 class="section-header">📊 Enzyme Analysis & Visualizations</h2>', unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧪 Overview", "⚡ Kinetics", "🌡️ Conditions", "🔬 Applications", "📋 Data Table"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Classification distribution pie chart
            class_counts = filtered_df['Classification'].value_counts()
            fig_pie = px.pie(values=class_counts.values, 
                           names=class_counts.index,
                           title="Enzyme Classification Distribution",
                           color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Molecular weight distribution
            fig_hist = px.histogram(filtered_df, x='Molecular_Weight', nbins=15,
                                  title="Molecular Weight Distribution",
                                  labels={'Molecular_Weight': 'Molecular Weight (Da)'},
                                  color_discrete_sequence=['#1f77b4'])
            fig_hist.update_layout(bargap=0.1)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Organism source analysis
        organism_counts = filtered_df['Organism'].value_counts().head(10)
        fig_organism = px.bar(x=organism_counts.values, y=organism_counts.index,
                             title="Top 10 Enzyme Source Organisms",
                             orientation='h',
                             labels={'x': 'Number of Enzymes', 'y': 'Organism'},
                             color=organism_counts.values,
                             color_continuous_scale='Viridis')
        fig_organism.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_organism, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Km vs Vmax scatter plot
            fig_kinetics = px.scatter(filtered_df, x='Km_Value', y='Vmax',
                                    color='Classification', size='Molecular_Weight',
                                    title="Enzyme Kinetics: Km vs Vmax",
                                    labels={'Km_Value': 'Km Value (mM)', 'Vmax': 'Vmax (units/mg)'},
                                    hover_data=['Enzyme_Name', 'Organism'])
            fig_kinetics.update_layout(xaxis_type="log", yaxis_type="log")
            st.plotly_chart(fig_kinetics, use_container_width=True)
        
        with col2:
            # Enzyme efficiency (Vmax/Km) analysis
            filtered_df['Efficiency'] = filtered_df['Vmax'] / filtered_df['Km_Value']
            top_efficient = filtered_df.nlargest(10, 'Efficiency')
            
            fig_efficiency = px.bar(top_efficient, x='Efficiency', y='Enzyme_Name',
                                   title="Top 10 Most Efficient Enzymes (Vmax/Km)",
                                   orientation='h',
                                   color='Classification',
                                   labels={'Efficiency': 'Catalytic Efficiency (Vmax/Km)'})
            fig_efficiency.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Kinetic parameters by classification
        fig_box = px.box(filtered_df, x='Classification', y='Km_Value',
                        title="Km Values by Enzyme Classification",
                        color='Classification')
        fig_box.update_layout(
            xaxis={'tickangle': 45},
            yaxis_type="log"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature vs pH scatter plot
            fig_conditions = px.scatter(filtered_df, x='pH_Optimum', y='Temperature_Optimum',
                                      color='Classification', size='Vmax',
                                      title="Optimal Operating Conditions",
                                      labels={'pH_Optimum': 'Optimal pH', 'Temperature_Optimum': 'Optimal Temperature (°C)'},
                                      hover_data=['Enzyme_Name', 'Organism'])
            st.plotly_chart(fig_conditions, use_container_width=True)
        
        with col2:
            # Temperature distribution by classification
            fig_temp_violin = px.violin(filtered_df, x='Classification', y='Temperature_Optimum',
                                       title="Temperature Optima by Classification",
                                       color='Classification')
            fig_temp_violin.update_layout(xaxis={'tickangle': 45})
            st.plotly_chart(fig_temp_violin, use_container_width=True)
        
        # pH distribution analysis
        fig_ph_hist = px.histogram(filtered_df, x='pH_Optimum', color='Classification',
                                  title="pH Optima Distribution",
                                  labels={'pH_Optimum': 'Optimal pH'},
                                  marginal="box")
        st.plotly_chart(fig_ph_hist, use_container_width=True)
    
    with tab4:
        # Application analysis
        app_counts = filtered_df['Application'].value_counts()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_app = px.bar(x=app_counts.values, y=app_counts.index,
                           title="Enzyme Applications",
                           orientation='h',
                           color=app_counts.values,
                           color_continuous_scale='Plasma')
            fig_app.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_app, use_container_width=True)
        
        with col2:
            st.markdown("### 🏭 Industrial Applications")
            for app, count in app_counts.head(5).items():
                st.write(f"**{app}**: {count} enzymes")
        
        # Substrate-Product network (simplified view)
        st.markdown("### 🔄 Substrate-Product Relationships")
        substrate_product = filtered_df[['Enzyme_Name', 'Substrate', 'Product', 'Classification']].head(10)
        st.dataframe(substrate_product, use_container_width=True)
    
    with tab5:
        # Interactive data table
        st.markdown("### 🗂️ Complete Enzyme Dataset")
        
        # Display filtered data with enhanced styling
        st.dataframe(
            filtered_df.style.highlight_max(axis=0, subset=['Vmax', 'Temperature_Optimum'])
                           .highlight_min(axis=0, subset=['Km_Value']),
            use_container_width=True,
            height=400
        )
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered enzyme data as CSV",
            data=csv,
            file_name=f"filtered_enzymes_{len(filtered_df)}_records.csv",
            mime="text/csv"
        )
        
        # Summary statistics
        st.markdown("### 📊 Statistical Summary")
        numeric_cols = ['Km_Value', 'Vmax', 'Temperature_Optimum', 'pH_Optimum', 'Molecular_Weight']
        st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)
        
        # Correlation analysis
        if len(filtered_df) > 1:
            st.markdown("### 🔗 Correlation Analysis")
            corr_matrix = filtered_df[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, 
                               title="Enzyme Parameter Correlations",
                               color_continuous_scale='RdBu_r',
                               aspect="auto")
            fig_corr.update_layout(width=600, height=500)
            st.plotly_chart(fig_corr, use_container_width=True)
    
    # Add humidity analysis section
    st.markdown("---")
    show_humidity_analysis()
    
    # Citation and Footer
    st.markdown("---")
    
    # Citation section
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #e1e4e8; margin-bottom: 2rem;'>
        <h3 style='color: #2c3e50; font-size: 1.5rem; margin-bottom: 1rem;'>📚 Dataset Source</h3>
        <p style='margin-bottom: 1rem; font-family: monospace; font-size: 1rem; color: #2c3e50;'>
            Dataset compiled from BRENDA - The Comprehensive Enzyme Information System:<br>
            Jeske, L., Placzek, S., Schomburg, I., Chang, A., & Schomburg, D. (2019). 
            "BRENDA in 2019: a European ELIXIR core data resource." 
            <em>Nucleic Acids Research</em>, 47(D1), D542-D549.<br>
            <a href="https://doi.org/10.1093/nar/gky1048" style="color: #2850a7;">https://doi.org/10.1093/nar/gky1048</a>
        </p>
        <p style='color: #2c3e50; font-size: 0.95rem;'>
            <strong>Access Date:</strong> September 5, 2025<br>
            <strong>Usage:</strong> Data adapted from BRENDA database for educational purposes.
            Visit <a href="https://www.brenda-enzymes.org" style="color: #2850a7;">www.brenda-enzymes.org</a> for the complete database.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🧬 <strong>BAE AI Class - Enzyme Research Project</strong> | Created by <strong>Terence Redford</strong></p>
        <p>📊 Dataset: Industrial & Biological Enzymes | 🧪 Built with Streamlit & Biochemical Data Science</p>
        <p>🔬 <em>Advancing understanding of enzyme kinetics and biotechnology applications</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
