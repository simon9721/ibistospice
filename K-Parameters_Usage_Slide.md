# How Ku/Kd Tables Are Used in IBIS Simulations

## Implementation in SPICE

### Behavioral Sources with K-Parameter Multiplication

```spice
* Pullup device (voltage-controlled current source)
B3 DIE PULLUP_REF I={V(Ku) * table(V(DIE), -6.0, -0.105, ..., 10.5, 2.34)}

* Pulldown device  
B4 DIE PULLDOWN_REF I={V(Kd) * table(V(DIE), -5.5, -2.37, ..., 11.0, 0.089)}
```

### K-Parameter PWL Voltage Sources

**Yes! The PWL values come directly from the extracted Ku/Kd tables.**

The extraction algorithm (from `solve_k_params_output()`) produces arrays like:

```python
# Rising edge K-parameters (from solving 2×2 system at each time point)
kr = [[time_0, ku_0, kd_0],     # [0.0ns,    1.000, 0.001]
      [time_1, ku_1, kd_1],     # [0.068ns,  0.999, 0.002]
      [time_2, ku_2, kd_2],     # [0.136ns,  0.982, 0.023]
      ...                       # ...
      [time_n, ku_n, kd_n]]     # [5.85ns,   0.001, 1.000]
```

These arrays are then converted to SPICE PWL format:

```spice
* Rising edge Ku waveform (pullup turns ON during rising edge)
* Uses dynamic delay parameter to retrigger on each edge
V20 K_U_RISE 0 PWL({delay_rise}, 0.001, 
                    {delay_rise+0.068ns}, 0.018,
                    {delay_rise+0.136ns}, 0.082, 
                    ..., 
                    {delay_rise+5.85ns}, 0.999)
                    ↑                    ↑
                delay updated by     relative timing
                edge detection       from edge

* Rising edge Kd waveform (pulldown turns OFF during rising edge)  
V40 K_D_RISE 0 PWL({delay_rise}, 0.999,
                    {delay_rise+0.068ns}, 0.982,
                    {delay_rise+0.136ns}, 0.918,
                    ...,
                    {delay_rise+5.85ns}, 0.001)
```

**The Process:**
1. Extract Ku/Kd from IBIS waveforms → numpy arrays `kr[time, ku, kd]`
2. Compress arrays (reduce redundant points) → ~100-200 points
3. Format as PWL strings with delay parameter: `f"{delay_rise+time*1e9}ns {ku_value}"`
4. Write to SPICE subcircuit file

### How Multiple Edges Work: Dynamic Delay Mechanism

**Key Insight:** PWL waveforms use a **delay parameter** that gets updated on each edge, effectively "replaying" the waveform with new timing.

**For regular pulse inputs:**

```
Time:        0ns   10ns   15.85ns   50ns   55.85ns   110ns  115.85ns
Input:       0V    →5V    5V        →0V    0V        →5V    5V
             LOW   RISE   HIGH      FALL   LOW       RISE   HIGH

delay_rise:  -     10ns   10ns      10ns   10ns      110ns  110ns
                   ↑ updated        (frozen)         ↑ updated again

K_U_RISE:    0.001 [Playing 10→15.85ns] ─── 0.999 ─── [Playing 110→115.85ns]
                   0.001→0.999                        0.001→0.999
```

**Mechanism:**
1. **Edge Detection:** Input crosses threshold (e.g., V(IN) crosses 2.5V)
2. **Update Delay:** `delay_rise = current_time` (e.g., delay_rise = 110ns)
3. **PWL Shifts:** Entire waveform timeline shifts to start at new delay
4. **Waveform Plays:** K-parameters transition over next ~6ns
5. **Hold:** After waveform ends, values freeze until next edge
6. **Repeat:** Next edge updates delay again, "replaying" the transition

**This enables:**
- Multiple transitions without redefining waveforms
- Each edge gets the same K-parameter profile
- Works for any input pattern (pulses, random, etc.)
- Natural handling of stuck high/low (waveform just stays at final value)

**Limitation:** If edges come too fast (< ~20ns apart), waveforms overlap and model accuracy degrades - matches real hardware toggle rate limits!

**Example from real generated file:**
```spice
V20 K_U_RISE 0 PWL({delay}, 0.0012496, {delay+6.8182e-11}, -0.0119220, 
    {delay+1.3636e-10}, -0.0430763, ..., {delay+5.85e-09}, 1.0003445)
```
Each `(time, value)` pair is a data point from the extracted Ku/Kd table!

---

## Physical Meaning During Switching

| Time | Ku | Kd | Physical State |
|------|----|----|----------------|
| **Before switching** | 1.0 | 0.0 | Pullup fully ON → Output HIGH (5V) |
| **During rising edge** | 1.0→0.0 | 0.0→1.0 | Pullup weakens, Pulldown strengthens |
| **After switching** | 0.0 | 1.0 | Pulldown fully ON → Output LOW (0V) |

### Example Ku/Kd Values (Rising Edge @ 1ns):

```
Time(ns)    Ku      Kd      V_out(V)    Transition Phase
─────────────────────────────────────────────────────────
  0.00     1.000   0.000      5.0       High State
  0.50     0.880   0.050      4.8       Start weakening
  1.00     0.660   0.460      3.5       Mid-transition  
  1.50     0.330   0.770      1.8       Accelerating
  2.00     0.100   0.950      0.5       Nearly complete
  2.50     0.001   0.999      0.05      Low State
```

---

## Simulation Flow

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

---

## Key Advantages

✓ **Accuracy**: Reproduces measured IBIS waveforms exactly  
✓ **Speed**: Fast table lookups, no transistor-level equations  
✓ **Vendor-neutral**: No proprietary transistor models needed  
✓ **Board-level simulation**: Captures real switching behavior including:
  - Supply voltage effects (via I-V table range)
  - Temperature effects (separate Typical/Min/Max corners)
  - Process variation (Fast-Strong, Typical, Weak-Slow)
  - Load-dependent slew rates (via fixture measurements)

---

## Summary

**K-parameters bridge the gap** between static I-V characterization and dynamic switching behavior:

1. **Extract** Ku(t) and Kd(t) from IBIS V-T waveforms by solving linear equations
2. **Store** as compact PWL (piece-wise linear) waveforms in SPICE netlist
3. **Apply** during simulation by multiplying I-V table currents
4. **Result**: Accurate, efficient behavioral models for signal integrity analysis

This approach enables **fast, accurate signal integrity simulations** at the board level without requiring detailed transistor models.
