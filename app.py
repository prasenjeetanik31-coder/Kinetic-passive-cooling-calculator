import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as patches
import matplotlib.transforms as mtransforms

st.set_page_config(
    page_title="Kinetic Passive Cooling — Advanced Actuator Calculator",
    page_icon="🌀",
    layout="wide",
)

# Custom Theme and CSS Injecting
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
    val_str = str(int(round(value))) if fmt == "int" else f"{value:{fmt}}"
    st.markdown(f'<div class="highlight-box"><div class="metric-label">✅ {label}</div><div class="metric-value" style="color:#4caf50">{val_str} <span class="metric-unit">{unit}</span></div></div>', unsafe_allow_html=True)

def warn_metric(label, value, unit, fmt=".2f"):
    val_str = str(int(round(value))) if fmt == "int" else f"{value:{fmt}}"
    st.markdown(f'<div class="warn-box"><div class="metric-label">⚠️ {label}</div><div class="metric-value" style="color:#ff9800">{val_str} <span class="metric-unit">{unit}</span></div></div>', unsafe_allow_html=True)

def eq(text): st.markdown(f'<span class="eq">{text}</span>', unsafe_allow_html=True)
def section(title): st.markdown(f"## {title}")

# =====================================================================
# SIDEBAR CONTROLS
# =====================================================================
with st.sidebar:
    st.markdown("# ⚙️ Advanced Design Controls")
    st.markdown("---")
    
    st.markdown("### 🪵 Louvre Blade Profile")
    H_blade   = st.slider("Blade height (mm)",        300, 1800, 700, 50)
    W_blade   = st.slider("Blade width (mm)",          60, 300,  150,  5)
    T_blade   = st.slider("Blade thickness (mm)",      10,  40,   18,  2)
    rho_blade = st.slider("Timber density (kg/m³)",   400, 900,  720,  10)
    angle_deg = st.slider("Target rotation (°)",       0,  90,   45,  5)
    st.markdown("---")
    
    st.markdown("### 🌡️ Thermal Boundaries")
    T_onset   = st.slider("Wax onset temp (°C)",  20, 35, 25, 1)
    T_full    = st.slider("Full melt temp (°C)",  25, 45, 35, 1)
    T_ambient = st.slider("Ambient design temp (°C)",    25, 45, 35, 1)
    st.markdown("---")
    
    st.markdown("### 🔩 Actuator Mechanicals")
    arm_mm    = st.slider("Bell crank arm length (mm)", 20, 80, 30, 5)
    r_pivot   = st.slider("Pivot pin radius (mm)",       3, 10,  5, 1)
    mu        = st.slider("Bearing friction coeff. μ", 0.05, 0.30, 0.12, 0.01)
    wind_pa   = st.slider("Wind pressure (Pa)",          0, 50, 10, 5)
    SF        = st.slider("Safety factor",             1.5, 5.0, 2.5, 0.5)
    st.markdown("---")
    
    st.markdown("### 🧪 Thermo-Wax Spec")
    wax_expansion = st.slider("Wax expansion β (%)",    10, 20, 15, 1)
    wax_pressure  = st.slider("Wax pressure (MPa)",  0.5, 20.0, 20.0, 0.5)
    wax_density   = st.slider("Wax density (g/mL)",  0.80, 0.95, 0.90, 0.01)
    wax_latent    = st.slider("Latent heat (kJ/kg)", 150, 250, 200, 10)
    st.markdown("---")
    
    st.markdown("### 🏷️ Radial Fin Arrays")
    num_fins  = st.slider("Number of radial fins",    4,  30,  19, 1)
    t_fin_mm  = st.slider("Fin thickness (mm)",      1.0, 5.0, 2.0, 0.5)
    h_fin_mm  = st.slider("Fin height / depth (mm)", 5.0, 25.0, 15.0, 0.5)
    st.markdown("---")
    
    st.markdown("### 🧱 Facade Surface Assembly")
    H_wall    = st.slider("Total Opening Height (mm)", 1000, 5000, 1500, 100)
    W_wall    = st.slider("Total Opening Width (mm)",  600, 4000, 1200, 100)
    overlap   = st.slider("Weather overlap (mm)",    5, 50, 20, 5)

# =====================================================================
# UNIFIED MATHEMATICAL MODEL ENGINE
# =====================================================================
d_bore       = 18.0         
wall_t       = 3.0          
OD           = 24.0         
k_brass      = 115.0        

H = H_blade / 1000          
W = W_blade / 1000          
T = T_blade / 1000          
angle_rad = math.radians(angle_deg)
beta = wax_expansion / 100

V_blade_m3 = H * W * T
mass_blade  = rho_blade * V_blade_m3
area_blade  = H * W

N_bearing   = mass_blade * 9.81
T_friction  = mu * N_bearing * r_pivot 

F_wind      = wind_pa * area_blade
eccentricity_mm = W_blade * 0.10   
T_wind      = F_wind * eccentricity_mm

T_raw       = T_friction + T_wind
T_design    = T_raw * SF
F_piston    = T_design / arm_mm

A_piston_m2 = math.pi / 4 * (d_bore / 1000) ** 2
F_capacity  = wax_pressure * 1e6 * A_piston_m2
force_margin = F_capacity / max(F_piston, 0.001)

s_geom      = arm_mm * math.sin(angle_rad)
s_design    = s_geom

# PISTON ROD CALCULATION
internal_guide = d_bore * 1.2    
external_link  = 15.0            
len_piston_rod = s_design + internal_guide + external_link

V_stroke_mL = A_piston_m2 * (s_design / 1000) * 1e6
V_wax_mL    = V_stroke_mL / beta
h_wax_mm    = (V_wax_mL * 1e-6 / A_piston_m2) * 1000
m_wax_g     = V_wax_mL * wax_density
Q_melt_J    = (m_wax_g / 1000) * (wax_latent * 1000)

len_cylinder = math.ceil(h_wax_mm + internal_guide + s_design + 20)

t_fin_m = t_fin_mm / 1000
h_fin_m = h_fin_mm / 1000
h_finned_zone_m = h_wax_mm / 1000

A_base_unfinned = (math.pi * (OD / 1000) * h_finned_zone_m) - (num_fins * t_fin_m * h_finned_zone_m)
A_fins_surface  = num_fins * (2.0 * h_fin_m * h_finned_zone_m)
A_total_finned  = A_base_unfinned + A_fins_surface

A_plain_cyl = math.pi * (OD / 1000) * h_finned_zone_m
area_multiplier = A_total_finned / max(A_plain_cyl, 0.001)

h_conv_still = 10.0
h_conv_wind  = 25.0
dT           = max(T_ambient - T_onset, 1)

m_fin_param  = math.sqrt((2.0 * h_conv_still) / max(k_brass * t_fin_m, 1e-6))
fin_efficiency = math.tanh(m_fin_param * h_fin_m) / (m_fin_param * h_fin_m) if m_fin_param > 0 else 1.0

A_effective = A_base_unfinned + (fin_efficiency * A_fins_surface)

Q_still      = h_conv_still * A_effective * dT
Q_wind_val   = h_conv_wind  * A_effective * dT

t_onset_s    = (0.15 * Q_melt_J) / max(Q_still, 0.001)
t_full_s     = (0.80 * Q_melt_J) / max(Q_still, 0.001)
t_full_wind  = (0.80 * Q_melt_J) / max(Q_wind_val, 0.001)

# SPATIAL RUN LAYOUT (WITH SMART ROUNDING)
cc_spacing_mm = W_blade - overlap
num_columns_horizontal = math.ceil((W_wall - overlap) / cc_spacing_mm) if cc_spacing_mm > 0 else 1
num_rows_vertical = max(int(round(H_wall / H_blade)), 1) if H_blade > 0 else 1
total_system_louvres = num_columns_horizontal * num_rows_vertical

total_wax_volume_mL = V_wax_mL * total_system_louvres
total_facade_wind_force_N = F_wind * total_system_louvres

# =====================================================================
# FRONTEND INTERFACE GENERATION
# =====================================================================
st.markdown("""# 🌀 Kinetic Passive Cooling System
### Advanced Wax Piston Actuator Simulator & Mechanical Engine
""")
st.markdown("---")

st.markdown("## 📊 Strategic Engineering Dashboard")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: metric("Bore diameter",     d_bore,           "mm",   "int")
with c2: metric("Cylinder OD",       OD,               "mm",   "int")
with c3: metric("Cylinder length",   len_cylinder,     "mm",   "int")
with c4: metric("Piston Rod Length", len_piston_rod,   "mm",   ".1f")
with c5: metric("Effective Area Ratio", area_multiplier, "x Base", ".1f")
with c6: metric("First response",    t_onset_s/60,     "min",  ".1f")

# Tab Initialization (REARRANGED SECTIONS)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🪵 Louvre & Torque Loads", 
    "🔩 Internal Hydraulics", 
    "🧪 Thermal Fins Performance", 
    "🧱 Facade Envelope Architecture", 
    "📐 Dynamic Architectural Drawings", 
    "📋 Manufacturing Specifications Table", 
    "📈 Transient Fluid Response Curves"
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        section("Louvre Physical Specs")
        eq(f"Volume = H × W × T = {H_blade} × {W_blade} × {T_blade} = {V_blade_m3*1e6:.0f} mm³")
        eq(f"Mass = ρ × V = {rho_blade} kg/m³ × {V_blade_m3*1e6:.0f} mm³ = {mass_blade:.3f} kg")
        metric("Individual Blade Mass", mass_blade, "kg")
    with col2:
        section("Aerodynamic Loading & Resistance")
        eq(f"Torque (Design) = (T_friction + T_wind) × SF = {T_design:.1f} N·mm")
        good_metric("Target Actuation Rod Force", F_piston, "N")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        section("Fluid Chamber Mechanics")
        metric("Piston Cross-Section Area", A_piston_m2 * 1e6, "mm²")
        good_metric("Hydrostatic Thrust Capacity", F_capacity, "N", ".1f")
    with col2:
        section("Wall Stress Boundaries")
        metric("Thin-Walled Hoop Stress Limit", 100.0, "MPa")
        good_metric("Calculated Safety Factor Margin", force_margin, "x safety")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        section("Exchanger Surface Multipliers")
        eq(f"Base Area = {A_plain_cyl*1e4:.2f} cm² | Finned Area = {A_total_finned*1e4:.2f} cm²")
        metric("Convective Surface Area Expansion", area_multiplier, "x surface area")
        good_metric("Analytical Fin Core Efficiency (η)", fin_efficiency * 100, "%", ".1f")
    with col2:
        section("Transient Heat Influx Timeline")
        metric("Still Air Complete Cycle", t_full_s / 60, "minutes", ".1f")
        good_metric("Coastal Wind Accelerated Cycle", t_full_wind / 60, "minutes", ".1f")
        st.info(f"💡 **Fin Influx Diagnostic:** Radial distribution fins increase total effective surface heat flux to **{Q_still:.2f} Watts** in still air conditions.")

with tab4:
    section("Envelope Integration Architecture")
    col1, col2 = st.columns(2)
    with col1:
        metric("Horizontal Center-to-Center Pivot Spacing", cc_spacing_mm, "mm", "int")
        metric("Blades per Row (Columns Required)", num_columns_horizontal, "units", "int")
        metric("Vertical Tiers Stacked (Rows Required)", num_rows_vertical, "tiers", "int")
    with col2:
        good_metric("Total Vertical Louvre Blades Needed", total_system_louvres, "pieces", "int")
        metric("Total System Fluid Volume", total_wax_volume_mL, "mL", ".1f")
        warn_metric("Cumulative Wind Load Target on Framing", total_facade_wind_force_N, "Newtons", ".1f")

with tab5:
    st.markdown("## 📐 Live Parametric Plan & Section Projections")
    st.caption("These drawings update vector geometries in real-time as you drag the profile controllers.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗺️ Top-Down Plan View (Horizontal Array Layout)")
        fig_plan, ax_plan = plt.subplots(figsize=(6, 5), facecolor='#0f1117')
        ax_plan.set_facecolor('#1a1d27')
        
        for i in range(3):
            pivot_x = i * cc_spacing_mm
            pivot_y = 0
            
            ts = ax_plan.transData
            tr = mtransforms.Affine2D().rotate_around(pivot_x, pivot_y, angle_rad) + ts
            
            rect = patches.Rectangle(
                (pivot_x - W_blade/2, pivot_y - T_blade/2), 
                W_blade, T_blade, 
                linewidth=1.5, edgecolor='#f0c040', facecolor='#f0c040', alpha=0.35, transform=tr
            )
            ax_plan.add_patch(rect)
            
            ax_plan.plot(pivot_x, pivot_y, 'o', color='#ff9800', markersize=6)
            if i == 0:
                ax_plan.text(pivot_x, pivot_y + T_blade*1.5, "Pivot Pin Track", color='#aaa', fontsize=7, ha='center')
        
        ax_plan.annotate('', xy=(0, -W_blade*0.4), xytext=(cc_spacing_mm, -W_blade*0.4),
                         arrowprops=dict(arrowstyle='<->', edgecolor='#7ecfff'))
        ax_plan.text(cc_spacing_mm/2, -W_blade*0.6, f"C/C Spacing: {cc_spacing_mm:.0f}mm", color='#7ecfff', fontsize=8, ha='center')
        
        ax_plan.set_xlim(-W_blade, cc_spacing_mm * 2.5)
        ax_plan.set_ylim(-W_blade, W_blade)
        ax_plan.set_aspect('equal')
        ax_plan.axis('off')
        st.pyplot(fig_plan)
        plt.close()

    with col2:
        st.markdown("### 🏢 Sectional Cut (Vertical Tier Stacking)")
        fig_sec, ax_sec = plt.subplots(figsize=(6, 5), facecolor='#0f1117')
        ax_sec.set_facecolor('#1a1d27')
        
        wall_box = patches.Rectangle((-50, 0), 100, H_wall, linewidth=2, edgecolor='#333', facecolor='none', linestyle='--')
        ax_sec.add_patch(wall_box)
        
        for r in range(num_rows_vertical):
            base_y = r * H_blade
            
            blade_box = patches.Rectangle((-T_blade/2, base_y), T_blade, H_blade, linewidth=1.5, edgecolor='#4caf50', facecolor='#4caf50', alpha=0.4)
            ax_sec.add_patch(blade_box)
            
            ax_sec.plot(0, base_y + H_blade/2, 'x', color='#ff5722', markersize=5)
            ax_sec.text(T_blade * 1.2, base_y + H_blade/2, f"Tier {r+1}", color='#aaa', fontsize=7, va='center')
            
        ax_sec.set_xlim(-150, 150)
        ax_sec.set_ylim(-100, max(H_wall, H_blade * num_rows_vertical) + 100)
        ax_sec.set_ylabel("Opening Height Axis (mm)", color='#aaa', fontsize=8)
        ax_sec.tick_params(colors='#aaa', labelsize=7)
        ax_sec.grid(True, color='#2e3147', linestyle=':', alpha=0.3)
        ax_sec.set_aspect('equal', adjustable='box')
        st.pyplot(fig_sec)
        plt.close()

with tab6:
    st.markdown("## 📋 Master Manufacturing Specification Datasheet")
    rows = [
        ("Facade Profile", "Horizontal Center-to-Center Spacing", f"{cc_spacing_mm} mm"),
        ("Facade Profile", "Total Facade Component Units Needed", f"{total_system_louvres} pcs"),
        ("Actuator Cylinder", "Internal Core Bore Diameter", f"Ø {d_bore} mm"),
        ("Actuator Cylinder", "Wall Solid Gauge Thickness", f"{wall_t} mm"),
        ("Actuator Cylinder", "Structural Outer Diameter", f"Ø {OD} mm"),
        ("Actuator Cylinder", "Calculated Housing Length", f"{len_cylinder} mm"),
        ("Thermal Fins Array", "Radial Fin Count Engineered", f"{num_fins} elements"),
        ("Thermal Fins Array", "Individual Fin Gauge", f"{t_fin_mm} mm"),
        ("Thermal Fins Array", "Radial Projection Width", f"{h_fin_mm} mm"),
        ("Thermal Fins Array", "Fin Surface Area Multiplier", f"{area_multiplier:.2f} x baseline"),
        ("Piston Linkage", "Kinetic Piston Stroke (Movement)", f"{s_design:.1f} mm"),
        ("Piston Linkage", "Physical Cutting Rod Length", f"{len_piston_rod:.1f} mm"),
        ("Piston Linkage", "Actuator Required Structural Force", f"{F_piston:.2f} N"),
        ("Wax Fuel Matrix", "Volumetric Solid Charge", f"{V_wax_mL:.1f} mL"),
        ("Wax Fuel Matrix", "Total Required Mass Weight", f"{m_wax_g:.2f} grams"),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["System Group", "Engineering Parameter", "Calculated Prototype Value"]), use_container_width=True, hide_index=True)

with tab7:
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0f1117')
        ax.set_facecolor('#1a1d27')
        t_arr = np.linspace(0, max(t_full_s * 1.3, 60), 400)
        
        k_still = 8.0 / max(t_full_s, 1)
        k_wind  = 8.0 / max(t_full_wind, 1)
        stroke_still = s_design / (1 + np.exp(-k_still * (t_arr - t_full_s * 0.5)))
        stroke_wind  = s_design / (1 + np.exp(-k_wind * (t_arr - t_full_wind * 0.5)))
        
        ax.plot(t_arr / 60, stroke_still, color='#f0c040', lw=2.5, label='Still Air (10 W/m²K)')
        ax.plot(t_arr / 60, stroke_wind, color='#4caf50', lw=2.5, linestyle='--', label='Coastal Gale (25 W/m²K)')
        
        ax.set_title("Fin-Accelerated Thermal Stroke Response", color='#f0c040', fontsize=10, fontweight='bold')
        ax.set_xlabel("Elapsed Time (Minutes)", color='#aaa', fontsize=8)
        ax.set_ylabel("Linear Actuator Stroke (mm)", color='#aaa', fontsize=8)
        ax.tick_params(colors='#aaa', labelsize=8)
        ax.grid(True, color='#2e3147', linestyle='--', alpha=0.4)
        ax.legend(facecolor='#1a1d27', edgecolor='#2e3147', labelcolor='#aaa', fontsize=7)
        st.pyplot(fig)
        plt.close()
        
    with col2:
        st.markdown("### 🔩 Actuator Component Spec Vector")
        st.info("ℹ️ **Physical Device Profile:** Cylinder housing maps out to an absolute structural length boundary of **`" + str(len_cylinder) + " mm`** to fully encompass the thermal fluid reservoir chamber charge weight safely.")
