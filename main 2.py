from shapely.geometry import Point, Polygon
import xml.etree.ElementTree as ET
import pandas as pd
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon
df = pd.read_csv(
    r"C:/Users/SABRINA/Desktop/AIproject/data/KBOS_100_1672887600.csv"
)

df["Time"] = df["Frame"]
print(df.columns.tolist())
print(type(df))
print(df[["Frame", "Time"]].head(20))
print(df.columns.tolist())
df = df.sort_values(
    by=["ID", "Time"]
).reset_index(drop=True)
df["Delta_Altitude"] = (
    df.groupby("ID")["Altitude"]
      .diff()
)
df["Delta_Altitude"] = (
    df["Delta_Altitude"]
    .fillna(0)
)
THRESHOLD = 20  # feet
def classify_movement(delta_alt):

    if abs(delta_alt) <= THRESHOLD:
        return "Taxiing"

    elif delta_alt > THRESHOLD:
        return "Departure"

    else:
        return "Final"
df["Movement"] = (
    df["Delta_Altitude"]
    .apply(classify_movement)
)
print(
df[
        [
            "ID",
            "Time",
            "Altitude",
            "Delta_Altitude",
            "Movement"
        ]
    ].head(30)
)
surface_df = (
    df[df["Movement"] == "Taxiing"]
    .copy()
)
print(surface_df.head())
SHORT_FINAL_ALTITUDE = 1000
short_final_df = df[
    (df["Movement"] == "Final") &
    (df["Altitude"] <= SHORT_FINAL_ALTITUDE)
].copy()
print(short_final_df.head(20))
print("Number of short-final observations:")
print(len(short_final_df))
print("Aircraft on short final:")
print(short_final_df["ID"].nunique())
aircraft_id = short_final_df["ID"].iloc[0]

aircraft = short_final_df[
    short_final_df["ID"] == aircraft_id
]

print(
    aircraft[
        ["Time",
         "Altitude",
         "Speed",
         "Heading"]
    ]
)
df["On_Short_Final"] = (
    (df["Movement"] == "Final") &
    (df["Altitude"] <= SHORT_FINAL_ALTITUDE)
).astype(int)
print(df["On_Short_Final"].value_counts())
tree = ET.parse("C:/Users/SABRINA/Desktop/AIproject/maps/map (3).osm")
root = tree.getroot()

print("File loaded successfully!")

for element in root.findall("way"):
    for tag in element.findall("tag"):
        k = tag.get("k")
        v = tag.get("v")

        if k == "aeroway":
            print("Aeroway:", v)
import xml.etree.ElementTree as ET

tree = ET.parse(
    r"C:/Users/SABRINA/Desktop/AIproject/maps/map (3).osm"
)
root = tree.getroot()

runway_count = 0

for way in root.findall("way"):

    for tag in way.findall("tag"):

        if (
            tag.get("k") == "aeroway"
            and
            tag.get("v") == "runway"
        ):
            runway_count += 1

            print("\nRUNWAY", runway_count)
            print("Way ID:", way.get("id"))

            for t in way.findall("tag"):
                print(
                    t.get("k"),
                    "=",
                    t.get("v")
                )

print("\nNumber of runways:", runway_count)
import xml.etree.ElementTree as ET

tree = ET.parse(
    r"C:/Users/SABRINA/Desktop/AIproject/maps/map (3).osm"
)
root = tree.getroot()

nodes = {}

for node in root.findall("node"):
    node_id = node.get("id")
    lat = float(node.get("lat"))
    lon = float(node.get("lon"))

    nodes[node_id] = (lat, lon)

print("Number of nodes:", len(nodes))
for way in root.findall("way"):

    tags = {
        tag.get("k"): tag.get("v")
        for tag in way.findall("tag")
    }

    if tags.get("aeroway") == "runway":

        print("\nRunway:", tags.get("ref"))

        coords = []

        for nd in way.findall("nd"):
            node_id = nd.get("ref")

            if node_id in nodes:
                coords.append(nodes[node_id])

        print("Number of points:", len(coords))
        print("First points:", coords[:5])
tree = ET.parse(
    r"C:/Users/SABRINA/Desktop/AIproject/maps/map (3).osm"
)
root = tree.getroot()

nodes = {}

for node in root.findall("node"):
    node_id = node.get("id")
    lat = float(node.get("lat"))
    lon = float(node.get("lon"))

    nodes[node_id] = (lon, lat)
runways = {}

for way in root.findall("way"):

    tags = {
        tag.get("k"): tag.get("v")
        for tag in way.findall("tag")
    }

    if tags.get("aeroway") == "runway":

        runway_name = tags.get(
            "ref",
            way.get("id")
        )

        coords = []

        for nd in way.findall("nd"):
            node_id = nd.get("ref")

            if node_id in nodes:
                coords.append(nodes[node_id])

        if len(coords) >= 3:
            runways[runway_name] = Polygon(coords)

print("Number of runway polygons:",
      len(runways))
row = df.iloc[0]

aircraft = Point(
    row["Lon"],
    row["Lat"]
)
for runway, polygon in runways.items():

    if polygon.contains(aircraft):

        print(
            "Aircraft is on runway:",
            runway
        )
df["Runway"] = None
df["Physical_Occupancy"] = 0

for i, row in df.iterrows():

    aircraft = Point(
        row["Lon"],
        row["Lat"]
    )

    for runway, polygon in runways.items():

        if polygon.contains(aircraft):

            df.at[i, "Runway"] = runway
            df.at[i,
                  "Physical_Occupancy"] = 1

            break
print(
    df[
        [
            "ID",
            "Time",
            "Runway",
            "Physical_Occupancy"
        ]
    ].head(20)
)

print(
    df["Physical_Occupancy"]
    .value_counts()
)
print(df.columns.tolist())
df["Runway_Occupied"] = (
    (df["Physical_Occupancy"] == 1) |
    (df["On_Short_Final"] == 1)
).astype(int)
print(df["Runway_Occupied"].value_counts())
df["Runway"] = None
def assign_runway(heading):
    if pd.isna(heading):
        return None

    # Runways 04 (040°)
    if 20 <= heading < 60:
        return "04L/22R or 04R/22L"

    # Runways 22 (220°)
    elif 200 <= heading < 240:
        return "04L/22R or 04R/22L"

    # Runway 09 (090°)
    elif 70 <= heading < 110:
        return "09/27"

    # Runway 27 (270°)
    elif 250 <= heading < 290:
        return "09/27"

    # Runways 14 (140°)
    elif 120 <= heading < 160:
        return "14/32"

    # Runway 32 (320°)
    elif 300 <= heading < 340:
        return "14/32"

    # Runways 15 (150°)
    elif 140 <= heading < 170:
        return "15L/33R or 15R/33L"

    # Runways 33 (330°)
    elif 320 <= heading < 350:
        return "15L/33R or 15R/33L"

    else:
        return None
df["Runway"] = df["Heading"].apply(assign_runway)
print(
    df[
        ["ID", "Time", "Heading", "Runway"]
    ].head(20)
)
df["Runway_Occupied"] = (
    (
        df["Physical_Occupancy"] == 1
    ) |
    (
        df["On_Short_Final"] == 1
    )
).astype(int)
runway_status = (
    df.groupby(["Time", "Runway"])["Runway_Occupied"]
      .max()
      .reset_index()
)

print(runway_status.head(20))
aircraft_count = (
    df[df["Runway"].notna()]
      .groupby(["Time", "Runway"])
      .size()
      .reset_index(name="Aircraft_Count")
)

print(aircraft_count.head(20))
df = df.sort_values(
    by=["ID", "Time"]
).reset_index(drop=True)

df["Delta_Speed"] = (
    df.groupby("ID")["Speed"]
      .diff()
      .fillna(0)
)
df["Speed_Not_Decreasing"] = (
    df["Delta_Speed"] >= 0
).astype(int)
df["Potential_Incursion"] = (
    (df["Runway_Occupied"] == 1) &
    (df["Speed_Not_Decreasing"] == 1)
).astype(int)
print(
    df[
        [
            "ID",
            "Time",
            "Runway",
            "Runway_Occupied",
            "Speed",
            "Delta_Speed",
            "Potential_Incursion"
        ]
    ].head(30)
)