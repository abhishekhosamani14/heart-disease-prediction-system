# create environment for windows
# python -m venv myenv
# activate environment
# myenv\Scripts\activate
# pip install  streamlit pandas numpy seaborn matplotlib scikit-learn reportlab

import streamlit as st
import numpy as np
import sqlite3
import hashlib
import pickle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

# -------- DATABASE --------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS history (
    username TEXT,
    score REAL,
    timestamp TEXT
)
""")

conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

st.set_page_config(
    page_title="Heart Disease Prediction",
    page_icon="❤️",
    layout="centered"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

    # -------- SESSION STATE --------
if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

if "risk_score" not in st.session_state:
    st.session_state.risk_score = None

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

if "history" not in st.session_state:
    st.session_state.history = []

# -------- LOGIN SESSION --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Dummy users (you can change)
users = {
    "admin": "1234",
    "user": "pass"
}

st.markdown("""
<style>

.stApp {
    background:  var(--background-color);
}

.main {
    padding: 2rem;
}

h1 {
    color: var(--text-color);
    text-align: center;
    font-size: 48px;
}

.stButton>button {
    background-color: #ff4b6e;
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 20px;
    font-weight: bold;
    border: none;
}

.info-box {
    padding: 15px;
    border-radius: 12px;
    color: white;
    font-size: 15px;
    background: linear-gradient(135deg, #1f4e79, #2a7faa);
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}

.stButton>button:hover {
    background-color: #e6395c;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# Load trained model and scaler
model = pickle.load(open('model.pkl','rb'))
scaler = pickle.load(open('scaler.pkl','rb'))
features = pickle.load(open('features.pkl','rb'))

# -------- AUTH SYSTEM --------
menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

# -------- SIGNUP --------
if choice == "Signup":
    st.title("📝 Signup")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Create Account"):
        c.execute("SELECT * FROM users WHERE username=?", (new_user,))
        if c.fetchone():
            st.error("User already exists ❌")
        else:
            c.execute("INSERT INTO users VALUES (?,?)",
                      (new_user, hash_password(new_pass)))
            conn.commit()
            st.success("Account created ✅")

    st.stop()

# -------- LOGIN --------
if not st.session_state.logged_in:

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, hash_password(password)))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

    st.stop()

def create_pdf(age, sex, prediction_text, risk_score, recommendations):
    pdf = SimpleDocTemplate("heart_report.pdf", pagesize=letter)

    styles = getSampleStyleSheet()
    content = []

    title = Paragraph("<b>Heart Disease Prediction Report</b>", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 20))
    date_time = datetime.now().strftime("%d-%m-%Y %H:%M")
    date_para = Paragraph(
        f"<b>Generated On:</b> {date_time}",
        styles['BodyText']
        )
    content.append(date_para)
    content.append(Spacer(1, 20))
    
    patient_info = Paragraph(
        f"""
        <b>Patient Details</b><br/>
        Age: {age}<br/>
        Sex: {sex}<br/>
        """,
        styles['BodyText']
    )

    content.append(patient_info)
    content.append(Spacer(1, 20))

    result = Paragraph(
        f"""
        <b>Prediction:</b> {prediction_text}<br/>
        <b>Risk Score:</b> {risk_score:.2f}%
        """,
        styles['BodyText']
    )

    content.append(result)
    content.append(Spacer(1, 20))

    rec_text = "<br/>".join(recommendations)

    rec_para = Paragraph(
        f"""
        <b>Recommendations:</b><br/>
        {rec_text}
        """,
        styles['BodyText']
    )

    content.append(rec_para)

    pdf.build(content)

st.sidebar.write(f"👤 {st.session_state.username}")
st.sidebar.title("ℹ️ About")

st.sidebar.markdown("""
<div class="info-box">
This AI system predicts the likelihood of heart disease using Machine Learning algorithms.

### Features Used:
- Age
- Blood Pressure
- Cholesterol
- ECG Results
- Heart Rate
- Exercise Angina

### Technologies:
- Python
- Streamlit
- Scikit-learn
- XGBoost
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.accuracy-box {
    background: linear-gradient(90deg, #1e7e34, #28a745);
    padding: 15px;
    border-radius: 12px;
    color: white;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="accuracy-box">
    ✅ Model Accuracy: 87%
</div>
""", unsafe_allow_html=True)
st.sidebar.write("") 
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Title
st.markdown("<h1>❤️ Heart Disease Prediction App</h1>", unsafe_allow_html=True)

st.markdown(
    "<center><h4 style='color: var(--text-color);'>AI-powered cardiovascular risk assessment system</h4></center>",
    unsafe_allow_html=True
)

st.write("")


with st.container():
    st.subheader("🩺 Enter Patient Details")


# Input fields
# Inputs
patient_name = st.text_input("Patient Name")
if patient_name:
    if not patient_name.replace(" ", "").isalpha():
        st.error("❌ Name should contain only letters (no numbers or symbols)")
age = st.number_input("Age", 1, 120, 25)
sex_display = st.selectbox("Gender", ["Male", "Female"])
sex = 1 if sex_display == "Male" else 0
cp_display = st.selectbox("Chest Pain Type", [
    "Typical Angina",
    "Atypical Angina",
    "Non-Anginal Pain",
    "Asymptomatic"
])
cp_map = {
    "Typical Angina": "TA",
    "Atypical Angina": "ATA",
    "Non-Anginal Pain": "NAP",
    "Asymptomatic": "ASY"
}

cp = cp_map[cp_display]
resting_bp = st.number_input(
    "Resting Blood Pressure (Normal: 90–120)",
    min_value=80,
    max_value=200,
    value=120,
    step=1
)
chol = st.number_input("Cholesterol", value=200)
fbs = st.selectbox("Fasting Blood Sugar > 120", [0, 1])
restecg_display = st.selectbox("Resting ECG", [
    "Normal",
    "ST-T Wave Abnormality",
    "Left Ventricular Hypertrophy"
])

restecg_map = {
    "Normal": "Normal",
    "ST-T Wave Abnormality": "ST",
    "Left Ventricular Hypertrophy": "LVH"
}

restecg = restecg_map[restecg_display]
ideal_max_hr = 220 - age
max_hr = st.number_input(
    f"Max Heart Rate (Ideal ~ {ideal_max_hr})",
    min_value=60,
    max_value=220,
    value=int(ideal_max_hr),
    step=1
)
exang_display = st.selectbox("Exercise Angina", ["Yes", "No"])
exang = "Y" if exang_display == "Yes" else "N"
oldpeak = st.number_input(
    "Oldpeak (ST Depression)",
    min_value=0.0,
    max_value=6.0,
    value=1.0,
    step=0.1
)
slope = st.selectbox("ST Slope", ["Up", "Flat", "Down"])


# 🔥 ADD THIS BLOCK HERE

sex = 1 if sex == 'M' else 0

cp = {"TA":0, "ATA":1, "NAP":2, "ASY":3}[cp]

restecg = {"Normal":0, "ST":1, "LVH":2}[restecg]

exang = 1 if exang == 'Y' else 0

slope = {"Up":0, "Flat":1, "Down":2}[slope]


# Prediction button
if st.button("Predict"):
    if not patient_name:
        st.warning("⚠️ Please enter patient name")
        st.session_state.prediction_done = False

    elif not patient_name.replace(" ", "").isalpha():
        st.error("❌ Invalid name (only letters allowed)")
        st.session_state.prediction_done = False

    else:
        st.session_state.prediction_done = True   # ✅ only valid case
    st.session_state.prediction_done = True

if st.button("Reset"):
    st.session_state.prediction_done = False
    st.session_state.risk_score = None
    st.session_state.prediction_result = None

if st.button("Clear History"):
    st.session_state.history = []
       
if st.session_state.prediction_done and patient_name and patient_name.replace(" ", "").isalpha():
    # Input dictionary
     input_dict = {
        'Age': age,
        'Sex': sex,
        'ChestPainType': cp,
        'RestingBP': resting_bp,
        'Cholesterol': chol,
        'FastingBS': fbs,
        'RestingECG': restecg,
        'MaxHR': max_hr,
        'ExerciseAngina': exang,
        'Oldpeak': oldpeak,
        'ST_Slope': slope
    }
    # Convert input to array
     input_data = np.array([[input_dict[col] for col in features]])
    # Scale input
     input_data = scaler.transform(input_data)
    # Prediction
     prediction = model.predict(input_data)
    # Probability score
     proba = model.predict_proba(input_data)[0][1]
     from datetime import datetime
     c.execute("INSERT INTO history VALUES (?,?,?)",
          (st.session_state.username, proba * 100, str(datetime.now())))
     conn.commit()
     st.session_state.history.append({
    "name": patient_name,
    "risk": proba * 100,
    "date": datetime.now().strftime("%d-%m-%Y"),
    "time": datetime.now().strftime("%H:%M")
})
     st.session_state.risk_score = proba * 100
     st.session_state.prediction_result = prediction[0]
     st.progress(int(st.session_state.risk_score))
     st.write(f"### Risk Score: {st.session_state.risk_score:.2f}%")
    # Prediction result heading
     st.subheader("🔍 Prediction Result")

    # HIGH RISK
     if st.session_state.prediction_result == 1:

        st.error(f"⚠️ High Risk of Heart Disease ({proba*100:.2f}%)")

        st.markdown("### 💡 Recommendations:")
        st.markdown("""
        - 🏃‍♂️ Exercise regularly (30 mins daily)
        - 🥗 Maintain a healthy diet (low fat, low sugar)
        - 🚭 Avoid smoking and alcohol
        - 🩺 Regular health checkups
        - 😌 Manage stress (yoga/meditation)
        """)

        # PDF recommendations
        recommendations = [
            "Exercise regularly (30 mins daily)",
            "Maintain healthy diet",
            "Avoid smoking and alcohol",
            "Regular health checkups",
            "Manage stress"
        ]

        # Create PDF
        create_pdf(
            age,
            "Male" if sex == 1 else "Female",
            "High Risk of Heart Disease",
            proba * 100,
            recommendations
        )

        # Download PDF button
        with open("heart_report.pdf", "rb") as file:
            st.download_button(
                label="📄 Download Report",
                data=file,
                file_name="heart_report.pdf",
                mime="application/pdf"
            )

    # LOW RISK
     else:

        st.success(f"✅ Low Risk of Heart Disease ({proba*100:.2f}%)")

        st.markdown("### 👍 Keep it up!")
        st.markdown("""
        - 💪 Continue healthy lifestyle
        - 🥗 Eat balanced diet
        - 🏃 Stay physically active
        - 🧘 Maintain mental wellness
        - 🩺 Regular checkups are still important
        """)

        # PDF recommendations
        recommendations = [
            "Continue healthy lifestyle",
            "Eat balanced diet",
            "Stay physically active",
            "Maintain mental wellness",
            "Regular checkups are important"
        ]

        # Create PDF
        create_pdf(
            age,
            "Male" if sex == 1 else "Female",
            "Low Risk of Heart Disease",
            proba * 100,
            recommendations
        )

        # Download PDF button
        with open("heart_report.pdf", "rb") as file:
            st.download_button(
                label="📄 Download Report",
                data=file,
                file_name="heart_report.pdf",
                mime="application/pdf"
            )
            
#st.subheader("📊 Prediction History")

#if st.session_state.history:
    #for i, record in enumerate(st.session_state.history, 1):
        #st.write(
        #f"{i}. 👤 {record['name']} — Risk: {record['risk']:.2f}% — 🕒 {record['time']}"
   # )
#else:
    #st.write("No predictions yet")

st.write("### 📊 Prediction History")
st.dataframe(st.session_state.history)

st.warning("⚠️ This prediction is for educational purposes only and not a medical diagnosis.")