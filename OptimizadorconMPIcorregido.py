import numpy as np
import time
import random
from mpi4py import MPI
import pickle

# Funciones objetivo (sin cambios)

# Configuración MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

class Particle:
    def __init__(self, pos, value, zone_id):
        self.pos = np.array(pos)
        self.value = value
        self.zone_id = zone_id

    def __repr__(self):
        pos_str = ", ".join(f"{p:.2e}" for p in self.pos)
        return f"Posición=[{pos_str}], Zona={self.zone_id:.2f}, Valor={self.value:.5f}"

def metodo_busqueda_aleatorio(cycles, N, M, distrib, rang, zone_size, objective_function, x_0):
    dim = len(rang)
    rang = np.array(rang)
    
    if np.allclose(x_0, [0]*dim):
        rangite = rang * (1 - zone_size)
    else:
        rangite = np.array([x_0 - zone_size*(rang[:,1] - rang[:,0]), 
                        x_0 + zone_size*(rang[:,1] - rang[:,0])])

    particles = []
    # Ciclo 0 solo en rank 0
    if rank == 0:
        for i in range(N):
            pos = [np.random.uniform(low=rang[j][0], high=rang[j][1]) for j in range(dim)]
            value = objective_function(pos)
            particles.append(Particle(pos, value, 0))
        particles.sort(key=lambda p: p.value)
        best_particles = particles[:M]
    else:
        best_particles = None

    # Distribuir mejores partículas y rangite
    best_particles = comm.bcast(best_particles, root=0)
    rangite = comm.bcast(rangite, root=0)

    global_zone_id = 0
    final_zone_particles = {}

    for cycle in range(1, cycles):
        if rank == 0:
            data = [(p, rangite) for p in best_particles]
        else:
            data = None

        # Scatter datos a cada proceso
        local_data = comm.scatter(data, root=0)
        parent, local_rangite = local_data

        # Muestreo
        if distrib == "normal":
            lk = np.sum(np.abs(local_rangite), axis=1)
            samples = np.random.normal(loc=parent.pos, scale=lk, size=(N, dim))
        else:
            low = parent.pos - zone_size * (rang[:,1] - rang[:,0])
            high = parent.pos + zone_size * (rang[:,1] - rang[:,0])
            samples = np.random.uniform(low=low, high=high, size=(N, dim))

        current_zone_particles = []
        for s in samples:
            val = objective_function(s)
            current_zone_particles.append(Particle(s, val, global_zone_id + rank))

        # Recoger resultados en rank 0
        gathered_particles = comm.gather(current_zone_particles, root=0)

        if rank == 0:
            best_particles = []
            for zone in gathered_particles:
                best_in_zone = min(zone, key=lambda p: p.value)
                best_particles.append(best_in_zone)
            best_particles.sort(key=lambda p: p.value)
            best_particles = best_particles[:M]
            rangite *= (1 - zone_size)
        else:
            best_particles = None

        best_particles = comm.bcast(best_particles, root=0)

    if rank == 0:
        return min(best_particles, key=lambda p: p.value)
    else:
        return None

class TunnelingOptimizer:
    def __init__(self, func, bounds, max_cycles=50, eta=2.0, tol=1e-6):
        self.func = func
        self.bounds = bounds
        self.max_cycles = max_cycles
        self.eta = eta
        self.tol = tol
        self.minima = []
        self.f_values = []

    def tunneling_function(self, x):
        f_current = self.f_values[-1] if self.f_values else np.inf
        numerator = self.func(x) - f_current
        denominator = 1.0
        for x_min in self.minima:
            distance = np.linalg.norm(x - x_min)
            denominator *= (distance**2 + 1e-6)
        return numerator / (denominator ** self.eta)

    def minimize_phase(self, x0):
        if rank == 0:
            res = metodo_busqueda_aleatorio(10,100, size, "uniforme", self.bounds, 0.35, self.func, x0)
            return res.pos, res.value
        else:
            metodo_busqueda_aleatorio(10,100,size, "uniforme", self.bounds, 0.35, self.func, x0)
            return None, None

    def tunneling_phase(self, x_last):
        best_x = None
        best_T = np.inf
        for _ in range(10):
            x_candidate, _ = self.minimize_phase(x_last)
            if x_candidate is None:
                continue
            T_val = self.tunneling_function(x_candidate)
            if T_val <= 0:
                return x_candidate
            if T_val < best_T:
                best_T = T_val
                best_x = x_candidate
        if best_x is not None:
            res = metodo_busqueda_aleatorio(10,100, size, "uniforme", self.bounds, 0.35, self.tunneling_function, best_x)
            return res.pos if res.value <= 0 else None
        return None

    def optimize(self, x0):
        x_current = np.array(x0)
        for cycle in range(self.max_cycles):
            x_min, f_min = self.minimize_phase(x_current)
            if rank == 0:
                if not self.minima or f_min < self.f_values[-1] - self.tol:
                    self.minima.append(x_min)
                    self.f_values.append(f_min)
                x_tunnel = self.tunneling_phase(x_min)
                if x_tunnel is None:
                    break
                x_current = x_tunnel
        if rank == 0:
            idx = np.argmin(self.f_values)
            return self.minima[idx], self.minima, cycle
        return None, None, 0

if __name__ == "__main__":

    

    def griewank(pos):
        return np.sum([pos[i]**2/4000 for i in range(len(pos))]) - np.prod([np.cos(pos[i]/np.sqrt(i+1)) for i in range(len(pos))]) + 1
    
    bounds = [(-5.12, 5.12)] * 2
    optimizer = TunnelingOptimizer(griewank, bounds)
    listtime = np.zeros(50)
    for i in range(50):
        if rank == 0:
            start = time.time()
            result, minima, cycles = optimizer.optimize([0, 0])
            finish = time.time() - start
            listtime[i] = finish
            print(f"Tiempo de ejecusión en el ciclo: {finish}")
        
        else:
            optimizer.optimize([0, 0])
    
    meantime  = np.mean(listtime)
    print(f"Tiempo de ejecusión: {meantime}")
    
