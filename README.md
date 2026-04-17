# Qube Cancer Atlas 🧬 Hardware Validation 
---

## Overview

This repository presents the **hardware validation pipeline** for quantum encoding of cancer gene expression using the **Qube Engine**.

The system demonstrates that high-dimensional biological data can be transformed into quantum states and executed on real superconducting quantum hardware while preserving structural integrity and exhibiting measurable alignment with drug response (IC50).

---

## How It Works

```
Classical Gene Expression Data  
    ↓
Memory Vector (normalized)  
    ↓
Quantum Encoding (RY rotations)  
    ↓
Variational Circuit (RY + RZ + entanglement)  
    ↓
Measurement (Pauli-Z observable)  
    ↓
Hardware Execution (IBM Quantum)
    ↓
Comparison (Ideal vs Hardware)
```

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```
---

## 🏗️ Architecture

The Qube Engine is a shallow variational quantum kernel designed for **noise-resilient execution on NISQ hardware**.

- Data encoding using rotation gates (RY)  
- Trainable variational layers (RY + RZ)  
- Linear entanglement (nearest-neighbor CNOT chain)  
- Expectation value measurement using Pauli-Z observables  

### Design Principles

- Low circuit depth  
- Hardware-aligned optimization  
- Stability under noise  
- Efficient parameter convergence  

---

## 🔧 Hardware Validation (IBM Quantum)

The system is executed on real superconducting quantum hardware using:

- **Backend:** ibm_fez  
- **Execution Mode:** Qiskit Runtime (Sampler)  
- **Shots:** 512  

This ensures evaluation under realistic noise conditions in the NISQ regime.

---

## Key Results

Based on hardware execution:

- **Stability Score:** ~97.15%  
- **Mean Deviation:** ~0.0285  
- **Noise (Std Dev):** ~0.0207 (~2.07% relative variation) 
- **Quantum–IC50 Correlation:** ~0.45  

These results indicate strong agreement between simulation and hardware outputs, with preserved biological signal.

---

## Performance Insight

- Quantum outputs maintain structural consistency under hardware noise  
- Deviation remains bounded across samples  
- Observable correlation with IC50 suggests biological relevance  

---

##  📊 Data Sources

This work utilizes publicly available cancer genomics and drug response datasets:

- Cancer Cell Line Encyclopedia (CCLE)
- DepMap Portal (Broad Institute)
- Genomics of Drug Sensitivity in Cancer (GDSC, Sanger Institute)
- Cell Model Passports (Sanger Institute)

These datasets provide gene expression profiles and drug response (IC50) measurements used for quantum encoding and validation.

---

## 📄 Associated Publication

If you use or reference this work, please cite:

> Hussain, G. (2026). *Quantum Kernel-Based Cancer Atlas: Hardware-Validated Mapping of Gene Expression to Drug Response*. Zenodo.  
https://doi.org/10.5281/zenodo.19633728

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19633728.svg)](https://doi.org/10.5281/zenodo.19633728)

---

## 📜 License

MIT License — free to use, modify, and build upon. 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software.

Attribution to the original author is appreciated.
