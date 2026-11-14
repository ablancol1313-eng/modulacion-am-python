# Actividad Formativa 4: Modulación en amplitud (AM)

Simulación de un sistema AM convencional con portadora (**DSB-LC**) utilizando Python, NumPy, SciPy y Matplotlib. Se comparan condiciones ideales, ruido blanco, atenuación y distorsión por recorte.

## Ejecutar en Visual Studio Code

```powershell
py -m pip install -r requirements.txt
py simulacion_am.py
```

Si `py` no funciona, sustituir por `python`.

## Modelo

- Mensaje: `m(t) = sin(2π · 10 t)`.
- Portadora: `c(t) = cos(2π · 200 t)`.
- Señal AM: `s(t) = [1 + 0.70 m(t)] cos(2π · 200 t)`.
- Muestreo de 4,000 Hz durante un segundo. Índice de modulación: 70 %, sin sobremodulación.
- Espectro ideal: portadora de 200 Hz y bandas laterales de 190 y 210 Hz.
- Escenarios: suma de ruido blanco gaussiano (desviación 0.22), atenuación por factor 0.5, y saturación por recorte a ±0.65.

## Evaluación

El detector por envolvente se implementa con `scipy.signal.hilbert` y un pasa bajos Butterworth. Se estima el mensaje usando una ganancia de referencia fija, **sin compensar automáticamente la atenuación**. Se calcula la raíz del error cuadrático medio (RMSE) en la región central del registro. La columna `Relacion_potencia_ideal_error_dB` de `metricas.csv` mide potencia de señal AM ideal frente a potencia de la diferencia con cada escenario; no debe confundirse con SNR físico del canal para los casos de atenuación y distorsión.

## Resultados

La carpeta `resultados/` contiene cinco imágenes PNG:

1. `01_modulacion_tiempo.png`: mensaje, portadora y AM.
2. `02_modulacion_espectro.png`: portadora y bandas laterales.
3. `03_escenarios_tiempo.png`: cuatro condiciones del canal.
4. `04_escenarios_espectro.png`: comparación espectral.
5. `05_demodulacion_comparacion.png`: envolvente y mensaje recuperado.

También incluye `metricas.csv` con mediciones numéricas.

## Referencias

- https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.hilbert.html
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html
- https://numpy.org/doc/stable/reference/routines.fft.html
