# IBIS to SPICE Conversion - Detailed Walkthrough

## Example: NXP 74HCT1G08 Output Model

This document shows the complete conversion process for a real IBIS model.

---

## 1. IBIS File Information

**Device:** NXP 74HCT1G08 (5V 2-input AND gate)  
**Component:** 74HCT1G08_GW (TSSOP5 package)  
**Model:** HCT1G08_OUTN_50 (Output buffer)

### Key Parameters from IBIS:

| Parameter | Typical | Min | Max | Units |
|-----------|---------|-----|-----|-------|
| **Voltage Range** | 5.0 | 4.5 | 5.5 | V |
| **Temperature** | 35 | -35 | 95 | °C |
| **R_pkg** | 83.53 | 83.41 | 83.66 | mΩ |
| **L_pkg** | 1.484 | 1.480 | 1.486 | nH |
| **C_pkg** | 0.236 | 0.189 | 0.353 | pF |
| **C_comp** | 2.32 | 1.86 | 2.78 | pF |

---

## 2. I-V Table Data

The IBIS file provides current vs voltage tables for each device/clamp:

### Pulldown Device I-V (Sample):
```
Voltage(V)    I_typ(A)      I_min(A)      I_max(A)
-5.5000       -2.3731       -2.2672       -2.6156
-5.0000       -2.1041       -2.0099       -2.3275
-2.5000       -0.6859       -0.6941       -0.6866
 0.0000        0.0000        0.0000        0.0000
 2.5000        0.0769        0.0349        0.1793
 5.0000        0.0824        0.0363        0.1939
```

**Interpretation:**
- **Negative voltage** → Device sources current (pulls toward VCC)
- **Positive voltage** → Device sinks current (pulls toward GND)
- **Zero crossing** → Defines the switching threshold

### Pullup Device I-V (Sample):
```
Voltage(V)    I_typ(A)      I_min(A)      I_max(A)
-5.5000       -0.1054       -0.0406       -0.2832
 0.0000       -0.0929       -0.0359       -0.2607
 2.5000       -0.0759       -0.0292       -0.2112
 5.0000        0.0000        0.0000        0.0000
 7.5000        0.7031        0.3016        1.3026
10.0000        2.0020        0.8597        3.5986
```

**Interpretation:**
- Pullup referenced to VCC (5V)
- Strong current when pin voltage is high (needs to pull down)
- Weak when pin is low (already at desired state)

---

## 3. V-T Waveform Data

IBIS provides voltage vs time measurements under specific test conditions:

### Rising Waveform #1:
- **R_fixture:** 50 Ω (test load resistance)
- **V_fixture:** 0 V (fixture voltage, ground-referenced)
- **Samples:** 100 time points from 0 to 15 ns

```
Time(ns)    V_typ(V)    V_min(V)    V_max(V)
  0.00      0.0000      0.0000      0.0000    ← Low state
  0.27     -0.0687     -0.0158      0.9384    ← Starting to rise
  0.68      0.4014     -0.0480      4.3716    ← Mid-transition
  1.09      1.8948      0.0004      4.4949    ← Approaching high
  2.05      3.0309      0.4022      4.5048    ← Nearly settled
  3.00      3.1150      1.0241      4.5049    ← High state
```

### Rising Waveform #2:
- **R_fixture:** 500 Ω (different load for solving equations)
- Similar structure, different voltage trajectory

**Why two waveforms?** To solve for Ku(t) and Kd(t), we need two equations at each time point!

---

## 4. Solving K-Parameters

### The Mathematical Problem:

At each time instant, all currents must balance (Kirchhoff's Current Law):

```
I_total = Ku(t)·I_pullup + Kd(t)·I_pulldown + I_pwr_clamp + I_gnd_clamp + I_fixture - I_capacitor
```

With two waveform measurements (different fixtures), we get two equations:
```
[I_pu1  I_pd1] [Ku]   [I_total1 - clamps1]
[I_pu2  I_pd2] [Kd] = [I_total2 - clamps2]
```

Solve this 2×2 system at each time point → Ku(t) and Kd(t)

### Results for Rising Edge (Typical corner):

```
Time(ns)    Ku          Kd        State
  0.00     0.001       1.014      ← Pulldown ON (low state)
  0.27    -0.042       0.854      ← Still mostly pulldown
  0.55     0.120       0.464      ← Transition region
  0.82     0.346       0.247      ← Pullup taking over
  1.09     0.662       0.075      ← Mostly pullup
  1.50     0.980       0.016      ← Pullup ON (high state)
  2.00+    1.000       0.000      ← Fully settled high
```

**Physical meaning:**
- **Ku goes 0→1:** Pullup transistor turning ON
- **Kd goes 1→0:** Pulldown transistor turning OFF
- **Overlap during transition:** Brief moment where both conduct (shoot-through)

### Compression Results:
- **Rising:** 100 → 68 samples (32% reduction)
- **Falling:** 173 → 153 samples (12% reduction)
- Removes redundant points where K-values don't change significantly

---

## 5. Generated SPICE Subcircuit Structure

### Complete Circuit Topology:

```
      VCC (5V)
        |
        +-- PULLUP_REF
        |
     [B3: Pullup]  ← Controlled by V(Ku)
        |
        +-- DIE node
        |   |
        |   +-- [C2: C_comp = 2.32pF]
        |   |
        |   +-- [B1: Power Clamp]
        |   |
        |   +-- [B2: Ground Clamp]
        |
     [B4: Pulldown]  ← Controlled by V(Kd)
        |
        +-- PULLDOWN_REF
        |
       GND
        
        DIE --[L1: L_pkg]-- MID --[R1: R_pkg]-- OUT
                                                  |
                                             [C1: C_pkg]
                                                  |
                                                 GND
```

### Behavioral Sources:

**Pullup (B3):**
```spice
B3 DIE PULLUP_REF I = {V(Ku) * table(V(DIE), voltage_points, current_points)}
```
- Current from I-V table
- **Multiplied** by Ku(t) voltage source
- When Ku=1, full pullup current flows
- When Ku=0, no pullup current

**Pulldown (B4):**
```spice
B4 DIE PULLDOWN_REF I = {V(Kd) * table(V(DIE), voltage_points, current_points)}
```
- Similar, but controlled by Kd(t)

### Stimulus Sources (LTSpice):

```spice
V16 K_U_OSC 0 PWL REPEAT FOREVER (0 1, 0.41ns 0, ...) ENDREPEAT
V36 K_D_OSC 0 PWL REPEAT FOREVER (0 0, 0.41ns 1, ...) ENDREPEAT
```

These PWL (piecewise linear) sources recreate the Ku(t) and Kd(t) waveforms.

### Stimulus Selection:

User can select via `stimulus` parameter:
1. **Oscillate** - Continuous square wave at specified freq/duty
2. **Inverted Oscillate** - Opposite phase
3. **Rising Edge** - Single low→high transition with delay
4. **Falling Edge** - Single high→low transition with delay
5. **Stuck High** - Ku=1, Kd=0 (constant)
6. **Stuck Low** - Ku=0, Kd=1 (constant)

Implemented with switches that select which PWL source drives Ku/Kd nodes.

---

## 6. How It Works in Simulation

When you run the SPICE simulation:

1. **Stimulus sources** generate Ku(t) and Kd(t) voltages
2. **Behavioral sources** compute:
   - `I_pullup = Ku * lookup_table(V_pin)`
   - `I_pulldown = Kd * lookup_table(V_pin)`
3. **Package RLC** filters the current/voltage
4. **Die capacitance** slows transitions
5. **Output voltage** results from current balance

### Example Timing:

```
Oscillation at 10 MHz:
  t=0-50ns: Ku=1, Kd=0  → OUT=HIGH (5V)
  t=50-51ns: Rising PWL applied → OUT rises
  t=51-100ns: Ku=0, Kd=1 → OUT=LOW (0V)
  t=100-101ns: Falling PWL applied → OUT falls
  ... repeat
```

The edge speeds match the IBIS waveforms because Ku(t) and Kd(t) were solved to reproduce them!

---

## 7. Accuracy and Limitations

### What This Captures Well:
✓ DC I-V characteristics (output drive strength)  
✓ Edge timing and transition rates  
✓ Load-dependent behavior  
✓ Package and die parasitics  
✓ Process/voltage/temperature corners  

### What This Doesn't Model:
✗ Internal gate logic  
✗ Input-to-output delay (only output edge shape)  
✗ Supply current draw  
✗ Temperature-dependent resistance changes during switching  
✗ Non-ideal effects not captured in IBIS  

### Use Cases:
- **Signal integrity** analysis (reflections, crosstalk, eye diagrams)
- **Board-level** simulations with transmission lines
- **Multi-drop** bus analysis
- **EMI** preliminary studies

---

## 8. Key Takeaways

The conversion works by:

1. **Extracting measured data** from IBIS (I-V tables, waveforms, parasitics)
2. **Solving for switching factors** Ku(t) and Kd(t) using linear algebra
3. **Building behavioral SPICE model** with table lookups and time-varying scaling
4. **No transistor-level modeling** → works across any IC technology
5. **Accurate reproduction** of IBIS measurement conditions

The result is a **compact, fast-simulating** SPICE model that preserves the electrical behavior needed for system-level analysis!

---

**Generated File:** `demo_output.sub` (ready to use in LTSpice)  
**Symbol File:** `demo_output.asy` (auto-created for LTSpice GUI)  
**Test It:** Drop into an LTSpice schematic, add a load, and simulate!
