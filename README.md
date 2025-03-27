# Global-minimum-search-method-with-tunneling
The algorithm searches for the global minimum by combining Monte Carlo techniques and tunneling. N random particles are launched, the M best are selected, and the sampling area is redefined. Tunneling allows escaping from local minima, ensuring rapid and robust convergence.
# Global Minimum Search Method with Tunneling

This repository contains the implementation of a novel optimization algorithm for global minimum search that combines Monte Carlo sampling with a tunneling mechanism to escape local minima. The method is designed to be robust, fast, and parallelizable, making it suitable for applications where function evaluations are computationally expensive (e.g., radioastronomy).

---

## Table of Contents

- [Overview](#overview)
- [Algorithm Description](#algorithm-description)
  - [Base Algorithm (Monte Carlo Sampling)](#base-algorithm-monte-carlo-sampling)
  - [Tunneling Mechanism](#tunneling-mechanism)
- [Parameters](#parameters)
- [Usage Instructions](#usage-instructions)
- [Customization and Modifications](#customization-and-modifications)
- [Results and Discussion](#results-and-discussion)
- [References](#references)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

The algorithm presented in this repository addresses the challenge of finding the global minimum of complex functions, which typically have multiple local minima. By integrating a Monte Carlo-based sampling approach with a tunneling strategy, the algorithm effectively navigates the search space, reorienting its exploration when stagnation occurs. This results in a method that not only converges rapidly but is also stable under varying conditions.

---

## Algorithm Description

### Base Algorithm (Monte Carlo Sampling)

- **Idea:**  
  The algorithm begins by launching a fixed number of particles, N, randomly distributed over the search space.
  
- **Process:**  
  1. **Sampling:** Deploy N particles across the entire search domain.
  2. **Selection:** Evaluate the objective function for each particle and select the M particles that yield the lowest (best) values.
  3. **Refinement:** Define a new sampling region (typically an N-dimensional hypercube) around the best particle or group of particles.
  4. **Iteration:** Repeat the sampling and selection process in the new, reduced region to refine the search further.
  
This approach minimizes the number of evaluations required while focusing the search in promising areas.

### Tunneling Mechanism

- **Purpose:**  
  To overcome the common problem of algorithms getting trapped in local minima.
  
- **Mechanism:**  
  When the standard sampling process fails to produce a better candidate, a tunneling function is activated. This function reorients the search towards new regions by “tunneling” through barriers formed by local minima.

- **Tunneling Function:**  
  The tunneling function is defined as:

  $T(x) = \frac{f(x) - f(x^a)}{ \left[(x - x^a)' (x - x^a) \right]^{\eta} }   $ 


  where:
  - $x^a$ is the current candidate minimum.
  - $\eta$ is a tunable constant that controls the tunneling aggressiveness.
  
This mechanism allows the algorithm to explore both nearby and distant regions, ensuring that it does not remain confined to suboptimal solutions.

---

## Parameters

- **N:**  
  The total number of particles launched in each sampling iteration. A higher \(N\) increases the exploration capability but also the computational cost.

- **M:**  
  The number of best-performing particles selected from the \(N\) samples. These particles are used to define the next sampling region.

- **Size_ite:**  
  A parameter (ranging between 0 and 1) that determines the reduction in the sampling region’s size after each iteration. A balanced reduction is essential: too little reduction prevents convergence, whereas too much may not allow adequate search time.

- **$\eta$:**  
  A constant used in the tunneling function that influences the ability to escape local minima. Experimental results indicate that small variations (e.g., $\eta = 1$ vs. $\eta = 1.5$) have a minor impact on the final outcome, maintaining both convergence speed and result quality.

---

## Usage Instructions

### Prerequisites

- **Git:** To clone the repository.
- **Python 3:** The main implementation is provided in a Jupyter Notebook.
- **Required Libraries:** Check the notebook (`optimizaciónmontecarlo.ipynb`) for dependencies such as `numpy`, `matplotlib`, etc.

### Steps to Run

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/BrayhanPR1/Global-minimum-search-method-with-tunneling.git
   cd Global-minimum-search-method-with-tunneling
