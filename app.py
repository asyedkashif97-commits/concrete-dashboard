import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import gradio as gr

# Load the model from your folder
model_path = "concrete_model.pkl"


def predict_concrete_strength(temperature, curing_days):
    if not os.path.exists(model_path):
        return (
            "Error",
            f"Missing file: Please place '{model_path}' in this folder.",
        )

    model = joblib.load(model_path)
    features = np.array([[temperature, curing_days]])
    predicted_strength = model.predict(features)[0]

    if predicted_strength < 20:
        status = "❌ Status: Weak. Do not remove construction formwork yet!"
    elif predicted_strength < 35:
        status = (
            "⚠️ Status: Curing. Structurally sound for minor construction loads."
        )
    else:
        status = (
            "✅ Status: Full Strength. Perfectly safe for complete structural loading!"
        )

    return f"{predicted_strength:.2f} MPa", status


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚧 Live Concrete Strength Prediction Dashboard")
    gr.Markdown(
        "Move the sliders to simulate sensor input telemetry feeds and monitor concrete structural capability."
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📡 Live Sensor Parameters")
            temp_slider = gr.Slider(
                minimum=10,
                maximum=50,
                value=25,
                step=1,
                label="Internal Temperature (°C)",
            )
            days_slider = gr.Slider(
                minimum=1,
                maximum=28,
                value=7,
                step=1,
                label="Curing Maturity Age (Days)",
            )
            submit_btn = gr.Button(
                "🔄 Calculate Structural Strength", variant="primary"
            )

        with gr.Column():
            gr.Markdown("### 📊 AI Structural Assessment Metrics")
            strength_output = gr.Textbox(label="Predicted Compressive Strength")
            status_output = gr.Textbox(
                label="Safety Advisory Alert Notification"
            )

    submit_btn.click(
        fn=predict_concrete_strength,
        inputs=[temp_slider, days_slider],
        outputs=[strength_output, status_output],
    )

if __name__ == "__main__":
    demo.launch()
