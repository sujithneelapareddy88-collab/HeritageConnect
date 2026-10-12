
import math
from urllib.parse import quote

import folium
import networkx as nx
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium


# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="HeritageConnect",
    page_icon="🏛️",
    layout="wide",
)

NOMINATIM = "https://nominatim.openstreetmap.org/search"

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

OSRM = "https://router.project-osrm.org"

HEADERS = {
    "User-Agent": "HeritageConnectEducationalProject/1.0"
}


# ============================================================
# UI THEME
# ============================================================
st.markdown("""
<style>
.stApp {
    background: #F5F8FC;
    color: #243B53;
}
.block-container {
    max-width: 100% !important;
    padding: 1.5rem 2rem 2.5rem 2rem !important;
}
[data-testid="stSidebar"] {
    background: #102A43;
}
[data-testid="stSidebar"] * {
    color: #F0F6FC;
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
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
}
.hc-brand-title {
    color: white;
    font-size: 21px;
    font-weight: 750;
}
.hc-brand-subtitle {
    color: #B9CBD9;
    font-size: 11px;
    margin-top: 4px;
}
.hc-hero {
    background: linear-gradient(115deg, #102A43, #174E63, #0F766E);
    color: white;
    border-radius: 20px;
    padding: 26px 30px;
    margin-bottom: 22px;
}
.hc-hero h1 {
    color: white;
    font-size: clamp(27px, 3vw, 38px);
    margin: 0 0 8px 0;
}
.hc-hero p {
    color: #D9E8F2;
    margin: 0;
}
.hc-eyebrow {
    color: #A7F3D0;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
    margin-bottom: 8px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E1EAF2;
    border-radius: 15px;
    padding: 17px;
}
[data-testid="stMetricLabel"] {
    color: #627D98;
}
[data-testid="stMetricValue"] {
    color: #102A43;
    font-weight: 750;
}
.stButton > button {
    border-radius: 10px;
    font-weight: 650;
    min-height: 42px;
}
.stButton > button[kind="primary"] {
    background: #0F766E;
    color: white;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: white !important;
    color: #102A43 !important;
    -webkit-text-fill-color: #102A43 !important;
    border: 1px solid #B8C9D9 !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: white !important;
    color: #102A43 !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "origin": None,
    "attractions": [],
    "search_place": "",
    "route_result": None,
    "route_error": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DISTANCE CALCULATION
# ============================================================
def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate geographic straight-line distance in kilometres."""
    radius = 6371.0

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [float(lat1), float(lon1), float(lat2), float(lon2)],
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    a = max(0.0, min(1.0, a))

    return 2 * radius * math.asin(math.sqrt(a))


# ============================================================
# FIXED TOURISM GRAPH
# ============================================================
def build_graph(points, neighbors=2):
    """
    Create a sparse proximity graph by connecting each location
    to its two nearest locations.

    The graph is undirected, so a connection selected by either
    endpoint is retained.
    """
    graph = nx.Graph()

    for point in points:
        graph.add_node(
            point["name"],
            lat=float(point["lat"]),
            lon=float(point["lon"]),
        )

    # Find nearest neighbors using actual coordinates.
    for i, first in enumerate(points):
        distances = []

        for j, second in enumerate(points):
            if i == j:
                continue

            distance = haversine_km(
                first["lat"],
                first["lon"],
                second["lat"],
                second["lon"],
            )

            distances.append((
                distance,
                second["name"],
            ))

        distances.sort(key=lambda item: item[0])

        for distance, neighbor in distances[:neighbors]:
            graph.add_edge(
                first["name"],
                neighbor,
                distance=distance,
                distance_km=distance,
            )

    return graph


# ============================================================
# CENTRALITY AND NETWORK METRICS
# ============================================================
def calculate_metrics(graph):
    if graph.number_of_nodes() == 0:
        return {
            "degree_centrality": {},
            "betweenness_centrality": {},
            "density": 0.0,
            "components": [],
        }

    return {
        "degree_centrality": nx.degree_centrality(graph),

        # Use hop count for network betweenness.
        "betweenness_centrality": nx.betweenness_centrality(
            graph,
            normalized=True,
        ),

        "density": nx.density(graph),
        "components": list(nx.connected_components(graph)),
    }


# ============================================================
# GEOCODING
# ============================================================
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
            "Place not found. Try a more specific Indian location."
        )

    place = results[0]

    return {
        "name": place["display_name"],
        "lat": float(place["lat"]),
        "lon": float(place["lon"]),
        "category": "Starting place",
    }


# ============================================================
# FETCH ATTRACTIONS
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nearby_attractions(lat, lon, radius_km):
    radii = list(dict.fromkeys(
        [max(1, int(radius_km))]
        + [r for r in (10, 5, 2) if r < int(radius_km)]
    ))

    for radius in radii:
        radius_m = radius * 1000

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
                    key=lambda point: haversine_km(
                        lat, lon,
                        point["lat"], point["lon"],
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
        "Attraction data is temporarily unavailable. Try again later."
    )


# ============================================================
# ROAD ROUTING
# ============================================================
def calculate_road_route(points, optimize=True):
    if len(points) < 2:
        raise ValueError("Select at least one attraction.")

    coordinates = ";".join(
        f'{point["lon"]},{point["lat"]}'
        for point in points
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

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            IndexError,
        ):
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
        raise RuntimeError("No driving route found.")

    route = data["routes"][0]

    return (
        points,
        route["geometry"]["coordinates"],
        route["distance"] / 1000,
        route["duration"] / 60,
    )


# ============================================================
# ROUTE MAP
# ============================================================
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
        if index == 0:
            color, icon, label = "green", "play", "START"
        elif index == len(points) - 1:
            color, icon, label = "red", "flag", "END"
        else:
            color, icon, label = "blue", "info-sign", "STOP"

        folium.Marker(
            [point["lat"], point["lon"]],
            tooltip=f"{label}: {point['name']}",
            popup=f"{label}: {point['name']}",
            icon=folium.Icon(color=color, icon=icon),
        ).add_to(route_map)

    if len(road_path) > 1:
        route_map.fit_bounds(road_path)

    return route_map


# ============================================================
# VEHICLE COST CALCULATOR
# ============================================================
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
        f'{best["Vehicle"]}: '
        f'{int(best["Vehicles needed"])} vehicle(s), '
        f'estimated fuel cost ₹'
        f'{best["Estimated fuel cost (INR)"]:,.2f}'
    )

    return df, recommendation


# ============================================================
# SVG NETWORK GRAPH
# ============================================================
def svg_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def draw_network_graph(graph, route_points):
    nodes = list(graph.nodes)
    count = len(nodes)

    if count == 0:
        st.info("There are no locations to display.")
        return

    width = 1100
    height = 650
    cx = width / 2
    cy = height / 2
    rx = width * 0.36
    ry = height * 0.34

    # Circular layout for readability.
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

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="100%" role="img" aria-label="Tourism network">',
        '<rect width="100%" height="100%" rx="18" fill="#F5F8FC"/>',
    ]

    # Draw edges first.
    for first, second, data in graph.edges(data=True):
        x1, y1 = positions[first]
        x2, y2 = positions[second]

        distance = float(data.get("distance_km", 0.0))

        svg.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            'stroke="#8AA4B8" stroke-width="2" opacity="0.85"/>'
        )

        # Labels are placed near edge midpoints.
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        svg.append(
            f'<text x="{mx:.1f}" y="{my - 5:.1f}" '
            'text-anchor="middle" '
            'font-family="Arial,sans-serif" font-size="10" '
            'fill="#486581">'
            f'{distance:.2f} km</text>'
        )

    start_name = route_points[0]["name"]
    end_name = route_points[-1]["name"]

    # Draw nodes.
    for i, node in enumerate(nodes):
        x, y = positions[node]

        if node == start_name:
            fill, role = "#15803D", "START"
        elif node == end_name:
            fill, role = "#DC2626", "END"
        else:
            fill, role = "#0F766E", "STOP"

        label = svg_escape(node)

        if len(label) > 34:
            label = label[:31] + "..."

        svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" '
            f'fill="{fill}" stroke="#FFFFFF" stroke-width="3"/>'
        )

        svg.append(
            f'<text x="{x:.1f}" y="{y + 4:.1f}" '
            'text-anchor="middle" font-family="Arial,sans-serif" '
            'font-size="11" font-weight="700" fill="#FFFFFF">'
            f'{i + 1}</text>'
        )

        label_y = y + 37 if y < height * 0.78 else y - 30

        svg.append(
            f'<text x="{x:.1f}" y="{label_y:.1f}" '
            'text-anchor="middle" font-family="Arial,sans-serif" '
            'font-size="12" font-weight="600" fill="#102A43">'
            f'{label}</text>'
        )

        svg.append(
            f'<text x="{x:.1f}" y="{label_y + 14:.1f}" '
            'text-anchor="middle" font-family="Arial,sans-serif" '
            f'font-size="9" fill="{fill}">{role}</text>'
        )

    svg.append("</svg>")

    st.components.v1.html(
        "".join(svg),
        height=670,
        scrolling=True,
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown("""
<div class="hc-brand">
  <div class="hc-brand-icon">🏛️</div>
  <div>
    <div class="hc-brand-title">HeritageConnect</div>
    <div class="hc-brand-subtitle">TOURISM INTELLIGENCE</div>
  </div>
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

st.markdown("""
<div class="hc-hero">
  <div class="hc-eyebrow">Explore India • Travel smarter</div>
  <h1>HeritageConnect</h1>
  <p>Plan heritage journeys, compare travel costs, and discover connections between destinations.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SMART TRIP PLANNER
# ============================================================
if page == "Smart Trip Planner":
    st.header("Find attractions anywhere in India")

    with st.form("place_search"):
        place_query = st.text_input(
            "Starting place",
            value=st.session_state["search_place"],
            placeholder="e.g. Tirupati, Jaipur, Mysuru Palace",
        )

        radius_km = st.slider(
            "Search radius (km)",
            min_value=1,
            max_value=100,
            value=30,
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
                            "No attractions found. Try a larger radius."
                        )

                except Exception as error:
                    st.session_state["route_error"] = str(error)

    if st.session_state["route_error"] and not st.session_state["route_result"]:
        st.error(st.session_state["route_error"])

    origin = st.session_state["origin"]
    attractions = st.session_state["attractions"]

    if origin and attractions:
        st.subheader("Available attractions")
        st.write("Starting place:", origin["name"])

        attraction_df = pd.DataFrame([
            {
                "Attraction": point["name"],
                "Category": point["category"],
                "Distance from start (km)": round(
                    haversine_km(
                        origin["lat"], origin["lon"],
                        point["lat"], point["lon"],
                    ),
                    2,
                ),
            }
            for point in attractions
        ])

        st.dataframe(
            attraction_df,
            use_container_width=True,
            hide_index=True,
        )

        lookup = {
            point["name"]: point for point in attractions
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
                min_value=1,
                max_value=500,
                value=3,
            )

        with c2:
            petrol = st.number_input(
                "Petrol price (INR/litre)",
                min_value=1.0,
                value=103.0,
            )

        with c3:
            diesel = st.number_input(
                "Diesel price (INR/litre)",
                min_value=1.0,
                value=91.0,
            )

        cng = st.number_input(
            "CNG price (INR/kg)",
            min_value=1.0,
            value=85.0,
        )

        optimize = st.checkbox(
            "Optimize visit order",
            value=True,
        )

        if st.button(
            "Analyze map and generate route",
            type="primary",
        ):
            st.session_state["route_result"] = None
            st.session_state["route_error"] = None

            if not chosen:
                st.session_state["route_error"] = (
                    "Select at least one attraction."
                )
            else:
                selected = [lookup[name] for name in chosen]

                points = [
                    dict(origin, route_role="start")
                ]

                for i, point in enumerate(selected):
                    role = (
                        "end"
                        if i == len(selected) - 1
                        else "stop"
                    )

                    points.append(
                        dict(point, route_role=role)
                    )

                with st.spinner("Calculating route and costs..."):
                    try:
                        ordered, geometry, distance, minutes = (
                            calculate_road_route(
                                points,
                                optimize,
                            )
                        )

                        vehicle_df, recommendation = (
                            calculate_vehicle_options(
                                int(tourists),
                                distance,
                                petrol,
                                diesel,
                                cng,
                            )
                        )

                        visit_df = pd.DataFrame([
                            {
                                "Order": i + 1,
                                "Place": point["name"],
                                "Category": point.get(
                                    "category", "Attraction"
                                ),
                                "Latitude": point["lat"],
                                "Longitude": point["lon"],
                            }
                            for i, point in enumerate(ordered)
                        ])

                        st.session_state["route_result"] = {
                            "points": ordered,
                            "distance": distance,
                            "minutes": minutes,
                            "map": build_route_map(
                                ordered,
                                geometry,
                            ),
                            "visit_df": visit_df,
                            "vehicle_df": vehicle_df,
                            "recommendation": recommendation,
                        }

                    except Exception as error:
                        st.session_state["route_error"] = str(error)

    if st.session_state["route_error"]:
        st.error(
            "Could not generate route: "
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

        st.subheader("Road route map")
        st_folium(
            result["map"],
            height=720,
            width=None,
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
            result["visit_df"].to_csv(index=False).encode("utf-8"),
            file_name="heritageconnect_visit_order.csv",
            mime="text/csv",
        )


# ============================================================
# GUIDES & ACCOMMODATION
# ============================================================
elif page == "Guides & Accommodation":
    st.header("Guides & Accommodation")

    st.info(
        "Demo directory only. Availability is not verified, "
        "and bookings are not made through this page."
    )

    destination = st.text_input("Destination")

    service = st.selectbox(
        "Service type",
        ["Tour guide", "Hotel", "Homestay", "Transport"],
    )

    if st.button("Search on map"):
        if destination.strip():
            url = (
                "https://www.google.com/maps/search/"
                + quote(service + " near " + destination)
            )

            st.markdown(f"[Open current listings]({url})")
        else:
            st.warning("Enter a destination.")


# ============================================================
# NETWORK ANALYTICS
# ============================================================
elif page == "Network Analytics":
    st.header("Tourism Network Analytics")

    result = st.session_state["route_result"]

    if result:
        points = result["points"]

        st.caption(
            "The graph connects each location to its two nearest "
            "locations. Distances are geographic, not driving distances."
        )

        # Build the graph directly from the latest route points.
        graph = build_graph(points, neighbors=2)
        metrics = calculate_metrics(graph)

        degree = metrics["degree_centrality"]
        between = metrics["betweenness_centrality"]

        metrics_df = pd.DataFrame([
            {
                "Place": node,
                "Degree centrality": round(degree[node], 3),
                "Betweenness centrality": round(between[node], 3),
            }
            for node in graph.nodes
        ])

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Graph nodes", graph.number_of_nodes())
        c2.metric("Graph edges", graph.number_of_edges())
        c3.metric("Network density", round(metrics["density"], 3))
        c4.metric("Connected groups", len(metrics["components"]))

        st.subheader("Centrality metrics")
        st.dataframe(
            metrics_df,
            use_container_width=True,
            hide_index=True,
        )

        # Inspect coordinates and actual distances.
        with st.expander("Inspect coordinates and distances"):
            coordinate_df = pd.DataFrame([
                {
                    "Place": point["name"],
                    "Latitude": round(float(point["lat"]), 6),
                    "Longitude": round(float(point["lon"]), 6),
                }
                for point in points
            ])

            st.write("Coordinates")
            st.dataframe(
                coordinate_df,
                use_container_width=True,
                hide_index=True,
            )

            distance_rows = []

            for i, first in enumerate(points):
                for second in points[i + 1:]:
                    distance = haversine_km(
                        first["lat"], first["lon"],
                        second["lat"], second["lon"],
                    )

                    distance_rows.append({
                        "Place A": first["name"],
                        "Place B": second["name"],
                        "Distance (km)": round(distance, 3),
                        "Connected": graph.has_edge(
                            first["name"],
                            second["name"],
                        ),
                    })

            st.write("Pairwise distances")
            st.dataframe(
                pd.DataFrame(distance_rows),
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Network graph")
        draw_network_graph(graph, points)

        st.subheader("Connected components")

        for i, component in enumerate(
            metrics["components"],
            start=1,
        ):
            st.write(
                f"**Group {i}:** "
                + ", ".join(sorted(component))
            )

        st.caption(
            "Degree centrality measures direct connections. "
            "Betweenness centrality measures how often a node lies "
            "on shortest paths between other nodes."
        )

    else:
        st.info(
            "Generate a trip in Smart Trip Planner first "
            "to view its network analytics."
        )


# ============================================================
# COMMUNITY ISSUES
# ============================================================
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

        submitted = st.form_submit_button("Validate report")

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


# ============================================================
# FOOTER
# ============================================================
st.divider()

st.caption(
    "HeritageConnect educational prototype • "
    "Map data © OpenStreetMap contributors"
)
