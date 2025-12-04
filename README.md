# IBIS to SPICE Converter

A Python tool for converting IBIS (I/O Buffer Information Specification) models to SPICE subcircuits for circuit simulation.

## Overview

This tool converts IBIS models into SPICE-compatible subcircuits that can be used in various circuit simulators. It supports multiple IBIS model types and provides both GUI and command-line interfaces.

### Supported IBIS Model Types
* Input
* Output
* 3-State
* Open_Drain
* I/O

## Features

* **GUI Application**: User-friendly interface for browsing and converting IBIS files
* **Model Visualization**: View I-V curves and Voltage-Time characteristics
* **Multiple Corners**: Generate models for Weak-Slow, Typical, Fast-Strong, or all corners
* **LTSpice Integration**: Automatic generation of LTSpice-compatible subcircuits and symbols
* **Generic SPICE Support**: Create subcircuits compatible with most SPICE simulators

## Usage

### GUI Application
Run the executable from the `bin` folder or use the Python GUI:

```bash
python gui/pybis2spice-gui.py
```

The GUI allows you to:
1. Browse for an IBIS model file
2. Select the component and model
3. Choose corner conditions (Weak-Slow, Typical, Fast-Strong)
4. Generate SPICE subcircuits
5. View model characteristics

### Command Line
```bash
python demo_conversion.py
```

See `CONVERSION_WALKTHROUGH.md` and `IBIS_TO_SPICE_GUIDE.md` for detailed usage instructions.

## Examples

LTSpice examples demonstrating various use cases are available in the `examples/` folder, including:
* Analog Devices LTC2879 (RS485)
* Nexperia LVC1G07
* NXP HCT1G08
* STMicroelectronics STM32G031
* Texas Instruments SN74LV1T34
* And more...

## References

This tool uses the [ecdtools library](https://ecdtools.readthedocs.io/en/latest/) for parsing IBIS files into Python data structures.

## Credits

This project is based on [pybis2spice](https://github.com/kamratia1/pybis2spice) by Kishan Amratia.

## License

MIT License - See LICENSE file for details.

Original Copyright (c) 2021 Kishan Amratia

