# Global Minimum Search with Monte Carlo and Tunneling

Este repositorio contiene la implementación de un optimizador estocástico paralelo que combina muestreo Monte Carlo y un mecanismo de tunelamiento para escapar de mínimos locales y converger hacia un mínimo global.

---

## Contenido del repositorio

* `OptimizadorconMPIcorregido.py`
  Implementación principal en Python usando `mpi4py` para paralelizar la evaluación de partículas.
* `README.md`
  Documentación del proyecto, instrucciones de uso y descripción del algoritmo.

---

## Requisitos

* Python 3.7 o superior

* Librerías Python:

  * `numpy`
  * `mpi4py`
  * `pickle` (opcional, para serialización de datos)
  * `time`, `random` (librerías estándar de Python)

* Entorno MPI instalado (por ejemplo, OpenMPI o MPICH).

---

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone <URL-del-repositorio>
   cd Global-minimum-search-method-with-tunneling
   ```
2. Crear y activar un entorno virtual (opcional):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate  # Windows
   ```
3. Instalar dependencias:

   ```bash
   pip install numpy mpi4py
   ```

---

## Descripción del Algoritmo

1. **Muestreo inicial**

   * Se generan `N` partículas con posiciones aleatorias dentro de un dominio $N$-dimensional.
   * Cada partícula evalúa la función objetivo y se ordenan por valor.
   * Se seleccionan las `M` mejores partículas para definir regiones de interés.

2. **Paralelización MPI**

   * El proceso raíz (rank 0) reparte las `M` partículas y los límites de muestreo (`rangite`) a cada proceso usando `MPI_Scatter`.
   * Cada proceso genera `N` nuevas muestras alrededor de su partícula asignada (distribución uniforme o normal).
   * Se recogen los resultados con `MPI_Gather` y la raíz consolida los mejores de cada zona.
   * El dominio de muestreo se reduce multiplicando `rangite *= (1 - zone_size)` y se repite el ciclo.

3. **Túnel de mínimos locales**

   * Tras cada fase de muestreo, si el mejor valor no mejora significativamente, se activa la fase de tunelamiento.
   * Se define una función auxiliar:

     $$
     T(x) = \frac{f(x) - f(x^*)}{\prod_{x_min\in\text{historial}} \|x - x_min\|^{2\eta}},
     $$

     donde $x^*$ es el último mínimo encontrado y $\eta$ controla la agresividad.
   * Se buscan candidatos que reduzcan $T(x)$ por debajo de cero para escapar de la trampa local.

4. **Estructura de clases**

   * `Particle`: almacena posición, valor y zona.
   * `TunnelingOptimizer`: coordina ciclos de búsqueda (`minimize_phase`) y tunelamiento (`tunneling_phase`).

---

## Parámetros de ejecución

| Parámetro   | Descripción                                                           | Valor por defecto |
| ----------- | --------------------------------------------------------------------- | ----------------- |
| `cycles`    | Número total de ciclos de muestreo y tunelamiento                     | 50                |
| `N`         | Número de partículas a generar por ciclo                              | 100               |
| `M`         | Número de partículas seleccionadas y distribuidas entre procesos      | `size` (núcleos)  |
| `distrib`   | Tipo de distribución: `"uniforme"` o `"normal"`                       | "uniforme"        |
| `zone_size` | Fracción del dominio original usada para definir regiones de muestreo | 0.35              |
| `eta`       | Exponente en la función de tunelamiento                               | 2.0               |
| `tol`       | Tolerancia mínima de mejora para considerar un nuevo mínimo           | 1e-6              |

---

## Ejecución

Para ejecutar el optimizador con 8 procesos:

```bash
mpiexec -n 8 python OptimizadorconMPIcorregido.py
```

El script imprimirá el tiempo de ejecución de cada ciclo y el tiempo medio tras completar todas las iteraciones.

---

## Ejemplo de salida

```
Tiempo de ejecusión en el ciclo: 0.28760576248168945
Tiempo de ejecusión en el ciclo: 0.2751939296722412
...  
Tiempo de ejecusión promedio: 0.281 s  
```

---

## Resultados esperados

* Reducción de tiempo de cómputo de aproximadamente 1/8 al paralelizar en 8 núcleos frente a la versión secuencial.
* Escalabilidad lineal al aumentar el número de partículas.

---

## Licencia

Este proyecto está bajo la licencia MIT. Véase `LICENSE` para más detalles.

---

## Agradecimientos

* MPI Forum por la especificación del estándar MPI.
* `mpi4py` por facilitar la integración de MPI con Python.
