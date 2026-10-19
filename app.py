import streamlit as st
import pandas as pd
st.set_page_config(
    page_title="Traffic Accident Detection",
    page_icon="🚗",
    layout="wide"
)
st.title("🚦 AI Traffic Accident Detection")
st.write("Smart system for detecting traffic accidents.")
st.divider()
data = pd.read_csv("alerts.csv")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("System Status")
    st.success("System is running")
with col2:
    st.subheader("Accident Alerts")
    accident_count = (
    data["Accident Detected"].astype(str).str.strip().str.lower() == "yes"
).sum()

    st.metric("Detected Accidents", int(accident_count))
    st.caption("Total accidents detected by the AI model")
with col3:
    st.subheader("Camera Status")
    st.info("Waiting for video")

st.divider()


pending_count = (
    data["Alert Status"]
    .astype(str).str.strip().str.lower() == "pending"
).sum()

st.metric("Pending Alerts", int(pending_count))

total_records = len(data)

accident_count = (
    data["Accident Detected"]
    .astype(str).str.strip().str.lower() == "yes"
).sum()

no_accident_count = total_records - accident_count

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", total_records)

with col2:
    st.metric("Accidents Detected", int(accident_count))

with col3:
    st.metric("No Accident", int(no_accident_count))

st.subheader("Accident Overview")

chart_data = pd.DataFrame({
    "Status": ["Accident", "No Accident"],
    "Count": [int(accident_count), int(no_accident_count)]
})

st.bar_chart(chart_data, x="Status", y="Count")

st.divider()

st.header("📹 Video Monitoring")


uploaded_video = st.file_uploader(
    "Upload a road video",
    type=["mp4", "avi", "mov"]
)

if uploaded_video is not None:
    st.video(uploaded_video)
else:
    st.info("Upload a road video to start viewing.")

st.header("Accident Log")



data = pd.read_csv("alerts.csv")


st.subheader("🚨 Accident Alerts")

accidents = data[
    data["Accident Detected"].astype(str).str.strip().str.lower() == "yes"
]

if not accidents.empty:
    st.warning(f"⚠️ {len(accidents)} accident alert(s) need attention.")

    for _, accident in accidents.iterrows():
        st.write(f"📍 Location: {accident['Camera Location']}")
        st.write(f"🕒 Time: {accident['Time']}")
        st.write(f"🎯 Confidence: {accident['Confidence']}")
        st.write(f"📨 Alert Status: {accident['Alert Status']}")
        st.divider()
else:
    st.success("No accidents recorded in the current data.")

st.subheader("📋 Accident Log")
st.dataframe(data, use_container_width=True)

st.caption(
    "Demo data only — no real accidents detected and no emergency alerts sent."
)


