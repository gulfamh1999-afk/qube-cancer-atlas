import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from scipy.optimize import minimize

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

# =====================================================
# 🧬 STEP 1 — LOAD DATA
# =====================================================

print("\n🧬 Loading Data...\n")

ccle = pd.read_csv("ccle_sample_small.csv")
ccle = ccle.rename(columns={"Unnamed: 0": "DepMap_ID"})

gdsc = pd.read_csv("gdsc1_ic50_part1.csv")

gdsc.columns = gdsc.columns.str.strip()
ic50_col = [c for c in gdsc.columns if "IC50" in c.upper()][0]

gdsc_sample = gdsc.head(len(ccle))
y = gdsc_sample[ic50_col].values

y = (y - np.mean(y)) / (np.std(y) + 1e-9)

print("✅ Data Loaded\n")

# =====================================================
# 🧬 STEP 2 — PREPROCESS
# =====================================================

X = ccle.drop(columns=["DepMap_ID"])

scaler = MinMaxScaler(feature_range=(-1, 1))
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=4)
X_pca = pca.fit_transform(X_scaled)

scaler2 = MinMaxScaler(feature_range=(-1, 1))
X_final = scaler2.fit_transform(X_pca)

dataset = [(X_final[i], y[i]) for i in range(len(X_final))]

print("✅ Quantum Dataset Ready\n")

# =====================================================
# ⚛️ QUBE ENGINE
# =====================================================

class QubeEngine:
    def __init__(self, backend=None, shots=512):
        self.backend = backend if backend else AerSimulator()
        self.shots = shots

    def _build_ansatz(self, angles, params):
        n = len(angles)
        qc = QuantumCircuit(n, n)

        for i, theta in enumerate(angles):
            qc.ry(theta, i)
            qc.ry(params[i], i)
            qc.rz(params[i + n], i)

        for i in range(n - 1):
            qc.cx(i, i + 1)

        qc.measure(range(n), range(n))
        return qc

    def evaluate(self, memory, params):
        angles = (np.array(memory) + 1.0) * (np.pi / 2.0)
        qc = self._build_ansatz(angles, params)
        compiled = transpile(qc, self.backend)

        if "ibm" in str(self.backend).lower():
            sampler = Sampler(mode=self.backend)
            job = sampler.run([compiled], shots=self.shots)
            result = job.result()

            data_bin = result[0].data
            counts = (
                data_bin.c.get_counts()
                if hasattr(data_bin, "c")
                else data_bin.meas.get_counts()
            )
        else:
            result = self.backend.run(compiled, shots=self.shots).result()
            counts = result.get_counts()

        total = sum(counts.values())
        exp = 0

        for bitstring, count in counts.items():
            prob = count / total
            z_val = sum([1 if b == '0' else -1 for b in bitstring])
            exp += z_val * prob

        return np.tanh(exp / len(memory))

    def train(self, dataset):
        n = len(dataset[0][0])
        params = np.random.rand(2 * n) * 2 * np.pi

        def loss(p):
            return np.mean([(self.evaluate(x, p) - y) ** 2 for x, y in dataset])

        result = minimize(loss, params, method='COBYLA', options={'maxiter': 100})
        return result.x

# =====================================================
# 🌐 IBM CONNECTION
# =====================================================

def get_ibm_backend():
    import os

    IBM_TOKEN = os.getenv("IBM_TOKEN")

    if IBM_TOKEN is None:
        raise ValueError("❌ IBM_TOKEN not set. Please set it using environment variables.")

    service = QiskitRuntimeService(
        channel="ibm_cloud",
        token=IBM_TOKEN,
        instance="open-instance"
    )

    print("✅ Connected to IBM Quantum")

    backend = service.least_busy(simulator=False)
    print(f"⚛️ Using backend: {backend.name}")

    return backend

# =====================================================
# 🔬 RUN
# =====================================================

print("⚛️ Training...\n")

local_engine = QubeEngine()
params = local_engine.train(dataset)

ibm_backend = get_ibm_backend()
ibm_engine = QubeEngine(backend=ibm_backend, shots=512)

ideal_vals = []
ibm_vals = []
diffs = []

print("\n🔬 Running Comparison...\n")

for i, (x, _) in enumerate(dataset[:10]):
    ideal = local_engine.evaluate(x, params)
    ibm = ibm_engine.evaluate(x, params)

    ideal_vals.append(ideal)
    ibm_vals.append(ibm)
    diffs.append(abs(ideal - ibm))

    print(f"Sample {i+1}")
    print(f"Ideal: {ideal:.4f}")
    print(f"IBM  : {ibm:.4f}")
    print(f"Δ diff: {abs(ideal - ibm):.4f}\n")

# =====================================================
# 📊 STABILITY
# =====================================================

stability = (1 - np.mean(diffs)) * 100
print(f"\n🔥 Stability Score: {stability:.2f}%")

# =====================================================
# 📊 NOISE ANALYSIS (FIXED)
# =====================================================

print("\n📊 Noise Analysis (Efficient)...\n")

# Method 1: Deviation-based noise (PRIMARY)
print("Mean deviation:", np.mean(diffs))
print("Std deviation:", np.std(diffs))

# Method 2: Light re-run (VERY SMALL)
noise_vals = []

for _ in range(2):
    run = [ibm_engine.evaluate(x, params) for x, _ in dataset[:3]]
    noise_vals.append(run)

noise_vals = np.array(noise_vals)
std_dev = np.std(noise_vals, axis=0)

print("Std Dev (3 samples):", std_dev)
print("Mean noise:", np.mean(std_dev))

# =====================================================
# 📊 CORRELATION
# =====================================================

corr = np.corrcoef(ideal_vals, y[:len(ideal_vals)])[0,1]
print(f"\n📈 Correlation (Quantum vs IC50): {corr:.4f}")

# =====================================================
# 📊 PLOTS
# =====================================================

plt.figure()
plt.plot(ideal_vals, marker='o', label="Ideal")
plt.plot(ibm_vals, marker='x', label="IBM")
plt.legend()
plt.title("Quantum vs IBM Output")
plt.show()

plt.figure()
plt.plot(diffs, marker='o')
plt.title("Deviation (Noise Proxy)")
plt.show()
