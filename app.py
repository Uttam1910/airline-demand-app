import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time as dt_time
from geopy.distance import great_circle
import pytz

# --- UI Configuration ---
st.set_page_config(
    page_title="✈️ AirTravel Analytics | Market Demand Dashboard",
    layout="wide",
    page_icon="✈️"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        /* Global styles */
        .main { background-color: #f5f7fa; }
        .header { color: #2c3e50; }
        .subheader { color: #1e3d73; border-bottom: 2px solid #1e3d73; padding-bottom: 8px; }
        .metric { text-align: center; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); background: white; }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        .footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 0.9em; }
        .tabs { margin-top: 20px; }
        .stAlert { border-left: 4px solid #1e3d73; }
        .stSpinner > div { text-align: center; }
        .stRadio > div { flex-direction: row; gap: 20px; }

        /* Button styling */
        .stButton>button {
            background-color: #1e3d73;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
        }

        /* In-app controls */
        .stSelectbox, .stTextInput, .stSlider {
            background-color: white !important;
            color: #000000 !important;
        }

        /* Sidebar-specific overrides */
        [data-testid="stSidebar"] .stSlider>div,
        [data-testid="stSidebar"] .stSelectbox>div,
        [data-testid="stSidebar"] .stTextInput>div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        [data-testid="stSidebar"] .widget-label,
        [data-testid="stSidebar"] label {
            color: #000000 !important;
        }
        [data-testid="stSidebar"] .stSlider input[type=range] {
            accent-color: #1e3d73;  /* dark-blue thumb & track */
        }
    </style>
""", unsafe_allow_html=True)



# --- App Header ---
st.title("✈️ AirTravel Analytics")
st.markdown("### Market Demand Intelligence Dashboard for Australian Airline Industry")
st.markdown("Analyze real-time flight demand trends, pricing patterns, and route popularity across Australian airports")

# --- Airport Database ---
airport_db = {
    "YSSY": {"name": "Sydney Kingsford Smith", "coords": (-33.9461, 151.1772), "city": "Sydney"},
    "YMML": {"name": "Melbourne Airport", "coords": (-37.6733, 144.8433), "city": "Melbourne"},
    "YBBN": {"name": "Brisbane Airport", "coords": (-27.3842, 153.1175), "city": "Brisbane"},
    "YPPH": {"name": "Perth Airport", "coords": (-31.9403, 115.9669), "city": "Perth"},
    "YPAD": {"name": "Adelaide Airport", "coords": (-34.9450, 138.5306), "city": "Adelaide"},
    "YBCG": {"name": "Gold Coast Airport", "coords": (-28.1644, 153.5047), "city": "Gold Coast"},
    "YSCB": {"name": "Canberra Airport", "coords": (-35.3069, 149.1950), "city": "Canberra"},
    "YMHB": {"name": "Hobart Airport", "coords": (-42.8361, 147.5103), "city": "Hobart"},
    "YPDN": {"name": "Darwin Airport", "coords": (-12.4083, 130.8728), "city": "Darwin"},
    "YBCS": {"name": "Cairns Airport", "coords": (-16.8858, 145.7553), "city": "Cairns"},
}

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("🔍 Data Parameters")




    
    # Airport Selection
    airport_options = [f"{airport_db[code]['city']} ({code})" for code in airport_db]
    selected_airport = st.selectbox(
        "Select Airport", 
        airport_options,
        index=0
    )
    airport_code = selected_airport.split('(')[-1].replace(')', '')
    
    # Time Range Selection - Fixed layout
    st.write("Time Range")
    time_option = st.radio(
        "", 
        ["Last 6 Hours", "Last 12 Hours", "Last 24 Hours", "Custom Range"],
        index=1,
        label_visibility="collapsed"
    )
    
    if time_option == "Custom Range":
        today = datetime.now().date()
        start_date = st.date_input("Start Date", value=today - timedelta(days=1))
        end_date = st.date_input("End Date", value=today)
        
        # Convert dates to datetime objects
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        
        # Convert to timestamps
        start_time = int(start_datetime.timestamp())
        end_time = int(end_datetime.timestamp())
    else:
        hours = int(time_option.split()[1])
        end_time = int(time.time())
        start_time = end_time - (hours * 3600)
    
    # Additional Filters
    st.subheader("Advanced Filters")
    min_flights = st.slider("Minimum Flights for Routes", 1, 50, 3)
    price_range = st.slider("Price Range (AUD)", 50, 1000, (100, 500))
    
    # Data Refresh
    st.markdown("---")
    st.button("🔄 Refresh Data", use_container_width=True)

# --- Helper Functions ---
def calculate_distance(dep_code, arr_code):
    """Calculate distance between two airports in km"""
    try:
        dep_coords = airport_db[dep_code]["coords"]
        arr_coords = airport_db[arr_code]["coords"]
        return round(great_circle(dep_coords, arr_coords).km, 2)
    except:
        return None

def generate_price(distance, base_fare=50, km_rate=0.15):
    """Generate realistic ticket price based on distance"""
    if distance is None:
        return np.random.randint(100, 500)
    return round(base_fare + (distance * km_rate) + np.random.randint(-30, 100), 2)

def calculate_demand_factor(hour):
    """Calculate demand factor based on time of day"""
    if 6 <= hour < 10:   # Morning peak
        return 1.4
    elif 16 <= hour < 20: # Evening peak
        return 1.6
    elif 10 <= hour < 16: # Midday
        return 1.2
    else:                 # Night
        return 0.8

def generate_insights(df, airport_code):
    """Generate data-driven insights without AI"""
    if df.empty:
        return "No data available to generate insights"
    
    insights = []
    
    # Top routes insight
    top_routes = df['estArrivalAirport'].value_counts().head(3)
    route_descs = []
    for code in top_routes.index:
        if code in airport_db:
            city_name = airport_db[code]["city"]
            route_descs.append(f"{city_name} ({code})")
        else:
            route_descs.append(f"Unknown ({code})")
    insights.append(f"**Top Routes:** {', '.join(route_descs)}")
    
    # Pricing insights
    avg_price = df['Price'].mean()
    price_comparison = "above" if avg_price > 350 else "below"
    insights.append(f"**Pricing:** Average ticket price ${avg_price:.2f} AUD ({price_comparison} industry average)")
    
    # Demand patterns
    peak_hour = df['Hour'].value_counts().idxmax()
    insights.append(f"**Peak Demand:** Highest at {peak_hour}:00 ({df['Hour'].value_counts().max()} flights)")
    
    # Route efficiency
    if not df.empty:
        longest_route = df.loc[df['Distance (km)'].idxmax()]
        shortest_route = df.loc[df['Distance (km)'].idxmin()]
        
        # Get city names safely
        longest_city = airport_db.get(longest_route['estArrivalAirport'], {}).get('city', 'Unknown')
        shortest_city = airport_db.get(shortest_route['estArrivalAirport'], {}).get('city', 'Unknown')
        
        insights.append(f"**Longest Route:** {longest_city} ({longest_route['Distance (km)']} km)")
        insights.append(f"**Shortest Route:** {shortest_city} ({shortest_route['Distance (km)']} km)")
        
        # Price-performance analysis
        df['Price per km'] = df['Price'] / df['Distance (km)']
        if not df['Price per km'].empty:
            best_value = df.loc[df['Price per km'].idxmin()]
            best_value_city = airport_db.get(best_value['estArrivalAirport'], {}).get('city', 'Unknown')
            insights.append(f"**Best Value:** {best_value_city} at ${best_value['Price']:.2f} ({best_value['Distance (km)']} km)")
    
    return "\n\n".join(insights)

# --- Data Loading ---
@st.cache_data(ttl=3600, show_spinner="Fetching flight data from OpenSky API...")
def load_flight_data(airport_code, start_time, end_time):
    """Fetch flight data from OpenSky API"""
    try:
        url = f"https://opensky-network.org/api/flights/departure?airport={airport_code}&begin={start_time}&end={end_time}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return None

# --- Main Dashboard ---
if st.button("🚀 Analyze Flight Demand", use_container_width=True, type="primary"):
    with st.spinner("Processing flight data and generating insights..."):
        data = load_flight_data(airport_code, start_time, end_time)
        
        if data is None or not data:
            st.warning(f"No flight data available for {airport_db[airport_code]['city']} in the selected time range")
        else:
            df = pd.DataFrame(data)
            
            # Data Cleaning
            required_cols = ['callsign', 'estDepartureAirport', 'estArrivalAirport', 'firstSeen', 'lastSeen']
            if not all(col in df.columns for col in required_cols):
                st.error("Required columns missing from API response")
                st.stop()
                
            df = df[required_cols]
            df.dropna(inplace=True)
            df = df[df['estArrivalAirport'].isin(airport_db.keys())]
            
            # Feature Engineering
            df['Departure Time'] = pd.to_datetime(df['firstSeen'], unit='s')
            df['Arrival Time'] = pd.to_datetime(df['lastSeen'], unit='s')
            df['Duration (min)'] = (df['Arrival Time'] - df['Departure Time']).dt.total_seconds() / 60
            df['Hour'] = df['Departure Time'].dt.hour
            df['Day of Week'] = df['Departure Time'].dt.day_name()
            df['Date'] = df['Departure Time'].dt.date
            
            # Calculate distances and prices
            df['Distance (km)'] = df.apply(
                lambda x: calculate_distance(x['estDepartureAirport'], x['estArrivalAirport']), 
                axis=1
            )
            df['Price'] = df.apply(
                lambda x: generate_price(x['Distance (km)']) * calculate_demand_factor(x['Hour']), 
                axis=1
            )
            
            # Filter by price range
            df = df[(df['Price'] >= price_range[0]) & (df['Price'] <= price_range[1])]
            
            # --- Dashboard Layout ---
            st.success(f"✅ Successfully analyzed {len(df)} flights from {airport_db[airport_code]['city']}")
            
            # Display time range
            start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')
            end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M')
            st.caption(f"⏱️ Data Time Range: {start_dt} to {end_dt}")
            
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Flights", len(df), "Departures")
            avg_price = df['Price'].mean() if not df.empty else 0
            col2.metric("Avg. Ticket Price", f"${avg_price:.2f} AUD", 
                        f"{'▲ High' if avg_price > 350 else '▼ Low'} season")
            
            peak_hour = df['Hour'].value_counts().idxmax() if not df.empty else "N/A"
            peak_flights = df['Hour'].value_counts().max() if not df.empty else 0
            col3.metric("Busiest Hour", f"{peak_hour}:00", f"{peak_flights} flights")
            
            top_dest = df['estArrivalAirport'].value_counts().index[0] if not df.empty else "N/A"
            top_dest_city = airport_db.get(top_dest, {}).get('city', 'Unknown') if not df.empty else "N/A"
            col4.metric("Popular Destination", f"{top_dest_city} ({top_dest})")
            
            st.markdown("---")
            
            # Tab-based Layout
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Route Analysis", "💰 Pricing Trends", "⏱️ Demand Patterns", "🗺️ Route Map", "📋 Data Explorer"])
            
            with tab1:  # Route Analysis
                st.subheader("✈️ Flight Route Analysis")
                
                # Top Routes
                route_counts = df['estArrivalAirport'].value_counts().reset_index()
                route_counts.columns = ['Arrival Airport', 'Flights']
                route_counts = route_counts[route_counts['Flights'] >= min_flights]
                
                if not route_counts.empty:
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        fig1 = px.bar(
                            route_counts.head(10),
                            x='Arrival Airport',
                            y='Flights',
                            text='Flights',
                            title=f"Top Flight Routes from {airport_db[airport_code]['city']}",
                            color='Flights',
                            color_continuous_scale='Teal',
                            hover_data={'Arrival Airport': False},
                            custom_data=['Arrival Airport']
                        )
                        fig1.update_traces(
                            textposition='outside',
                            hovertemplate="<b>%{customdata[0]}</b><br>%{y} flights"
                        )
                        fig1.update_layout(height=500, plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        st.subheader("Route Efficiency")
                        
                        if not df.empty:
                            # Calculate efficiency metrics
                            route_efficiency = df.groupby('estArrivalAirport').agg({
                                'Distance (km)': 'mean',
                                'Duration (min)': 'mean',
                                'Price': 'mean'
                            }).reset_index()
                            route_efficiency['Price per km'] = route_efficiency['Price'] / route_efficiency['Distance (km)']
                            
                            # Sort by efficiency
                            efficient_routes = route_efficiency.sort_values('Price per km').head(5)
                            efficient_routes['Route'] = efficient_routes['estArrivalAirport'].apply(
                                lambda x: f"{airport_db.get(x, {}).get('city', 'Unknown')} ({x})"
                            )
                            
                            st.dataframe(
                                efficient_routes[['Route', 'Price per km']].set_index('Route'),
                                use_container_width=True
                            )
                            
                            st.markdown("**Key Insights:**")
                            st.markdown("- ✈️ Shorter routes have higher price per km")
                            st.markdown("- 🌆 City routes are more efficient than regional")
                        else:
                            st.warning("No efficiency data available")
                else:
                    st.warning("No routes meet the minimum flight threshold")
            
            with tab2:  # Pricing Trends
                st.subheader("💰 Pricing Analysis")
                
                if not df.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Price vs Distance
                        fig2 = px.scatter(
                            df,
                            x='Distance (km)',
                            y='Price',
                            color='estArrivalAirport',
                            title="Price vs Distance",
                            trendline="ols",
                            labels={'Distance (km)': 'Distance (km)', 'Price': 'Price (AUD)'},
                            hover_data=['estArrivalAirport', 'Hour']
                        )
                        fig2.update_traces(marker=dict(size=8, opacity=0.7))
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    with col2:
                        # Price distribution
                        fig3 = px.box(
                            df,
                            y='Price',
                            title="Ticket Price Distribution",
                            points="all",
                            color_discrete_sequence=['#1e3d73']
                        )
                        fig3.update_layout(showlegend=False)
                        st.plotly_chart(fig3, use_container_width=True)
                    
                    # Price by time of day
                    st.subheader("Hourly Pricing Trends")
                    hourly_prices = df.groupby('Hour')['Price'].mean().reset_index()
                    
                    fig4 = px.line(
                        hourly_prices,
                        x='Hour',
                        y='Price',
                        title="Average Ticket Price by Hour of Day",
                        markers=True
                    )
                    fig4.update_layout(
                        xaxis=dict(tickmode='linear', dtick=1),
                        yaxis_title="Price (AUD)",
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig4.add_vrect(x0=6, x1=10, fillcolor="green", opacity=0.1, annotation_text="Morning Peak")
                    fig4.add_vrect(x0=16, x1=20, fillcolor="red", opacity=0.1, annotation_text="Evening Peak")
                    st.plotly_chart(fig4, use_container_width=True)
                else:
                    st.warning("No pricing data available")
            
            with tab3:  # Demand Patterns
                st.subheader("⏱️ Demand Patterns")
                
                if not df.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Hourly demand
                        hourly = df.groupby('Hour').size().reset_index(name='Flights')
                        fig5 = px.bar(
                            hourly,
                            x='Hour',
                            y='Flights',
                            title="Flight Departures by Hour",
                            color='Flights',
                            color_continuous_scale='Blues'
                        )
                        fig5.update_layout(
                            xaxis=dict(tickmode='linear', dtick=1),
                            yaxis_title="Number of Flights"
                        )
                        st.plotly_chart(fig5, use_container_width=True)
                    
                    with col2:
                        # Daily demand
                        daily = df.groupby('Day of Week').size().reset_index(name='Flights')
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        daily['Day of Week'] = pd.Categorical(daily['Day of Week'], categories=day_order, ordered=True)
                        daily = daily.sort_values('Day of Week')
                        
                        fig6 = px.line(
                            daily,
                            x='Day of Week',
                            y='Flights',
                            title="Weekly Demand Pattern",
                            markers=True
                        )
                        fig6.update_layout(yaxis_title="Number of Flights")
                        st.plotly_chart(fig6, use_container_width=True)
                    
                    # Demand vs Price
                    st.subheader("Demand vs Pricing Relationship")
                    demand_price = df.groupby('Hour').agg({'Price': 'mean', 'callsign': 'count'}).reset_index()
                    demand_price.columns = ['Hour', 'Avg Price', 'Flights']
                    
                    fig7 = px.scatter(
                        demand_price,
                        x='Flights',
                        y='Avg Price',
                        size='Flights',
                        color='Hour',
                        title="Demand-Price Relationship",
                        labels={'Flights': 'Number of Flights', 'Avg Price': 'Average Price (AUD)'},
                        trendline="ols"
                    )
                    st.plotly_chart(fig7, use_container_width=True)
                else:
                    st.warning("No demand data available")
            
            with tab4:  # Route Map
                st.subheader("🗺️ Flight Route Visualization")
                
                if not df.empty:
                    # Create base map
                    fig8 = go.Figure()
                    
                    # Add routes
                    for _, row in df.iterrows():
                        dep_coords = airport_db[row['estDepartureAirport']]["coords"]
                        arr_coords = airport_db[row['estArrivalAirport']]["coords"]
                        
                        fig8.add_trace(go.Scattergeo(
                            lon=[dep_coords[1], arr_coords[1]],
                            lat=[dep_coords[0], arr_coords[0]],
                            mode='lines',
                            line=dict(width=1, color='#1e3d73'),
                            opacity=0.5,
                            showlegend=False
                        ))
                    
                    # Add airport markers
                    airports_in_data = pd.unique(df[['estDepartureAirport', 'estArrivalAirport']].values.ravel('K'))
                    airport_points = [airport_db[code]["coords"] for code in airports_in_data if code in airport_db]
                    
                    if airport_points:
                        lats, lons = zip(*airport_points)
                        fig8.add_trace(go.Scattergeo(
                            lon=lons,
                            lat=lats,
                            mode='markers',
                            marker=dict(size=10, color='#e74c3c'),
                            text=[airport_db[code]["name"] for code in airports_in_data],
                            name='Airports'
                        ))
                    
                    # Update map layout
                    fig8.update_geos(
                        projection_type="natural earth",
                        showland=True,
                        landcolor="rgb(243, 243, 243)",
                        countrycolor="rgb(204, 204, 204)",
                        showocean=True,
                        oceancolor="rgb(212, 236, 255)",
                        showcountries=True,
                        showcoastlines=True
                    )
                    
                    fig8.update_layout(
                        title=f"Flight Routes from {airport_db[airport_code]['name']}",
                        height=600,
                        geo=dict(
                            scope='world',
                            projection_scale=3,
                            center=dict(lat=airport_db[airport_code]["coords"][0], 
                                       lon=airport_db[airport_code]["coords"][1])
                        )
                    )
                    
                    st.plotly_chart(fig8, use_container_width=True)
                else:
                    st.warning("No data available for map visualization")
            
            with tab5:  # Data Explorer and Insights
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📋 Flight Data Explorer")
                    st.dataframe(
                        df.sort_values('Departure Time', ascending=False).head(100),
                        use_container_width=True,
                        height=600
                    )
                
                with col2:
                    st.subheader("📈 Market Insights")
                    insights = generate_insights(df, airport_code)
                    st.info(insights)
                    
                    st.subheader("📌 Strategic Recommendations")
                    st.markdown("""
                    - **Increase capacity** during peak hours (6-10 AM, 4-8 PM)
                    - **Optimize pricing** for high-demand routes
                    - **Promote off-peak** travel with discounted fares
                    - **Expand service** to underserved destinations
                    - **Bundle offers** for popular city pairs
                    """)
            
            # Data Export
            st.markdown("---")
            st.subheader("📥 Export Data")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Full Dataset (CSV)",
                data=csv,
                file_name=f"flight_demand_{airport_code}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime='text/csv'
            )

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>AirTravel Analytics Dashboard • Real-time Market Intelligence • Data Source: OpenSky Network API</p>
        <p>Note: Ticket prices are simulated based on route distance and demand patterns for demonstration purposes</p>
    </div>
""", unsafe_allow_html=True)