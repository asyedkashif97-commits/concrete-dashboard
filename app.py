import os
import joblib
import numpy as np
import xgboost as xgb
import gradio as gr

MODEL_PATH = "concrete_model.pkl"

# =========================================================================
# SIMULATED TELEMETRY FOR CUBES 01 TO 05 ONLY
# =========================================================================
CUBE_DATABASE = {
    "Cube 01": {
        "mix": "M20 Grade",
        "curing_days": 3,
        "base_temp": 42.5,
        "utm_strength": "19.50 MPa",
        "timestamp": "Sept 16, 2026 - 09:00 AM"
    },
    "Cube 02": {
        "mix": "M20 Grade",
        "curing_days": 7,
        "base_temp": 31.2,
        "utm_strength": "29.10 MPa",
        "timestamp": "Sept 12, 2026 - 11:30 AM"
    },
    "Cube 03": {
        "mix": "M25 High Strength",
        "curing_days": 14,
        "base_temp": 24.8,
        "utm_strength": "Pending Test (Day 28)",
        "timestamp": "Sept 05, 2026 - 08:15 AM"
    },
    "Cube 04": {
        "mix": "M30 Special Mix",
        "curing_days": 28,
        "base_temp": 22.1,
        "utm_strength": "42.30 MPa",
        "timestamp": "Aug 22, 2026 - 07:00 AM"
    },
    "Cube 05": {
        "mix": "M20 Grade",
        "curing_days": 1,
        "base_temp": 48.9,
        "utm_strength": "Too Weak to Test",
        "timestamp": "Sept 18, 2026 - 04:30 PM"
    }
}

def update_cube_dashboard(selected_cube):
    """Processes individual cube metadata, calculates maturity, and runs XGBoost."""
    cube_data = CUBE_DATABASE[selected_cube]
    curing_days = cube_data["curing_days"]
    temp = cube_data["base_temp"]
    
    # 1. Nurse-Saul Maturity Estimation
    datum_temp = -10.0
    total_hours = curing_days * 24
    calculated_maturity = (temp - datum_temp) * total_hours
    
    # 2. Safety Check for Machine Learning Model Execution
    if not os.path.exists(MODEL_PATH):
        return (
            cube_data["mix"], cube_data["timestamp"], f"{temp:.1f} °C",
            f"{calculated_maturity:.0f} °C-hours", "Error: Missing model file", 
            "❌ Please place concrete_model.pkl in repository.", cube_data["utm_strength"], "N/A"
        )
    
    # 3. Compute Strength Prediction using pre-trained XGBoost
    model = joblib.load(MODEL_PATH)
    features = np.array([[temp, curing_days]])
    predicted_strength = float(model.predict(features))
    
    # 4. Determine Engineering Advisory Alert Flags
    if predicted_strength < 20.0:
        status = "❌ Status: Critical Low Strength. Do NOT remove structural formwork framing panels!"
    elif predicted_strength < 35.0:
        status = "⚠️ Status: Moderate Curing. Structurally sound for early/minor handling profiles."
    else:
        status = "✅ Status: Targeted Capacity Met. Safe to safely strip forms and apply complete loads."
    
    # 5. Calculate difference between AI and real physical lab UTM values
    real_utm = cube_data["utm_strength"]
    if "MPa" in real_utm:
        real_num = float(real_utm.replace(" MPa", ""))
        error_val = f"{abs(predicted_strength - real_num):.2f} MPa"
    else:
        error_val = "Awaiting lab validation"
        
    return (
        cube_data["mix"], 
        cube_data["timestamp"], 
        f"{temp:.2f} °C",
        f"{calculated_maturity:.0f} °C-hours", 
        f"{predicted_strength:.2f} MPa", 
        status, 
        real_utm,
        error_val
    )

# =========================================================================
# GRADIO INTERACTIVE INTERFACE LAYOUT DESIGN WITH UNIVERSITY BRANDING
# =========================================================================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # 🏛️ University Headers
    gr.Markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #0A3663; margin-bottom: 5px; font-size: 26px; font-weight: bold;">
                MEHRAN UNIVERSITY OF ENGINEERING AND TECHNOLOGY
            </h1>
            <h2 style="color: #4A5568; margin-top: 0px; margin-bottom: 5px; font-size: 18px; font-weight: 500;">
                SZAB CAMPUS KHAIRPUR MIRS
            </h2>
            <h3 style="color: #718096; margin-top: 0px; margin-bottom: 25px; font-size: 15px; font-weight: bold; border-bottom: 2px solid #E2E8F0; padding-bottom: 15px;">
                DEPARTMENT OF CIVIL ENGINEERING
            </h3>
        </div>
        """
    )
    
    gr.Markdown("# 🚧 Multi-Cube Real-Time Concrete Maturity & Strength Tracker")
    gr.Markdown("Select individual structural concrete sample units below to display distinct wireless IoT data profiles.")

    cube_selector = gr.Dropdown(
        choices=list(CUBE_DATABASE.keys()),
        value=list(CUBE_DATABASE.keys())[0],
        label="🔍 Select Concrete Specimen Core to Inspect"
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📋 Specimen Metadata Profile")
            mix_out = gr.Textbox(label="Mix Design Profile Specification")
            time_out = gr.Textbox(label="Casting Commencement Timestamp")
            
            gr.Markdown("### 📡 Live Sensor Parameters")
            temp_out = gr.Textbox(label="Current Internal Concrete Temp")
            maturity_out = gr.Textbox(label="Calculated Maturity Index (Nurse-Saul)")
            
        with gr.Column(scale=1):
            gr.Markdown("### 📊 AI Structural Assessment Metrics")
            strength_out = gr.Textbox(label="XGBoost Predicted Compressive Strength")
            status_out = gr.Textbox(label="Safety Advisory Alert Notification")
            
            gr.Markdown("### 🧪 Lab Validation Matrix")
            utm_out = gr.Textbox(label="Universal Testing Machine (UTM) Physical Crushing Result")
            error_out = gr.Textbox(label="Model Prediction Variance / Margin of Error")

    # Link the data matching loops cleanly (Perfect 8-item array matching)
    cube_selector.change(
        fn=update_cube_dashboard,
        inputs=[cube_selector],
        outputs=[mix_out, time_out, temp_out, maturity_out, strength_out, status_out, utm_out, error_out]
    )
    
    demo.load(
        fn=update_cube_dashboard,
        inputs=[cube_selector],
        outputs=[mix_out, time_out, temp_out, maturity_out, strength_out, status_out, utm_out, error_out]
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
