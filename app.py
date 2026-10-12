import math
import requests
import pandas as pd
import networkx as nx
from analytics import build_graph, calculate_metrics
import streamlit as st
import folium
from streamlit_folium import st_folium

# ==================================================
# CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="HeritageConnect",
    page_icon="🏛️",
    layout="wide",
)

# ==================================================
# PROFESSIONAL UI THEME
# ==================================================
st.markdown("""
<style>
:root {
    --hc-navy: #102A43;
    --hc-teal: #0F766E;
    --hc-teal-light: #E6FFFA;
    --hc-ink: #243B53;
    --hc-muted: #627D98;
}
.stApp {
    background: #F5F8FC;
    color: var(--hc-ink);
}
[data-testid="stAppViewContainer"] > .main {
    background: #F5F8FC;
}
.block-container {
    max-width: 100% !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2.2rem !important;
    padding-right: 2.2rem !important;
}
[data-testid="stSidebar"] {
    background: #102A43;
    border-right: 1px solid #1E405D;
}
[data-testid="stSidebar"] * {
    color: #F0F6FC;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 0.55rem 0.7rem;
    border-radius: 0.65rem;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #1E405D;
}
.hc-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 18px 0;
    border-bottom: 1px solid #36566F;
    margin-bottom: 18px;
}
.hc-brand-icon {
    width: 44px;
    height: 44px;
    border-radius: 13px;
    background: #D9F2E6;
    color: #14532D;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
}
.hc-brand-title {
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 750;
    letter-spacing: -0.4px;
    line-height: 1.15;
}
.hc-brand-subtitle {
    color: #B9CBD9;
    font-size: 11px;
    margin-top: 4px;
}
.hc-hero {
    background: linear-gradient(115deg, #102A43 0%, #174E63 65%, #0F766E 100%);
    color: white;
    border-radius: 20px;
    padding: 26px 30px;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(16, 42, 67, 0.12);
}
.hc-eyebrow {
    color: #A7F3D0;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.hc-hero h1 {
    color: white;
    font-size: clamp(27px, 3vw, 38px);
    line-height: 1.12;
    margin: 0 0 8px 0;
    letter-spacing: -1px;
}
.hc-hero p {
    color: #D9E8F2;
    font-size: 14px;
    margin: 0;
}
h1, h2, h3 {
    color: #102A43;
    letter-spacing: -0.35px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E1EAF2;
    border-radius: 15px;
    padding: 17px 18px;
    box-shadow: 0 3px 12px rgba(16, 42, 67, 0.04);
}
[data-testid="stMetricLabel"] {
    color: #627D98;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #102A43;
    font-weight: 750;
}
.stButton > button, .stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: 650;
    min-height: 42px;
    border: 1px solid #0F766E;
    transition: all 0.15s ease;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: #0F766E;
    color: white;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: #115E59;
    color: #0F766E;
}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid #E1EAF2;
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
hr {
    border-color: #DCE6EF;
}
/* High-contrast widget colors */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
    border: 1px solid #B8C9D9 !important;
    border-radius: 10px !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #627D98 !important;
    -webkit-text-fill-color: #627D98 !important;
    opacity: 1 !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    color: #102A43 !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #102A43 !important;
}
[data-testid="stSlider"] [role="slider"] {
    background-color: #0F766E !important;
    border-color: #0F766E !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #F0F6FC !important;
    background: transparent;
    border: 1px solid transparent;
    transition: background 0.15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #0F766E !important;
    border-color: #5EEAD4 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * {
    color: #FFFFFF !important;
}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"] p,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
    color: #243B53;
}
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="columnheader"] {
    color: #243B53 !important;
}
.hc-section-label {
    color: #0F766E;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin-bottom: 4px;
}
@media (max-width: 800px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .hc-hero {
        padding: 22px;
        border-radius: 15px;
    }
}
</style>
""", unsafe_allow_html=True)

NOMINATIM = "https://nominatim.openstreetmap.org/search"

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

OSRM = "https://router.project-osrm.org"

HEADERS = {
    "User-Agent": "HeritageConnectEducationalProject/1.0"
}

# ==================================================
# SESSION STATE
# ==================================================
for key, value in {
    "origin": None,
    "attractions": [],
    "search_place": "",
    "route_result": None,
    "route_error": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# DISTANCE
# ==================================================
def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(
        min(1, math.sqrt(a))
    )


# ==================================================
# GEOCODING: INDIA-WIDE SEARCH
# ==================================================
def geocode_place(query):
    response = requests.get(
        NOMINATIM,
        params={
            "q": query,
            "format": "jsonv2",
            "limit": 1,
            "countrycodes": "in",
        },
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(
            "Place not found. Try a more specific Indian "
            "city, landmark, heritage site, or address."
        )

    place = results[0]

    return {
        "name": place["display_name"],
        "lat": float(place["lat"]),
        "lon": float(place["lon"]),
        "category": "Starting place",
    }


# ==================================================
# NEARBY ATTRACTIONS
# ==================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nearby_attractions(lat, lon, radius_km):
    """Fetch and cache nearby attractions, with smaller-radius fallbacks."""

    requested_radius = max(1, int(radius_km))

    radii = list(dict.fromkeys(
        [requested_radius]
        + [r for r in (10, 5, 2) if r < requested_radius]
    ))

    for radius in radii:
        radius_m = int(radius * 1000)

        query = f"""
        [out:json][timeout:12];
        (
          nwr(around:{radius_m},{lat},{lon})
            ["tourism"~"attraction|museum|viewpoint|artwork|zoo|gallery|theme_park|aquarium"];
          nwr(around:{radius_m},{lat},{lon})["historic"];
          nwr(around:{radius_m},{lat},{lon})["heritage"];
        );
        out center tags;
        """

        for server in OVERPASS_SERVERS:
            try:
                response = requests.post(
                    server,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=15,
                )

                response.raise_for_status()
                elements = response.json().get("elements", [])

                found = []
                seen = set()

                for item in elements:
                    tags = item.get("tags", {})
                    name = tags.get("name") or tags.get("name:en")

                    if not name:
                        continue

                    if item.get("type") == "node":
                        p_lat = item.get("lat")
                        p_lon = item.get("lon")
                    else:
                        center = item.get("center", {})
                        p_lat = center.get("lat")
                        p_lon = center.get("lon")

                    if p_lat is None or p_lon is None:
                        continue

                    p_lat = float(p_lat)
                    p_lon = float(p_lon)

                    identity = (
                        name.strip().lower(),
                        round(p_lat, 5),
                        round(p_lon, 5),
                    )

                    if identity in seen:
                        continue

                    seen.add(identity)

                    found.append({
                        "name": str(name).strip(),
                        "lat": p_lat,
                        "lon": p_lon,
                        "category": str(
                            tags.get("tourism")
                            or tags.get("historic")
                            or tags.get("heritage")
                            or "Attraction"
                        ).replace("_", " ").title(),
                        "source": "OpenStreetMap",
                    })

                found.sort(
                    key=lambda p: haversine_km(
                        lat, lon, p["lat"], p["lon"]
                    )
                )

                return found

            except (
                requests.RequestException,
                ValueError,
                KeyError,
                TypeError,
            ):
                continue

    raise RuntimeError(
        "Nearby attraction data is temporarily unavailable from "
        "the public map servers. Please wait and try again."
    )


# ==================================================
# ROAD ROUTING
# ==================================================
def calculate_road_route(points, optimize=True):
    if len(points) < 2:
        raise ValueError(
            "Choose at least one attraction besides the start."
        )

    coordinates = ";".join(
        f'{p["lon"]},{p["lat"]}' for p in points
    )

    if optimize and len(points) >= 3:
        try:
            response = requests.get(
                f"{OSRM}/trip/v1/driving/{coordinates}",
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "source": "first",
                    "destination": "last",
                    "roundtrip": "false",
                },
                timeout=60,
            )

            response.raise_for_status()
            data = response.json()

            if data.get("code") == "Ok" and data.get("trips"):
                trip = data["trips"][0]
                waypoints = data.get("waypoints", [])

                order = sorted(
                    range(len(points)),
                    key=lambda i: waypoints[i].get(
                        "waypoint_index", i
                    ),
                )

                ordered = [points[i] for i in order]

                return (
                    ordered,
                    trip["geometry"]["coordinates"],
                    trip["distance"] / 1000,
                    trip["duration"] / 60,
                )

        except Exception:
            pass

    response = requests.get(
        f"{OSRM}/route/v1/driving/{coordinates}",
        params={
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
        },
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError(
            data.get("message", "No driving route found.")
        )

    route = data["routes"][0]

    return (
        points,
        route["geometry"]["coordinates"],
        route["distance"] / 1000,
        route["duration"] / 60,
    )


# ==================================================
# BUILD MAP
# ==================================================
def build_route_map(points, geometry):
    route_map = folium.Map(
        location=[points[0]["lat"], points[0]["lon"]],
        zoom_start=8,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    road_path = [
        [lat, lon] for lon, lat in geometry
    ]

    folium.PolyLine(
        road_path,
        color="#087CF0",
        weight=5,
        opacity=0.85,
        tooltip="Recommended road route",
    ).add_to(route_map)

    for index, point in enumerate(points):
        role = point.get("route_role")

        if role == "start" or index == 0:
            marker_color = "green"
            marker_icon = "play"
            role_label = "START"

        elif role == "end" or index == len(points) - 1:
            marker_color = "red"
            marker_icon = "flag-checkered"
            role_label = "END"

        else:
            marker_color = "blue"
            marker_icon = "coffee"
            role_label = "STOP"

        folium.Marker(
            [point["lat"], point["lon"]],
            tooltip=f"{role_label}: {point['name']}",
            popup=f"{role_label}: {point['name']}",
            icon=folium.Icon(
                color=marker_color,
                icon=marker_icon,
                prefix="fa",
            ),
        ).add_to(route_map)

    if len(road_path) > 1:
        route_map.fit_bounds(road_path)

    return route_map


# ==================================================
# VEHICLE RECOMMENDATION
# ==================================================
def calculate_vehicle_options(
    tourists,
    distance_km,
    petrol_price,
    diesel_price,
    cng_price,
):
    fleet = [
        ("Auto-rickshaw", 3, "CNG", 25, cng_price),
        ("Hatchback", 4, "Petrol", 16, petrol_price),
        ("Sedan", 4, "Petrol", 15, petrol_price),
        ("SUV", 6, "Diesel", 12, diesel_price),
        ("Tempo Traveller", 12, "Diesel", 9, diesel_price),
    ]

    rows = []

    for name, capacity, fuel, mileage, price in fleet:
        vehicles = math.ceil(tourists / capacity)

        cost = (
            vehicles
            * (distance_km / mileage)
            * price
        )

        rows.append({
            "Vehicle": name,
            "Fuel": fuel,
            "Capacity per vehicle": capacity,
            "Vehicles needed": vehicles,
            "Mileage (km/unit)": mileage,
            "Estimated fuel cost (INR)": round(cost, 2),
            "Cost per tourist (INR)": round(
                cost / tourists, 2
            ),
        })

    df = pd.DataFrame(rows).sort_values(
        "Estimated fuel cost (INR)"
    )

    best = df.iloc[0]

    recommendation = (
        f'{best["Vehicle"]}, '
        f'{int(best["Vehicles needed"])} vehicle(s), '
        f'estimated fuel cost ₹'
        f'{best["Estimated fuel cost (INR)"]:,.2f}'
    )

    return df, recommendation


# ==================================================
# GRAPH ANALYTICS
# ==================================================
def tourism_graph(points):
    """Build a graph connecting consecutive route locations."""

    graph = nx.Graph()

    for point in points:
        graph.add_node(point["name"])

    for i in range(len(points) - 1):
        first = points[i]
        second = points[i + 1]

        distance = haversine_km(
            first["lat"],
            first["lon"],
            second["lat"],
            second["lon"],
        )

        graph.add_edge(
            first["name"],
            second["name"],
            distance_km=distance,
        )

    return graph


# ==================================================
# SIDEBAR AND HEADER
# ==================================================
st.sidebar.markdown("""
<div class="hc-brand">
  <div class="hc-brand-icon">🏛️</div>
  <div>
    <div class="hc-brand-title">HeritageConnect</div>
    <div class="hc-brand-subtitle">TOURISM INTELLIGENCE</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hc-hero">
  <div class="hc-eyebrow">Explore India • Travel smarter</div>
  <h1>HeritageConnect</h1>
  <p>Plan heritage journeys, compare travel costs, and discover connections between destinations.</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "WORKSPACE",
    [
        "Smart Trip Planner",
        "Guides & Accommodation",
        "Network Analytics",
        "Community Issues",
    ],
)

st.caption(
    "LIVE MAP DATA · OpenStreetMap and public routing services. "
    "Please verify road conditions, opening hours, fuel prices, and provider details."
)


# ==================================================
# SMART TRIP PLANNER
# ==================================================
if page == "Smart Trip Planner":
    st.markdown(
        '<div class="hc-section-label">PLAN A JOURNEY</div>',
        unsafe_allow_html=True,
    )

    st.header("Find attractions anywhere in India")

    with st.form("place_search"):
        place_query = st.text_input(
            "Starting place",
            value=st.session_state["search_place"],
            placeholder="e.g. Tirupati, Jaipur, Mysuru Palace",
        )

        radius_km = st.slider(
            "Search radius (km)",
            1,
            100,
            30,
        )

        search_clicked = st.form_submit_button(
            "Find nearby attractions"
        )

    if search_clicked:
        st.session_state["search_place"] = place_query.strip()
        st.session_state["origin"] = None
        st.session_state["attractions"] = []
        st.session_state["route_result"] = None
        st.session_state["route_error"] = None

        if not place_query.strip():
            st.error("Enter a starting place.")

        else:
            with st.spinner("Searching map data..."):
                try:
                    origin = geocode_place(place_query)

                    attractions = fetch_nearby_attractions(
                        origin["lat"],
                        origin["lon"],
                        radius_km,
                    )

                    st.session_state["origin"] = origin
                    st.session_state["attractions"] = attractions

                    if attractions:
                        st.success(
                            f"Found {len(attractions)} attractions."
                        )
                    else:
                        st.warning(
                            "No named attractions found. "
                            "Try a larger radius or another place."
                        )

                except Exception as error:
                    st.session_state["route_error"] = str(error)

    if (
        st.session_state["route_error"]
        and not st.session_state["route_result"]
    ):
        st.error(st.session_state["route_error"])

    origin = st.session_state["origin"]
    attractions = st.session_state["attractions"]

    if origin and attractions:
        st.subheader("Select your attractions")

        st.write("Starting place:", origin["name"])

        df_attractions = pd.DataFrame([
            {
                "Attraction": point["name"],
                "Category": point["category"],
                "Distance from start (km)": round(
                    haversine_km(
                        origin["lat"],
                        origin["lon"],
                        point["lat"],
                        point["lon"],
                    ),
                    1,
                ),
                "Source": point["source"],
            }
            for point in attractions
        ])

        st.dataframe(
            df_attractions,
            use_container_width=True,
            hide_index=True,
        )

        lookup = {
            point["name"]: point
            for point in attractions
        }

        chosen = st.multiselect(
            "Choose places to visit",
            options=list(lookup.keys()),
            key="chosen_attractions",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            tourists = st.number_input(
                "Number of tourists",
                1,
                500,
                3,
            )

        with c2:
            petrol = st.number_input(
                "Petrol price (INR/litre)",
                1.0,
                value=103.0,
            )

        with c3:
            diesel = st.number_input(
                "Diesel price (INR/litre)",
                1.0,
                value=91.0,
            )

        cng = st.number_input(
            "CNG price (INR/kg)",
            1.0,
            value=85.0,
        )

        optimize = st.checkbox(
            "Optimize visit order",
            value=True,
        )

        if st.button(
            "Analyze map and generate route",
            type="primary",
            key="generate_route",
        ):
            st.session_state["route_result"] = None
            st.session_state["route_error"] = None

            if not chosen:
                st.session_state["route_error"] = (
                    "Select at least one attraction."
                )

            else:
                selected_points = [
                    lookup[name] for name in chosen
                ]

                points = [
                    dict(origin, route_role="start")
                ]

                points.extend(
                    dict(
                        point,
                        route_role=(
                            "end"
                            if i == len(selected_points) - 1
                            else "stop"
                        ),
                    )
                    for i, point in enumerate(selected_points)
                )

                with st.spinner(
                    "Calculating route and fuel costs..."
                ):
                    try:
                        ordered, geometry, km, minutes = (
                            calculate_road_route(
                                points,
                                optimize,
                            )
                        )

                        vehicle_df, recommendation = (
                            calculate_vehicle_options(
                                int(tourists),
                                km,
                                petrol,
                                diesel,
                                cng,
                            )
                        )

                        visit_df = pd.DataFrame([
                            {
                                "Order": index + 1,
                                "Place": point["name"],
                                "Category": point.get(
                                    "category",
                                    "Attraction",
                                ),
                                "Latitude": point["lat"],
                                "Longitude": point["lon"],
                            }
                            for index, point in enumerate(ordered)
                        ])

                        route_map = build_route_map(
                            ordered,
                            geometry,
                        )

                        st.session_state["route_result"] = {
                            "points": ordered,
                            "distance": km,
                            "minutes": minutes,
                            "map": route_map,
                            "visit_df": visit_df,
                            "vehicle_df": vehicle_df,
                            "recommendation": recommendation,
                        }

                    except Exception as error:
                        st.session_state["route_error"] = (
                            f"{type(error).__name__}: {error}"
                        )

    # Display results outside the button block.
    if st.session_state["route_error"]:
        st.error(
            "Could not generate the route: "
            + st.session_state["route_error"]
        )

    result = st.session_state["route_result"]

    if result:
        st.divider()
        st.header("Route summary")

        a, b, c = st.columns(3)

        a.metric(
            "Driving distance",
            f'{result["distance"]:.1f} km',
        )

        b.metric(
            "Estimated driving time",
            f'{result["minutes"]:.0f} min',
        )

        c.metric(
            "Attractions",
            str(len(result["points"]) - 1),
        )

        st.subheader("Visit order")

        st.dataframe(
            result["visit_df"],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Connected road route")

        st_folium(
            result["map"],
            height=720,
            width=1400,
            key="heritageconnect_route_map",
            returned_objects=[],
        )

        st.subheader("Vehicle recommendation")

        st.success(result["recommendation"])

        st.dataframe(
            result["vehicle_df"],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download visit order CSV",
            result["visit_df"].to_csv(
                index=False
            ).encode("utf-8"),
            file_name="heritageconnect_visit_order.csv",
            mime="text/csv",
        )

        st.caption(
            "Fuel costs are estimates. Public OSRM routing does "
            "not guarantee the globally shortest or cheapest trip."
        )


# ==================================================
# GUIDES AND ACCOMMODATION
# ==================================================
elif page == "Guides & Accommodation":
    st.header("Guides & Accommodation")

    st.info(
        "Demo directory only. It does not verify availability "
        "or make real bookings."
    )

    destination = st.text_input("Destination")

    service = st.selectbox(
        "Service type",
        [
            "Tour guide",
            "Hotel",
            "Homestay",
            "Transport",
        ],
    )

    if st.button("Search on map"):
        if destination.strip():
            from urllib.parse import quote

            url = (
                "https://www.google.com/maps/search/"
                + quote(service + " near " + destination)
            )

            st.markdown(
                f"[Open current listings]({url})"
            )

        else:
            st.warning("Enter a destination.")


# ==================================================
# NETWORK ANALYTICS
# ==================================================
elif page == "Network Analytics":
    st.header("Tourism Network Analytics")

    result = st.session_state["route_result"]

    if result:
        # Build a proximity network from the selected trip locations.
        graph = build_graph(
            result["points"],
            max_distance_km=25,
        )

        calculated = calculate_metrics(graph)

        degree = calculated["degree_centrality"]
        between = calculated["betweenness_centrality"]

        metrics = pd.DataFrame([
            {
                "Place": node,
                "Degree centrality": round(
                    degree[node],
                    3,
                ),
                "Betweenness centrality": round(
                    between[node],
                    3,
                ),
            }
            for node in graph.nodes
        ])

        left, right = st.columns(2)

        left.metric(
            "Graph nodes",
            graph.number_of_nodes(),
        )

        right.metric(
            "Graph edges",
            graph.number_of_edges(),
        )

        st.metric(
            "Network density",
            round(calculated["density"], 3),
        )

        st.metric(
            "Connected groups",
            len(calculated["components"]),
        )

        st.dataframe(
            metrics,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Network graph")

        st.caption(
            "Each node represents a selected location. Lines connect "
            "locations within 25 km of one another and show straight-line "
            "distances. This is a proximity network, not a road network."
        )

        nodes = list(graph.nodes)
        count = len(nodes)

        width = 1000
        height = 520
        cx = width / 2
        cy = height / 2
        rx = width * 0.37
        ry = height * 0.34

        positions = {}

        for i, node in enumerate(nodes):
            angle = (
                -math.pi / 2
                + 2 * math.pi * i / max(count, 1)
            )

            positions[node] = (
                cx + rx * math.cos(angle),
                cy + ry * math.sin(angle),
            )

        def svg_escape(value):
            return (
                str(value)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" '
            f'width="100%" role="img" '
            f'aria-label="Tourism network graph">',
            '<rect width="100%" height="100%" '
            'rx="18" fill="#F5F8FC"/>',
        ]

        # Draw edges before nodes.
        for u, v, data in graph.edges(data=True):
            x1, y1 = positions[u]
            x2, y2 = positions[v]

            distance = data.get("distance_km", 0)

            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                f'x2="{x2:.1f}" y2="{y2:.1f}" '
                'stroke="#8AA4B8" stroke-width="1.8" '
                'opacity="0.9"/>'
            )

            svg_parts.append(
                f'<text x="{mx:.1f}" y="{my - 5:.1f}" '
                'text-anchor="middle" '
                'font-family="Arial,sans-serif" '
                'font-size="11" fill="#486581">'
                f'{distance:.1f} km</text>'
            )

        # Draw nodes.
        for i, node in enumerate(nodes):
            x, y = positions[node]

            if i == 0:
                fill, tag = "#15803D", "START"
            elif i == len(nodes) - 1:
                fill, tag = "#DC2626", "END"
            else:
                fill, tag = "#0F766E", "STOP"

            label = svg_escape(node)

            short_label = (
                label
                if len(label) <= 34
                else label[:31] + "..."
            )

            svg_parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" '
                'r="18" '
                f'fill="{fill}" '
                'stroke="#FFFFFF" stroke-width="3"/>'
            )

            svg_parts.append(
                f'<text x="{x:.1f}" y="{y + 4:.1f}" '
                'text-anchor="middle" '
                'font-family="Arial,sans-serif" '
                'font-size="10" font-weight="700" '
                f'fill="#FFFFFF">{i + 1}</text>'
            )

            label_y = (
                y + 35
                if y < height * 0.78
                else y - 29
            )

            svg_parts.append(
                f'<text x="{x:.1f}" y="{label_y:.1f}" '
                'text-anchor="middle" '
                'font-family="Arial,sans-serif" '
                'font-size="12" font-weight="600" '
                'fill="#102A43">'
                f'{short_label}</text>'
            )

            svg_parts.append(
                f'<text x="{x:.1f}" y="{label_y + 14:.1f}" '
                'text-anchor="middle" '
                'font-family="Arial,sans-serif" '
                'font-size="9" '
                f'fill="{fill}">{tag}</text>'
            )

        svg_parts.append("</svg>")

        svg_markup = "".join(svg_parts)

        st.components.v1.html(
            svg_markup,
            height=540,
            scrolling=True,
        )

        st.subheader("Connected components")

        for index, component in enumerate(
            calculated["components"],
            start=1,
        ):
            st.write(
                f"**Group {index}:** "
                + ", ".join(sorted(component))
            )

        st.caption(
            "Degree centrality measures direct connections. "
            "Betweenness centrality measures how often a location "
            "lies on shortest paths between other locations."
        )

    else:
        st.info(
            "Generate a trip first to view its graph analytics."
        )


# ==================================================
# COMMUNITY ISSUES
# ==================================================
elif page == "Community Issues":
    st.header("Community Tourism Issues")

    st.warning(
        "Prototype form only. Reports are not saved or sent "
        "to authorities."
    )

    with st.form("community_issue"):
        location = st.text_input("Location")

        issue = st.selectbox(
            "Issue type",
            [
                "Waste management",
                "Road condition",
                "Safety",
                "Accessibility",
                "Tourist information",
                "Other",
            ],
        )

        details = st.text_area("Description")

        submitted = st.form_submit_button(
            "Validate report"
        )

        if submitted:
            if location.strip() and details.strip():
                st.success(
                    "Form validated for demonstration only; "
                    "nothing was permanently submitted."
                )
            else:
                st.error(
                    "Enter the location and issue description."
                )


st.divider()

st.caption(
    "HeritageConnect educational prototype • "
    "Map data © OpenStreetMap contributors"
)
