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

```spice
* Rising edge Ku waveform (pullup turns OFF)
V20 K_U_RISE 0 PWL(0ns 1.0, 0.5ns 0.85, 1.0ns 0.65, ..., 5.0ns 0.0)

* Rising edge Kd waveform (pulldown turns ON)  
V40 K_D_RISE 0 PWL(0ns 0.0, 0.5ns 0.15, 1.0ns 0.45, ..., 5.0ns 1.0)

* Falling edge patterns (inverse)
V21 K_U_FALL 0 PWL(...)
V41 K_D_FALL 0 PWL(...)
```

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
