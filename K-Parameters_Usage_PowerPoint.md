# PowerPoint Slide: How Ku/Kd Tables Are Used in IBIS Simulations

---

## SLIDE 1: How Ku/Kd Tables Are Used in IBIS Simulations

### Left Column: SPICE Implementation

**1. PWL Voltage Sources (from extracted tables)**
```spice
* Extracted arrays: kr = [[time, ku, kd], ...]
* Creates voltage nodes K_U_RISE, K_D_RISE, K_U_FALL, K_D_FALL
V20 K_U_RISE 0 PWL(0ns 0.001, 0.068ns 0.018, 
                    0.136ns 0.082, ..., 5.85ns 0.999)
V21 K_U_FALL 0 PWL(...)
V40 K_D_RISE 0 PWL(0ns 0.999, 0.068ns 0.982,
                    0.136ns 0.918, ..., 5.85ns 0.001)
V41 K_D_FALL 0 PWL(...)
```
→ **Each (time, value) pair comes directly from extracted Ku/Kd arrays**

**2. Dynamic Delay for Multiple Edges**
```spice
* PWL waveforms use delay parameter that updates on each edge
* Edge detection sets delay to current time when threshold crossed
V20 K_U_RISE 0 PWL({delay_rise}, 0.001, 
                    {delay_rise+0.068ns}, 0.018, ...,
                    {delay_rise+5.85ns}, 0.999)
```
→ **Delay parameter "replays" the waveform at each new edge**

**3. Switching Logic (selects rise vs fall waveforms)**
```spice
* Routes correct PWL waveform based on input edge
B1 Ku 0 V={V(IN) > Vth ? V(K_U_RISE) : V(K_U_FALL)}
B2 Kd 0 V={V(IN) > Vth ? V(K_D_RISE) : V(K_D_FALL)}
```
→ **Creates V(Ku) and V(Kd) nodes that behavioral sources use**

**4. Behavioral Sources (multiply I-V table by K-parameters)**
```spice
* I-V pairs from IBIS [Pullup]/[Pulldown] tables
B3 DIE PULLUP_REF I={V(Ku) * table(V(DIE), 
   -6.0, -0.105, ..., 10.5, 2.34)}

B4 DIE PULLDOWN_REF I={V(Kd) * table(V(DIE), 
   -5.5, -2.37, ..., 11.0, 0.089)}
```
→ **V(Ku)/V(Kd) scale the I-V curves dynamically during simulation**

### Right Column: Simulation Flow

**At each time step t:**
```
1. Read PWL waveforms (K_U_RISE, K_D_RISE, etc.)
2. Switching logic selects → V(Ku) and V(Kd)
3. Measure V(DIE) at output node
4. Lookup I_pullup(V_DIE) from I-V table (IBIS [Pullup])
5. Lookup I_pulldown(V_DIE) from I-V table (IBIS [Pulldown])
6. Calculate: I = Ku×I_pullup + Kd×I_pulldown + clamps
7. Apply current → solve for new V(DIE)
8. Repeat for next time step
```

**Example Values (Rising Edge @ 1ns):**

| Time | Ku   | Kd   | V_out | State          |
|------|------|------|-------|----------------|
| 0.0  | 0.00 | 1.00 | 0.0V  | Low            |
| 0.5  | 0.12 | 0.95 | 0.5V  | Start switch   |
| 1.0  | 0.34 | 0.54 | 1.8V  | Mid-transition |
| 1.5  | 0.67 | 0.23 | 3.5V  | Accelerating   |
| 2.5  | 1.00 | 0.00 | 5.0V  | High           |

### Bottom: Key Points
✓ **Accurate** - Reproduces IBIS waveforms exactly  
✓ **Fast** - Table lookups, no transistor equations  
✓ **Vendor-neutral** - No proprietary models needed

---

## DESIGN NOTES:

**Layout:**
- 2-column design: Implementation (left) | Simulation Flow (right)
- Use monospace font for all code blocks
- Highlight multiplication operators (×) in formulas
- Table with alternating row colors

**Visual Elements:**
- Add arrow showing kr array → PWL conversion
- Consider small waveform graph showing Ku/Kd crossing
- Color code: Ku (blue), Kd (red)

**Font sizes:**
- Title: 36pt bold
- Section headers: 24pt bold
- Code: 14pt monospace
- Body text: 18pt
