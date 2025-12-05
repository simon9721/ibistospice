# PowerPoint Slide: How Ku/Kd Tables Are Used in IBIS Simulations

---

## SLIDE 1: How Ku/Kd Tables Are Used in IBIS Simulations

### Left Column: SPICE Implementation

**1. Behavioral Sources (multiply I-V table by K-parameters)**
```spice
B3 DIE PULLUP_REF I={V(Ku) * table(V(DIE), 
   -6.0, -0.105, ..., 10.5, 2.34)}

B4 DIE PULLDOWN_REF I={V(Kd) * table(V(DIE), 
   -5.5, -2.37, ..., 11.0, 0.089)}
```

**2. PWL Voltage Sources (from extracted tables)**
```spice
* Extracted arrays: kr = [[time, ku, kd], ...]
V20 K_U_RISE 0 PWL(0ns 1.000, 0.068ns 0.999, 
                    0.136ns 0.982, ..., 5.85ns 0.001)

V40 K_D_RISE 0 PWL(0ns 0.001, 0.068ns 0.002,
                    0.136ns 0.023, ..., 5.85ns 1.000)
```
→ **Each (time, value) pair comes directly from extracted Ku/Kd arrays**

### Right Column: Simulation Flow

**At each time step t:**
```
1. Read V(Ku) and V(Kd) from PWL sources
2. Measure V(DIE) at output node
3. Lookup I_pullup(V_DIE) from I-V table
4. Lookup I_pulldown(V_DIE) from I-V table
5. Calculate: I = Ku×I_pullup + Kd×I_pulldown + clamps
6. Apply current → solve for new V(DIE)
7. Repeat for next time step
```

**Example Values (Rising Edge @ 1ns):**

| Time | Ku   | Kd   | V_out | State          |
|------|------|------|-------|----------------|
| 0.0  | 1.00 | 0.00 | 5.0V  | High           |
| 0.5  | 0.88 | 0.05 | 4.8V  | Start switch   |
| 1.0  | 0.66 | 0.46 | 3.5V  | Mid-transition |
| 1.5  | 0.33 | 0.77 | 1.8V  | Accelerating   |
| 2.5  | 0.00 | 1.00 | 0.0V  | Low            |

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
