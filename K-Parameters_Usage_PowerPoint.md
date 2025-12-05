# PowerPoint Slides: How Ku/Kd Tables Are Used in IBIS Simulations

---

## SLIDE 1: Implementation in SPICE
**Title Slide**

### Main Content:
**How Ku/Kd Tables Are Used in IBIS Simulations**

Implementation and Simulation Flow

---

## SLIDE 2: Behavioral Sources with K-Parameter Multiplication

### Title: SPICE Behavioral Sources

### Content:

**Pullup Device:**
```
B3 DIE PULLUP_REF I={V(Ku) * table(V(DIE), 
   -6.0, -0.105, -5.5, -0.104, ..., 10.5, 2.34)}
```

**Pulldown Device:**
```
B4 DIE PULLDOWN_REF I={V(Kd) * table(V(DIE), 
   -5.5, -2.37, -5.0, -2.10, ..., 11.0, 0.089)}
```

### Key Points (Bullets):
• Behavioral sources (B-devices) use voltage-controlled current
• `table()` function performs I-V lookup from IBIS data
• `V(Ku)` and `V(Kd)` multiply the table currents
• Real-time scaling during simulation

**Layout Note:** Use monospace font for code, highlight the multiplication operators

---

## SLIDE 3: K-Parameter PWL Voltage Sources

### Title: From Extracted Tables to PWL Waveforms

### Content Box 1 - The Source Data:
**Extraction algorithm produces arrays:**
```
kr = [[time_0, ku_0, kd_0],    # [0.0ns,   1.000, 0.001]
      [time_1, ku_1, kd_1],    # [0.068ns, 0.999, 0.002]
      [time_2, ku_2, kd_2],    # [0.136ns, 0.982, 0.023]
      ...
      [time_n, ku_n, kd_n]]    # [5.85ns,  0.001, 1.000]
```

### Content Box 2 - Conversion to SPICE:
```
V20 K_U_RISE 0 PWL(0ns 1.000, 0.068ns 0.999, 
                    0.136ns 0.982, ..., 5.85ns 0.001)

V40 K_D_RISE 0 PWL(0ns 0.001, 0.068ns 0.002,
                    0.136ns 0.023, ..., 5.85ns 1.000)
```

### Key Takeaway (Bottom):
**✓ Every (time, value) pair in PWL comes directly from extracted Ku/Kd tables!**

**Layout Note:** Use arrows to show kr[time, ku, kd] → PWL mapping

---

## SLIDE 4: The Process Flow

### Title: From Extraction to SPICE

### Process Steps (Numbered):
1. **Extract Ku/Kd** from IBIS waveforms
   → numpy arrays `kr[time, ku, kd]`

2. **Compress arrays** (reduce redundant points)
   → ~100-200 points per waveform

3. **Format as PWL strings**
   → `f"{time*1e9}ns {ku_value}"`

4. **Write to SPICE** subcircuit file
   → Ready for simulation

### Example from Real File:
```
V20 K_U_RISE 0 PWL({delay}, 0.0012496, 
    {delay+6.8182e-11}, -0.0119220,
    {delay+1.3636e-10}, -0.0430763, ...)
```

**Layout Note:** Use flow diagram or numbered boxes with arrows

---

## SLIDE 5: Physical Meaning During Switching

### Title: What Ku and Kd Values Mean

### Table:
| Time (ns) | Ku    | Kd    | V_out (V) | Transition Phase    |
|-----------|-------|-------|-----------|---------------------|
| 0.00      | 1.000 | 0.000 | 5.0       | High State          |
| 0.50      | 0.880 | 0.050 | 4.8       | Start weakening     |
| 1.00      | 0.660 | 0.460 | 3.5       | Mid-transition      |
| 1.50      | 0.330 | 0.770 | 1.8       | Accelerating        |
| 2.00      | 0.100 | 0.950 | 0.5       | Nearly complete     |
| 2.50      | 0.001 | 0.999 | 0.05      | Low State           |

### Key Insight (Bottom Box):
**During rising edge:**
• Ku: 1.0 → 0.0 (Pullup weakens/turns OFF)
• Kd: 0.0 → 1.0 (Pulldown strengthens/turns ON)

**Layout Note:** Consider adding a graph showing Ku and Kd curves vs. time

---

## SLIDE 6: Simulation Flow Diagram

### Title: How SPICE Uses K-Parameters

### Flow Diagram:
```
┌──────────────────┐
│  SPICE Solver    │
│  at time = t     │
└────────┬─────────┘
         │
         ├─→ Read V(Ku) and V(Kd) from PWL sources
         │
         ├─→ Measure V(DIE) at output node
         │
         ├─→ Lookup I_pullup(V_DIE) from table
         ├─→ Lookup I_pulldown(V_DIE) from table
         │
         ├─→ Calculate: I = Ku×I_pullup + Kd×I_pulldown + clamps
         │
         ├─→ Apply current to circuit (Kirchhoff's laws)
         │
         └─→ Solve for new voltage → update V(DIE)
                          ↓
                    Repeat for t+Δt
```

**Layout Note:** Use flowchart shapes with arrows; color-code different operations

---

## SLIDE 7: Complete Circuit Implementation

### Title: All Components Together

### Circuit Elements:

**Package (RLC):**
```
R1 OUT MID {R_pkg}
L1 DIE MID {L_pkg}
C1 OUT 0 {C_pkg}
C2 DIE 0 {C_comp}
```

**Behavioral Sources:**
```
B3 DIE PULLUP_REF I={V(Ku)*table(V(DIE), ...)}
B4 DIE PULLDOWN_REF I={V(Kd)*table(V(DIE), ...)}
```

**K-Parameter Drivers:**
```
V20 K_U_RISE 0 PWL(...)    * Rising edge
V21 K_U_FALL 0 PWL(...)    * Falling edge
V40 K_D_RISE 0 PWL(...)
V41 K_D_FALL 0 PWL(...)
```

**Layout Note:** Consider a simple circuit schematic diagram

---

## SLIDE 8: Key Advantages

### Title: Why K-Parameters Work

### Advantages (with icons/bullets):

✓ **Accuracy**
• Reproduces measured IBIS waveforms exactly

✓ **Speed**
• Fast table lookups, no transistor-level equations

✓ **Vendor-Neutral**
• No proprietary transistor models needed

✓ **Comprehensive Coverage**
• Supply voltage effects (via I-V table range)
• Temperature effects (Typical/Min/Max corners)
• Process variation (Fast-Strong, Weak-Slow)
• Load-dependent slew rates (via fixture measurements)

**Layout Note:** Use large icons for each advantage; 2-column layout

---

## SLIDE 9: Summary

### Title: K-Parameters: The Bridge

### Summary Flow:
```
Static I-V Tables    →    K-Parameters    →    Dynamic Simulation
(From IBIS)          (Time-varying 0-1)   (Accurate waveforms)
```

### The Bridge:
**K-parameters bridge the gap** between static I-V characterization and dynamic switching behavior:

1. **Extract** Ku(t) and Kd(t) from IBIS V-T waveforms
2. **Store** as compact PWL waveforms in SPICE netlist
3. **Apply** during simulation by multiplying I-V table currents
4. **Result** → Accurate, efficient behavioral models

### Bottom Line:
**Fast, accurate signal integrity simulations at board level**
*Without detailed transistor models*

**Layout Note:** Use visual flow arrows; highlight the "bridge" concept

---

## DESIGN NOTES FOR ALL SLIDES:

### Color Scheme Suggestions:
- **Title background:** Dark blue or teal
- **Code blocks:** Light gray background with monospace font
- **Key points:** Use accent color (orange/green) for emphasis
- **Tables:** Alternating row colors for readability

### Font Suggestions:
- **Titles:** Sans-serif, bold, 36-44pt
- **Body text:** Sans-serif, 18-24pt
- **Code:** Monospace (Consolas, Courier New), 14-18pt

### Visual Elements:
- Add company/project logo if applicable
- Use arrows (→) to show flow/transformation
- Include simple circuit diagram on slide 7
- Consider adding waveform graphs on slide 5

### Animations (Optional):
- Slide 6: Animate flow diagram step-by-step
- Slide 4: Build process steps one at a time
- Slide 8: Fly in advantage bullets sequentially

---

## END OF PRESENTATION

Total Slides: 9 (including title)
Estimated Presentation Time: 10-15 minutes
