"""Actividad 4: modulación AM convencional con portadora (DSB-LC).

Ejecutar: python simulacion_am.py
Genera cinco figuras y un archivo de métricas CSV en resultados/.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, sosfiltfilt

FS = 4000                    # Frecuencia de muestreo (Hz)
DURACION = 1.0              # segundos
FM = 10                     # Frecuencia del mensaje (Hz)
FC = 200                    # Frecuencia portadora (Hz)
MU = 0.70                   # Índice de modulación, 0 < MU < 1
AMPLITUD_PORTADORA = 1.0
SEMILLA = 2026
t = np.arange(int(FS * DURACION)) / FS
N = len(t)
RUTA = Path(__file__).resolve().parent / "resultados"
RUTA.mkdir(parents=True, exist_ok=True)

# Señal informativa de baja frecuencia y portadora de alta frecuencia.
mensaje = np.sin(2 * np.pi * FM * t)
portadora = AMPLITUD_PORTADORA * np.cos(2 * np.pi * FC * t)

# AM convencional con portadora: s(t)=Ac·[1+mu·m(t)]·cos(2πfc·t).
# Su producto desarrolla una portadora en fc y dos bandas laterales fc±fm.
am_ideal = AMPLITUD_PORTADORA * (1 + MU * mensaje) * np.cos(2 * np.pi * FC * t)
envolvente_ideal = AMPLITUD_PORTADORA * (1 + MU * mensaje)

# Tres efectos de un canal, aplicados por separado a la misma AM ideal.
ruido = 0.22 * np.random.default_rng(SEMILLA).standard_normal(N)
escenarios = {
    "Ideal": am_ideal,
    "Ruido": am_ideal + ruido,
    "Atenuación": 0.50 * am_ideal,
    "Distorsión": np.clip(am_ideal, -0.65, 0.65),
}

def espectro(x):
    """Espectro unilateral de amplitud (muestreo coherente de tonos)."""
    f = np.fft.rfftfreq(len(x), d=1/FS)
    amp = 2 * np.abs(np.fft.rfft(x)) / len(x)
    amp[0] /= 2
    amp[-1] /= 2
    return f, amp

def demodular(x):
    """Detector de envolvente Hilbert y estimación de mensaje sin AGC.

    El filtro elimina ondulaciones de alta frecuencia. En atenuación, el
    nivel de amplitud NO se corrige, para mostrar el impacto del canal.
    """
    envolvente = np.abs(hilbert(x))
    sos = butter(5, 60, btype="lowpass", fs=FS, output="sos")
    envolvente_lisa = sosfiltfilt(sos, envolvente)
    mensaje_estimado = (envolvente_lisa / AMPLITUD_PORTADORA - 1) / MU
    return envolvente_lisa, mensaje_estimado

def guardar(fig, nombre):
    fig.savefig(RUTA / nombre, dpi=165, bbox_inches="tight")
    plt.close(fig)

# Figura 1: componentes y AM ideal en tiempo.
fig, ax = plt.subplots(3, 1, figsize=(10, 8), layout="constrained")
ax[0].plot(t, mensaje, color="#2871a6"); ax[0].set(title="Mensaje de 10 Hz", ylabel="Amplitud")
ax[1].plot(t, portadora, color="#bd6b2b"); ax[1].set(title="Portadora de 200 Hz", ylabel="Amplitud")
ax[2].plot(t, am_ideal, color="#355c7d", lw=.8, label="AM ideal")
ax[2].plot(t, envolvente_ideal, "r--", lw=1.2, label="Envolvente")
ax[2].plot(t, -envolvente_ideal, "r--", lw=1.2)
ax[2].legend(loc="upper right", fontsize=8)
ax[2].set(title="Modulación AM (70 %)", ylabel="Amplitud", xlabel="Tiempo (s)")
for a in ax: a.set_xlim(0, .25); a.grid(alpha=.2)
guardar(fig, "01_modulacion_tiempo.png")

# Figura 2: picos en la portadora y bandas laterales.
fig, ax = plt.subplots(figsize=(10, 4.5), layout="constrained")
freq, amplitud = espectro(am_ideal)
ax.plot(freq, amplitud, color="#226aa3")
for f0, rotulo in [(FC-FM, "190 Hz: banda lateral"), (FC, "200 Hz: portadora"), (FC+FM, "210 Hz: banda lateral")]:
    ax.axvline(f0, color="#ce6a30", ls="--", alpha=.6)
    ax.text(f0, .8 if f0 == FC else .28, rotulo, rotation=90, va="bottom", ha="right", fontsize=8)
ax.set(xlim=(160, 240), xlabel="Frecuencia (Hz)", ylabel="Amplitud", title="Espectro de la señal AM ideal")
ax.grid(alpha=.25)
guardar(fig, "02_modulacion_espectro.png")

# Figura 3: cómo cambia la señal en los distintos escenarios.
fig, axs = plt.subplots(4, 1, figsize=(10, 9), layout="constrained")
for ax, (nombre, x) in zip(axs, escenarios.items()):
    ax.plot(t, x, color="#226aa3", lw=.85)
    ax.set(xlim=(.02, .22), title=nombre, ylabel="Amplitud")
    ax.grid(alpha=.2)
axs[-1].set_xlabel("Tiempo (s)")
guardar(fig, "03_escenarios_tiempo.png")

# Figura 4: espectro comparado (ruido de banda ancha y armónicos del recorte).
fig, axs = plt.subplots(3, 1, figsize=(10, 9), layout="constrained")
for ax, nombre in zip(axs, ["Ruido", "Atenuación", "Distorsión"]):
    for tag, x in [("Ideal", am_ideal), (nombre, escenarios[nombre])]:
        f, a = espectro(x)
        ax.plot(f, a, label=tag, lw=1)
    ax.set(xlim=(0, 700), title=f"Espectro: ideal frente a {nombre.lower()}", xlabel="Frecuencia (Hz)", ylabel="Amplitud")
    ax.legend(); ax.grid(alpha=.2)
guardar(fig, "04_escenarios_espectro.png")

# Figura 5: comparación de envolventes y recuperación del mensaje.
fig, axs = plt.subplots(2, 1, figsize=(10, 7), layout="constrained")
axs[0].plot(t, envolvente_ideal, "k--", label="Envolvente ideal", lw=1.5)
axs[1].plot(t, mensaje, "k--", label="Mensaje original", lw=1.5)
resumen = []
for nombre, x in escenarios.items():
    env, recuperado = demodular(x)
    axs[0].plot(t, env, lw=1.1, label=nombre)
    axs[1].plot(t, recuperado, lw=1.1, label=nombre)
    # Excluir bordes por los transitorios de filtrado; métricas frente al mensaje original.
    tramo = slice(int(.1 * FS), int(.9 * FS))
    rmse = float(np.sqrt(np.mean((recuperado[tramo] - mensaje[tramo]) ** 2)))
    energia = float(np.mean(am_ideal ** 2))
    error_rf = float(np.mean((x - am_ideal) ** 2))
    snr_rel = 10 * np.log10(energia / max(error_rf, 1e-15))
    resumen.append({"Escenario": nombre, "RMSE_mensaje_sin_AGC": f"{rmse:.4f}", "Relacion_potencia_ideal_error_dB": f"{snr_rel:.2f}"})
for ax in axs:
    ax.set_xlim(.1, .4); ax.grid(alpha=.2); ax.legend(ncol=3, fontsize=8)
axs[0].set(title="Envolvente detectada", ylabel="Amplitud de envolvente")
axs[1].set(title="Mensaje recuperado (sin control automático de ganancia)", xlabel="Tiempo (s)", ylabel="Amplitud normalizada")
guardar(fig, "05_demodulacion_comparacion.png")

with (RUTA / "metricas.csv").open("w", newline="", encoding="utf-8") as ar:
    writer = csv.DictWriter(ar, fieldnames=list(resumen[0]))
    writer.writeheader(); writer.writerows(resumen)

print("Simulación AM terminada. Resultados:")
for row in resumen:
    print(row)
print("Figuras y métricas:", RUTA)
