import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import gradio as gr

MODEL_PATH = "concrete_model.pkl"

# =========================================================================
# CENTRAL DATABASE FOR MULTIPLE CONCRETE CUBES (SIMULATED TELEMETRY)
# =========================================================================
CUBE_DATABASE = {
    "Cube 01 (Foundation Column A1)": {
        "mix": "M20 Grade",
        "curing_days": 3,
        "base_temp": 42.5,
        "utm_strength": "19.50 MPa",
        "timestamp": "Sept 16, 2026 - 09:00 AM"
    },
    "Cube 02 (Roof Slab Beam B4)": {
        "mix": "M20 Grade",
        "curing_days": 7,
        "base_temp": 31.2,
        "utm_strength": "29.10 MPa",
        "timestamp": "Sept 12, 2026 - 11:30 AM"
    },
    "Cube 03 (Ground Retaining Wall)": {
        "mix": "M25 High Strength",
        "curing_days": 14,
        "base_temp": 24.8,
        "utm_strength": "Pending Test (Day 28)",
        "timestamp": "Sept 05, 2026 - 08:15 AM"
    },
    "Cube 04 (Bridge Pier Base C)": {
        "mix": "M30 Special Mix",
        "curing_days": 28,
        "base_temp": 22.1,
        "utm_strength": "42.30 MPa",
        "timestamp": "Aug 22, 2026 - 07:00 AM"
    },
    "Cube 05 (Lab Control Sample)": {
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
    
    # 1. Nurse-Saul Maturity Estimation: Index = Sum of (Temp - Datum_Temp) * Hours
    # Assuming continuous average curing temperature baseline over tracking lifecycle
    datum_temp = -10.0
       # 5. Build Data Table for Curing Profile Progress Visualization Graph
    time_points = np.linspace(0, total_hours, 20)
    temp_curve = temp + (10 * np.sin(time_points / 12)) + np.random.uniform(-0.5, 0.5, size=20)
    
    graph_df = pd.DataFrame({
        "Hours": time_points,
        "Temperature": temp_curve
    })
    
    # Calculate difference between AI and real physical hydraulic lab machine test values
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
        error_val,
        graph_df
    )

# =========================================================================
# GRADIO INTERACTIVE INTERFACE LAYOUT DESIGN WITH UNIVERSITY BRANDING
# =========================================================================
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # 🏛️ High-Level University and Department Branding Headers
    gr.Markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #0A3663; margin-bottom: 5px; font-size: 28px; font-weight: bold;">
                MEHRAN UNIVERSITY OF ENGINEERING AND TECHNOLOGY
            </h1>
            <h2 style="color: #4A5568; margin-top: 0px; margin-bottom: 5px; font-size: 20px; font-weight: 500;">
                SZAB CAMPUS KHAIRPUR MIRS
            </h2>
            <h3 style="color: #718096; margin-top: 0px; margin-bottom: 25px; font-size: 16px; font-weight: bold; border-bottom: 2px solid #E2E8F0; padding-bottom: 15px;">
                DEPARTMENT OF CIVIL ENGINEERING
            </h3>
        </div>
        """
    )
    
    gr.Markdown("# 🚧 Multi-Cube Real-Time Concrete Maturity & Strength Tracker")
    gr.Markdown("Select individual structural concrete sample units below to display distinct wireless IoT data profiles.")

    # Dropdown Menu to switch between individual concrete samples
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

    gr.Markdown("### 📈 Live Time-Temperature Maturity Curve Trend (15-Minute Sensor Intervals)")
    temp_graph = gr.LinePlot(
        x="Hours",
        y="Temperature",
        x_title="Curing Duration (Hours elapsed)",
        y_title="Internal Telemetry Temperature (°C)",
        title="Concrete Internal Temperature Log Curve",
        width=900,
        height=300
    )

    # Link the selector switch event to update everything on the page dynamically
    cube_selector.change(
        fn=update_cube_dashboard,
        inputs=[cube_selector],
        outputs=[mix_out, time_out, temp_out, maturity_out, strength_out, status_out, utm_out, error_out, temp_graph]
    )
    
    # Trigger initial data load when page boots up
    demo.load(
        fn=update_cube_dashboard,
        inputs=[cube_selector],
        outputs=[mix_out, time_out, temp_out, maturity_out, strength_out, status_out, utm_out, error_out, temp_graph]
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
