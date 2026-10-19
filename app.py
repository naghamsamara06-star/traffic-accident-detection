
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. إعداد الصفحة والتحديث التلقائي
# ==========================================
st.set_page_config(
    page_title="Traffic Accident Detection",
    page_icon="🚦",
    layout="wide"
)

st_autorefresh(interval=3000, key="traffic_refresh")

# ==========================================
# 2. القائمة الجانبية واللغة
# ==========================================
with st.sidebar:
    st.title("🚦 Traffic Monitor")

    language = st.selectbox(
        "Language / اللغة",
        ["العربية", "English"]
    )

    is_ar = language == "العربية"

    if is_ar:
        pages = [
            "🏠 الرئيسية",
            "🚨 الحوادث والتنبيهات",
            "📹 مراقبة الفيديو",
            "🗺️ خريطة الحوادث"
        ]
        menu_label = "القائمة الرئيسية"
    else:
        pages = [
            "🏠 Dashboard",
            "🚨 Accidents & Alerts",
            "📹 Video Monitoring",
            "🗺️ Accident Map"
        ]
        menu_label = "Main Menu"

    page = st.radio(menu_label, pages)

    st.divider()
    st.subheader("🔔 إعدادات الإنذار")

    sound_enabled = st.toggle(
        "تفعيل صوت الإنذار" if is_ar else "Enable alarm sound",
        value=True,
        key="sound_enabled"
    )

# تحديد الصفحة المختارة
dashboard_page = page == pages[0]
alerts_page = page == pages[1]
video_page = page == pages[2]
map_page = page == pages[3]

# ==========================================
# 3. النصوص حسب اللغة
# ==========================================
if is_ar:
    title = "نظام اكتشاف الحوادث المرورية"
    subtitle = "لوحة المراقبة الذكية للطرق والتقاطعات"
    status_title = "حالة النظام"
    running = "النظام يعمل"
    stats_title = "إحصائيات المرور"
    total_label = "إجمالي السجلات"
    accident_label = "الحوادث المكتشفة"
    normal_label = "بدون حادث"
    pending_label = "التنبيهات المعلّقة"
    video_title = "مراقبة الفيديو"
    upload_label = "ارفعي فيديو للطريق"
    waiting_video = "ارفعي فيديو لعرضه هنا"
    alerts_title = "تنبيهات الحوادث"
    log_title = "سجل الحوادث"
    location_label = "الموقع"
    time_label = "الوقت"
    confidence_label = "نسبة الثقة"
    alert_status_label = "حالة التنبيه"
    no_accidents = "لا توجد حوادث مسجّلة في البيانات الحالية"
    demo_note = (
        "بيانات تجريبية فقط — لم يتم ربط نموذج اكتشاف "
        "الحوادث الحقيقي أو إرسال تنبيهات للطوارئ."
    )
else:
    title = "AI Traffic Accident Detection"
    subtitle = "Smart monitoring dashboard for roads and intersections"
    status_title = "System Status"
    running = "System is running"
    stats_title = "Traffic Statistics"
    total_label = "Total Records"
    accident_label = "Accidents Detected"
    normal_label = "No Accident"
    pending_label = "Pending Alerts"
    video_title = "Video Monitoring"
    upload_label = "Upload a road video"
    waiting_video = "Upload a video to display it here"
    alerts_title = "Accident Alerts"
    log_title = "Accident Log"
    location_label = "Location"
    time_label = "Time"
    confidence_label = "Confidence"
    alert_status_label = "Alert Status"
    no_accidents = "No accidents recorded in the current data"
    demo_note = (
        "Demo data only — the real accident detection model "
        "and emergency notifications are not connected yet."
    )

# ==========================================
# 4. التصميم الداكن
# ==========================================
st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #e5e7eb;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #f1f5f9;
}
div[data-testid="stMetric"] {
    background-color: #172033;
    border: 1px solid #29364b;
    padding: 16px;
    border-radius: 12px;
}
div[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}
div[data-testid="stMetricValue"] {
    color: #38bdf8;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. قراءة البيانات وتجهيزها
# ==========================================
data = pd.read_csv("alerts.csv")

required_columns = [
    "Time",
    "Camera Location",
    "Accident Detected",
    "Confidence",
    "Alert Status"
]

for column in required_columns:
    if column not in data.columns:
        if column == "Accident Detected":
            data[column] = "No"
        elif column == "Alert Status":
            data[column] = "No Alert"
        else:
            data[column] = "Unknown"

accident_mask = (
    data["Accident Detected"]
    .astype(str).str.strip().str.lower() == "yes"
)

accidents = data[accident_mask].copy()

total_records = len(data)
accident_count = int(accident_mask.sum())
no_accident_count = total_records - accident_count

pending_count = int(
    (
        data["Alert Status"]
        .astype(str).str.strip().str.lower() == "pending"
    ).sum()
)

has_accident = not accidents.empty

# ==========================================
# 6. اكتشاف الحوادث الجديدة
# ==========================================
if "known_row_count" not in st.session_state:
    # السجلات الموجودة عند أول تشغيل لا تطلق إنذارًا
    st.session_state.known_row_count = total_records
    new_accident = False

elif total_records > st.session_state.known_row_count:
    new_rows = data.iloc[st.session_state.known_row_count:]

    new_accident = (
        new_rows["Accident Detected"]
        .astype(str).str.strip().str.lower() == "yes"
    ).any()

    st.session_state.known_row_count = total_records

elif total_records < st.session_state.known_row_count:
    st.session_state.known_row_count = total_records
    new_accident = False

else:
    new_accident = False

# ==========================================
# 7. إعداد صوت الإنذار
# ==========================================
if sound_enabled and new_accident:
    st.toast(
        "🚨 تم تسجيل حادث جديد!" if is_ar
        else "🚨 A new accident has been recorded!"
    )

# إبقاء اختبار الصوت في الشريط الجانبي
with st.sidebar:
    sound_html = """
    <div style="font-family:Arial;text-align:center;">
      <button id="testSound"
        style="background:#b91c1c;color:white;border:none;
        padding:10px;border-radius:8px;font-size:14px;
        cursor:pointer;width:100%;">
        🔊 اختبار الصوت
      </button>
      <div id="soundStatus"
        style="color:#cbd5e1;font-size:12px;margin-top:5px;">
      </div>
    </div>
    <script>
    const shouldAlarm = __SHOULD_ALARM__;

    async function playAlarm() {
        const AudioClass =
            window.AudioContext || window.webkitAudioContext;

        if (!AudioClass) return;

        const ctx = new AudioClass();
        await ctx.resume();

        const oscillator = ctx.createOscillator();
        const gain = ctx.createGain();

        oscillator.type = "sine";
        oscillator.frequency.value = 880;
        gain.gain.value = 0.2;

        oscillator.connect(gain);
        gain.connect(ctx.destination);

        oscillator.start();
        oscillator.stop(ctx.currentTime + 0.5);

        oscillator.onended = () => ctx.close();
    }

    document.getElementById("testSound").addEventListener(
        "click", () => playAlarm()
    );

    if (shouldAlarm) {
        playAlarm().catch(() => {});
    }
    </script>
    """

    sound_html = sound_html.replace(
        "__SHOULD_ALARM__",
        str(bool(sound_enabled and new_accident)).lower()
    )

    components.html(sound_html, height=65)

# ==========================================
# 8. دالة عرض تفاصيل الحوادث
# ==========================================

def show_accident_cards(rows):
    """Display accident cards with clear status and confidence."""

    if rows.empty:
        st.info(
            "لا توجد حوادث مسجلة حاليًا."
            if is_ar
            else "No incidents recorded yet."
        )
        return

    for _, row in rows.iterrows():
        detected = str(row.get("Accident Detected", "No")).strip().lower()
        is_accident = detected in ["yes", "true", "1", "نعم"]

        confidence = str(row.get("Confidence", "N/A"))
        location = str(row.get("Camera Location", "Unknown"))
        time_value = str(row.get("Time", "Unknown"))
        alert_status = str(row.get("Alert Status", "Pending"))

        if is_accident:
            title = "🚨 حادث مروري مكتشف" if is_ar else "🚨 Accident Detected"
            status_color = "#ff4b4b"
            status_text = "يوجد حادث" if is_ar else "Accident Detected"
        else:
            title = "✅ لا يوجد حادث" if is_ar else "✅ No Accident"
            status_color = "#21c55d"
            status_text = "لا يوجد حادث" if is_ar else "No Accident"

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="
                    border-right: 5px solid {status_color};
                    padding: 10px 14px;
                    border-radius: 8px;
                    background-color: rgba(100, 116, 139, 0.10);
                ">
                    <h4 style="margin: 0 0 10px 0;">{title}</h4>
                    <span style="
                        background-color: {status_color};
                        color: white;
                        padding: 4px 10px;
                        border-radius: 15px;
                        font-size: 13px;
                    ">{status_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"**{'📍 الموقع' if is_ar else '📍 Location'}:** {location}"
                )
                st.markdown(
                    f"**{'🕒 الوقت' if is_ar else '🕒 Time'}:** {time_value}"
                )

            with col2:
                st.markdown(
                    f"**{'🎯 نسبة الثقة' if is_ar else '🎯 Confidence'}:** {confidence}"
                )
                st.markdown(
                    f"**{'🔔 حالة التنبيه' if is_ar else '🔔 Alert Status'}:** {alert_status}"
                )

            

# ==========================================
# 9. الصفحة الرئيسية
# ==========================================
if dashboard_page:
    st.title("🚦 " + title)
    st.caption(subtitle)
    st.divider()

    st.subheader(status_title)
    st.success("🟢 " + running)

    st.subheader("📊 " + stats_title)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(total_label, total_records)
    c2.metric(accident_label, accident_count)
    c3.metric(normal_label, no_accident_count)
    c4.metric(pending_label, pending_count)

    st.divider()
    st.subheader("📈 " + stats_title)

    chart_data = pd.DataFrame({
        "Status": [
            "حوادث" if is_ar else "Accidents",
            "بدون حادث" if is_ar else "No Accident"
        ],
        "Count": [accident_count, no_accident_count]
    })

    st.bar_chart(chart_data, x="Status", y="Count")

    st.divider()
    st.subheader(
        "🚨 أحدث الحوادث" if is_ar else "🚨 Recent Accidents"
    )

    # عرض أحدث 3 حوادث فقط في الرئيسية
    if has_accident:
        show_accident_cards(accidents.tail(3).iloc[::-1])
    else:
        st.success(no_accidents)

    st.caption("ℹ️ " + demo_note)

# ==========================================
# 10. صفحة الحوادث والتنبيهات
# ==========================================
elif alerts_page:
    st.title("🚨 " + alerts_title)
    st.caption(
        "متابعة الحوادث المسجلة وحالة التنبيهات"
        if is_ar
        else "Review recorded accidents and alert status"
    )

    st.metric(accident_label, accident_count)

    st.divider()
    show_accident_cards(accidents.iloc[::-1])

    st.divider()
    st.subheader("📋 " + log_title)

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )

    st.caption("ℹ️ " + demo_note)

# ==========================================
# 11. صفحة مراقبة الفيديو
# ==========================================
elif video_page:
    st.title("📹 " + video_title)

    st.info(
        "هذه الصفحة تعرض الفيديو الذي ترفعينه يدويًا. "
        "لم يتم ربطها بالكاميرات أو نموذج الذكاء الاصطناعي بعد."
        if is_ar
        else
        "This page displays manually uploaded videos. "
        "Live cameras and the AI model are not connected yet."
    )

    uploaded_video = st.file_uploader(
        upload_label,
        type=["mp4", "avi", "mov"],
        key="road_video_upload"
    )

    if uploaded_video is not None:
        st.video(uploaded_video)
    else:
        st.info(waiting_video)

# ==========================================
# 12. صفحة خريطة الحوادث
# ==========================================
elif map_page:
    st.title("🗺️ خريطة مواقع الحوادث")

    if not has_accident:
        st.info(
            "لا توجد حوادث مسجلة حاليًا."
            if is_ar
            else "No accidents are currently recorded."
        )

    elif not {"Latitude", "Longitude"}.issubset(data.columns):
        st.warning(
            "أضيفي عمودي Latitude وLongitude إلى alerts.csv."
            if is_ar
            else "Add Latitude and Longitude columns to alerts.csv."
        )

    else:
        locations = accidents.dropna(
            subset=["Latitude", "Longitude"]
        ).copy()

        locations["Latitude"] = pd.to_numeric(
            locations["Latitude"], errors="coerce"
        )
        locations["Longitude"] = pd.to_numeric(
            locations["Longitude"], errors="coerce"
        )

        locations = locations.dropna(
            subset=["Latitude", "Longitude"]
        )

        if locations.empty:
            st.warning(
                "لا توجد إحداثيات صالحة للحوادث."
                if is_ar
                else "No valid accident coordinates are available."
            )
        else:
            first = locations.iloc[0]

            accident_map = folium.Map(
                location=[
                    float(first["Latitude"]),
                    float(first["Longitude"])
                ],
                zoom_start=13
            )

            for _, row in locations.iterrows():
                lat = float(row["Latitude"])
                lon = float(row["Longitude"])

                popup_text = (
                    f"الموقع: {row['Camera Location']}<br>"
                    f"الوقت: {row['Time']}<br>"
                    f"الثقة: {row['Confidence']}"
                )

                folium.Marker(
                    location=[lat, lon],
                    tooltip=str(row["Camera Location"]),
                    popup=popup_text,
                    icon=folium.Icon(
                        color="red",
                        icon="warning-sign"
                    )
                ).add_to(accident_map)

                directions_url = (
                    "https://www.google.com/maps/dir/?api=1"
                    f"&destination={lat},{lon}"
                )

                st.markdown(
                    f"[📍 فتح الاتجاهات إلى {row['Camera Location']}]"
                    f"({directions_url})"
                )

            st_folium(
                accident_map,
                use_container_width=True,
                height=550,
                key="incident_map"
            )

# ==========================================
# 13. تذييل الصفحة
# ==========================================
st.sidebar.caption(
    "نسخة تجريبية | Demo Version"
)
