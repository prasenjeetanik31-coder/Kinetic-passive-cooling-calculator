import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(
    page_title="Kinetic Passive Cooling — Actuator Calculator",
    page_icon="🌀",
    layout="wide",
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1 { color: #f0c040; font-size: 1.6rem; font-weight: 700; }
    h2 { color: #f0c040; font-size: 1.1rem; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 4px; }
    h3 { color: #aaaaaa; font-size: 0.95rem; font-weight: 500; }
    .metric-box { background: #1a1d27; border: 1px solid #2e3147; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
    .metric-label { color: #888; font-size: 0.78rem; margin-bottom: 2px; }
    .metric-value { color: #f0c040; font-size: 1.4rem; font-weight: 700; }
    .metric-unit  { color: #aaa; font-size: 0.78rem; }
    .highlight-box { background: #1a2a1a; border: 1px solid #2d5a2d; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
    .warn-box { background: #2a1a0a; border: 1px solid #5a3a0a; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
    .info-box { background: #0a1a2a; border: 1px solid #1a4a6a; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
    .eq { font-family: monospace; font-size: 0.85rem; color: #7ecfff; background: #101520; padding: 8px 12px; border-radius: 6px; margin: 4px 0 10px; display: block; }
    .stSlider > div > div > div { background: #f0c040 !important; }
</style>
""", unsafe_allow_html=True)

def metric(label, value, unit, fmt=".2f"):
    val_str = str(int(round(value))) if fmt == "int" else f"{value:{fmt}}"
    st.markdown(f'<div class="metric-box"><div class="metric-label">{label}</div><div class="metric-value">{val_str} <span class="metric-unit">{unit}</span></div></div>', unsafe_allow_html=True)

def good_metric(label, value, unit, fmt=".2f"):
    val_str = f"{value:{fmt}}"
    st.markdown(f'<div class="highlight-box"><div class="metric-label">✅ {label}</div><div class="metric-value" style="color:#4caf50">{val_str} <span class="metric-unit">{unit}</span></div></div>', unsafe_allow_html=True)

def warn_metric(label, value, unit, fmt=".2f"):
    val_str = f"{value:{fmt}}"
    st.markdown(f'<div class="warn-box"><div class="metric-label">⚠️ {label}</div><div class="metric-value" style="color:#ff9800">{val_str} <span class="metric-unit">{unit}</span></div></div>', unsafe_allow_html=True)

def eq(text): st.markdown(f'<span class="eq">{text}</span>', unsafe_allow_html=True)
def section(title): st.markdown(f"## {title}")

with st.sidebar:
    st.markdown("# ⚙️ Design Parameters")
    st.markdown("---")
    st.markdown("### 🪵 Louvre Blade")
    H_blade   = st.slider("Blade height (mm)",        300, 1800, 600, 50)
    W_blade   = st.slider("Blade width (mm)",          60, 300,  100,  5)
    T_blade   = st.slider("Blade thickness (mm)",      10,  40,   18,  2)
    rho_blade = st.slider("Timber density (kg/m³)",   400, 900,  720,  10)
    angle_deg = st.slider("Target rotation (°)",       20,  90,   45,  5)
    st.markdown("---")
    st.markdown("### 🌡️ Thermal Trigger")
    T_onset   = st.slider("Wax onset temperature (°C)",  20, 35, 25, 1)
    T_full    = st.slider("Full melt temperature (°C)",  25, 45, 35, 1)
    T_ambient = st.slider("Ambient design temp (°C)",    25, 45, 35, 1)
    st.markdown("---")
    st.markdown("### 🔩 Mechanism")
    arm_mm    = st.slider("Bell crank arm length (mm)", 20, 80, 30, 5)
    r_pivot   = st.slider("Pivot pin radius (mm)",       3, 10,  5, 1)
    mu        = st.slider("Bearing friction coeff. μ", 0.05, 0.30, 0.12, 0.01)
    wind_pa   = st.slider("Wind pressure (Pa)",          0, 50, 10, 5)
    SF        = st.slider("Safety factor",             1.5, 5.0, 2.5, 0.5)
    st.markdown("---")
    st.markdown("### 🧪 Wax Properties")
    wax_expansion = st.slider("Wax expansion β (%)",    10, 20, 15, 1)
    wax_pressure  = st.slider("Wax pressure (MPa)",  0.5, 20.0, 20.0, 0.5)
    wax_density   = st.slider("Wax density (g/mL)",  0.80, 0.95, 0.90, 0.01)
    wax_latent    = st.slider("Latent heat (kJ/kg)", 150, 250, 200, 10)
    st.markdown("---")
    st.markdown("### 🏗️ Cylinder")
    wall_t = st.slider("Wall thickness (mm)", 1, 10, 2, 1)

H = H_blade / 1000
W = W_blade / 1000
T = T_blade / 1000
arm = arm_mm / 1000
r_piv = r_pivot / 1000
angle_rad = math.radians(angle_deg)
beta = wax_expansion / 100

V_blade_m3 = H * W * T
mass_blade  = rho_blade * V_blade_m3
area_blade  = H * W

N_bearing   = mass_blade * 9.81
T_friction  = mu * N_bearing * r_piv * 1000
F_wind      = wind_pa * area_blade
T_wind      = F_wind * (W_blade / 4)
T_raw       = T_friction + T_wind
T_design    = T_raw * SF
F_piston    = T_design / arm_mm

A_min_m2    = F_piston / (wax_pressure * 1e6)
d_min_mm    = math.sqrt(4 * A_min_m2 / math.pi) * 1000
d_bore      = 12.0

A_piston_m2 = math.pi / 4 * (d_bore / 1000) ** 2
F_capacity  = wax_pressure * 1e6 * A_piston_m2
force_margin = F_capacity / max(F_piston, 0.001)

t_wall_min  = (wax_pressure * 1e6 * (d_bore / 2 / 1000)) / (100e6)
OD          = d_bore + 2 * wall_t

s_geom      = arm_mm * math.sin(angle_rad)
s_design    = s_geom
V_stroke_mL = A_piston_m2 * (s_design / 1000) * 1e6
V_wax_mL    = V_stroke_mL / beta
h_wax_mm    = (V_wax_mL * 1e-6 / A_piston_m2) * 1000
h_wax_design = h_wax_mm
m_wax_g     = V_wax_mL * wax_density
Q_melt_J    = (m_wax_g / 1000) * (wax_latent * 1000)

len_cylinder = math.ceil(h_wax_design + (d_bore * 1.2) + s_design + 20)

h_conv_still = 10.0
h_conv_wind = 25.0
dT          = max(T_ambient - T_onset, 1)
A_plain_cyl = math.pi * (OD / 1000) * (h_wax_design / 1000)
Q_still     = h_conv_still * A_plain_cyl * dT
Q_wind_val  = h_conv_wind  * A_plain_cyl * dT
t_onset_s   = (0.15 * Q_melt_J) / max(Q_still, 0.001)
t_full_s    = (0.80 * Q_melt_J) / max(Q_still, 0.001)
t_full_wind = (0.80 * Q_melt_J) / max(Q_wind_val, 0.001)

st.markdown("""# 🌀 Kinetic Passive Cooling System
### Wax Piston Actuator — Engineering Calculator
""")
st.markdown("---")
st.markdown("## 📊 Key Results at a Glance")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: metric("Bore diameter",     d_bore,          "mm",  "int")
with c2: metric("Cylinder OD",       OD,              "mm",  "int")
with c3: metric("Cylinder length",   len_cylinder,    "mm",  "int")
with c4: metric("Piston stroke",     s_design,        "mm",  ".1f")
with c5: metric("Wax charge",        V_wax_mL,        "mL",  ".1f")
with c6: metric("First movement",    t_onset_s/60,    "min", ".1f")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🪵 Louvre & Torque", "🔩 Piston & Cylinder", "🧪 Wax & Stroke", "📐 Full Spec Table", "📈 Response Charts"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        section("Louvre Blade")
        eq(f"V = H × W × T = {H_blade} × {W_blade} × {T_blade} = {V_blade_m3*1e6:.0f} mm³")
        eq(f"m = ρ × V = {rho_blade} × {V_blade_m3*1e6:.0f}×10⁻⁶ = {mass_blade:.3f} kg")
        metric("Blade mass",  mass_blade,     "kg")
    with col2:
        section("Torque Analysis")
        eq(f"T_design = (T_friction + T_wind) × SF = {T_design:.2f} N·mm")
        good_metric("Required piston force", F_piston, "N")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        section("Piston Sizing")
        good_metric("Force capacity",   F_capacity,   "N",  ".1f")
    with col2:
        section("Cylinder Safety")
        metric("Cylinder OD", OD, "mm", "int")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        section("Stroke Geometry")
        eq(f"s = {s_geom:.2f} mm")
    with col2:
        section("Energy Profile")
        eq(f"Q_melt = {Q_melt_J/1000:.2f} kJ")

with tab4:
    st.markdown("## 📐 Complete Actuator Specification")
    rows = [
        ("Cylinder", "Bore (inner diameter)", f"Ø {d_bore} mm"),
        ("Cylinder", "Wall thickness", f"{wall_t} mm"),
        ("Cylinder", "Outer diameter (OD)", f"Ø {OD} mm"),
        ("Cylinder", "Total length", f"{len_cylinder} mm"),
        ("Piston", "Design stroke", f"{s_design:.1f} mm"),
        ("Wax Core", "Onset temperature", f"{T_onset}°C"),
        ("Wax Core", "Full melt temperature", f"{T_full}°C"),
        ("Wax Core", "Wax volume", f"{V_wax_mL:.1f} mL"),
        ("Wax Core", "Wax mass", f"{m_wax_g:.2f} g"),
        ("Performance", "Required force", f"{F_piston:.2f} N"),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Component", "Parameter", "Value"]), use_container_width=True, hide_index=True)

with tab5:
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0f1117')
        ax.set_facecolor('#1a1d27')
        t_arr = np.linspace(0, max(t_full_s * 1.3, 60), 400)
        k_val = 8 / max(t_full_s, 1)
        stroke_still = s_design / (1 + np.exp(-k_val * (t_arr - t_full_s * 0.5)))
        ax.plot(t_arr / 60, stroke_still, color='#f0c040', lw=2.5, label='Still air profile')
        ax.tick_params(colors='#aaa')
        st.pyplot(fig)
        plt.close()
    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 4), facecolor='#0f1117')
        ax2.set_facecolor('#1a1d27')
        strokes_plot = np.linspace(0, s_geom, 200)
        angles_plot = np.degrees(np.arcsin(strokes_plot / arm_mm))
        ax2.plot(strokes_plot, angles_plot, color='#f0c040', lw=2.5)
        ax2.tick_params(colors='#aaa')
        st.pyplot(fig2)
        plt.close()
