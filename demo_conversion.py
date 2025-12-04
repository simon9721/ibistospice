"""
Demonstration: IBIS to SPICE Conversion Process
Shows step-by-step how the tool converts HCT1G08 output model
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pybis2spice import pybis2spice
from pybis2spice import subcircuit
import numpy as np

print("="*80)
print("IBIS to SPICE Conversion Demonstration")
print("Using: NXP 74HCT1G08 (5V 2-input AND gate)")
print("="*80)

# Step 1: Load IBIS file
print("\n[STEP 1] Loading IBIS file...")
ibis_file = 'test/ibis/hct1g08.ibs'
ibis_model = pybis2spice.get_ibis_model_ecdtools(ibis_file)
print(f"✓ Loaded: {ibis_file}")
print(f"  Components: {ibis_model.component_names}")
print(f"  Models: {ibis_model.model_names}")

# Step 2: Extract data for specific model
print("\n[STEP 2] Extracting data model...")
component_name = '74HCT1G08_GW'
model_name = 'HCT1G08_OUTN_50'
ibis_data = pybis2spice.DataModel(ibis_model, model_name, component_name)

print(f"✓ Model: {model_name}")
print(f"  Type: {ibis_data.model_type}")
print(f"  Voltage Range: {ibis_data.v_range} V [Typ, Min, Max]")
print(f"  Temperature Range: {ibis_data.temp_range} °C")
print(f"  C_comp: {ibis_data.c_comp*1e12} pF")

# Step 3: Show I-V table data
print("\n[STEP 3] I-V Table Data...")
print(f"  Pullup table shape: {np.shape(ibis_data.iv_pullup)}")
print(f"  Pulldown table shape: {np.shape(ibis_data.iv_pulldown)}")
print(f"  Power clamp shape: {np.shape(ibis_data.iv_pwr_clamp)}")
print(f"  Ground clamp shape: {np.shape(ibis_data.iv_gnd_clamp)}")

print("\n  Sample Pulldown I-V (first 5 points):")
print("    Voltage(V)  I_typ(A)    I_min(A)    I_max(A)")
for i in range(5):
    v, i_typ, i_min, i_max = ibis_data.iv_pulldown[i]
    print(f"    {v:10.4f}  {i_typ:10.4f}  {i_min:10.4f}  {i_max:10.4f}")

# Step 4: Show V-T waveform data
print("\n[STEP 4] V-T Waveform Data...")
print(f"  Rising waveforms: {len(ibis_data.vt_rising)}")
print(f"  Falling waveforms: {len(ibis_data.vt_falling)}")

if ibis_data.vt_rising:
    wf = ibis_data.vt_rising[0]
    print(f"\n  Rising Waveform #1:")
    print(f"    R_fixture: {wf.r_fix} Ω")
    print(f"    V_fixture: {wf.v_fix} V [Typ, Min, Max]")
    print(f"    Samples: {np.shape(wf.data)[0]}")
    print(f"    Time range: {wf.data[0, 0]*1e9:.2f} ns to {wf.data[-1, 0]*1e9:.2f} ns")
    
    print("\n    Sample points (first 5):")
    print("      Time(ns)    V_typ(V)    V_min(V)    V_max(V)")
    for i in range(5):
        t, v_typ, v_min, v_max = wf.data[i]
        print(f"      {t*1e9:8.4f}    {v_typ:8.4f}    {v_min:8.4f}    {v_max:8.4f}")

# Step 5: Solve K-parameters
print("\n[STEP 5] Solving K-parameters for Typical corner...")
corner = 1  # 1=Typical, 2=Min, 3=Max
kr = pybis2spice.solve_k_params_output(ibis_data, corner=corner, waveform_type="Rising")
kf = pybis2spice.solve_k_params_output(ibis_data, corner=corner, waveform_type="Falling")

print(f"✓ Rising K-parameters calculated: {np.shape(kr)[0]} time points")
print(f"✓ Falling K-parameters calculated: {np.shape(kf)[0]} time points")

print("\n  Rising K-parameters (first 10 points):")
print("    Time(ns)     Ku          Kd")
for i in range(0, min(10, len(kr)), 2):
    t, ku, kd = kr[i]
    print(f"    {t*1e9:8.4f}    {ku:8.5f}    {kd:8.5f}")

print("\n  Physical meaning:")
print("    Ku = 1.0, Kd = 0.0  → Pullup fully ON, Pulldown OFF (high state)")
print("    Ku = 0.0, Kd = 1.0  → Pullup OFF, Pulldown fully ON (low state)")
print("    Ku & Kd transition  → Output switching between states")

# Step 6: Compress K-parameters
print("\n[STEP 6] Compressing K-parameters...")
kr_orig_size = np.shape(kr)[0]
kf_orig_size = np.shape(kf)[0]

kr_comp = pybis2spice.compress_param(kr, threshold=1e-6)
kf_comp = pybis2spice.compress_param(kf, threshold=1e-6)

print(f"  Rising: {kr_orig_size} → {np.shape(kr_comp)[0]} samples "
      f"({100*(1-np.shape(kr_comp)[0]/kr_orig_size):.1f}% reduction)")
print(f"  Falling: {kf_orig_size} → {np.shape(kf_comp)[0]} samples "
      f"({100*(1-np.shape(kf_comp)[0]/kf_orig_size):.1f}% reduction)")

# Step 7: Generate SPICE subcircuit
print("\n[STEP 7] Generating SPICE subcircuit...")
output_file = 'demo_output.sub'
result = subcircuit.generate_spice_model(
    io_type="Output",
    subcircuit_type="LTSpice",
    ibis_data=ibis_data,
    corner="Typical",
    output_filepath=output_file
)

if result == 0:
    print(f"✓ SPICE subcircuit created: {output_file}")
    
    # Show first 50 lines of generated file
    print("\n  Preview of generated SPICE file (first 50 lines):")
    print("  " + "-"*76)
    with open(output_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 50:
                print("  ... (file continues)")
                break
            print(f"  {line}", end='')
    print("  " + "-"*76)
else:
    print("✗ Failed to create SPICE subcircuit")

# Step 8: Summary
print("\n[STEP 8] Conversion Summary")
print("="*80)
print("The tool has:")
print("  1. Parsed IBIS file and extracted I-V tables and V-T waveforms")
print("  2. Solved for time-varying switching parameters Ku(t) and Kd(t)")
print("  3. Compressed the waveforms to reduce file size")
print("  4. Generated a SPICE subcircuit with:")
print("     - Package RLC network (R_pkg, L_pkg, C_pkg)")
print("     - Die capacitance (C_comp)")
print("     - Behavioral current sources using table() lookups")
print("     - PWL voltage sources for Ku(t) and Kd(t)")
print("     - Device currents multiplied by switching factors")
print("\n  The resulting .sub file can be used in LTSpice or other simulators")
print("  to model the I/O pin's electrical behavior accurately!")
print("="*80)
