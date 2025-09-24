#!/usr/bin/env python3
import os
import numpy as np


import pyphare.pharein as ph
from pyphare.cpp import cpp_lib
from pyphare.simulator.simulator import Simulator
from pyphare.simulator.simulator import startMPI

os.environ["PHARE_SCOPE_TIMING"] = "0"  # turn on scope timing


ph.NO_GUI()
cpp = cpp_lib()

cells = (200, 400, 50)
dl = (0.2, 0.2, 0.2)

diag_outputs = "."
time_step_nbr = 100
time_step = 0.001
final_time = time_step * time_step_nbr
timestamps = [0, final_time]


def config():
    # start_time = 0
    sim = ph.Simulation(
        time_step=time_step,
        time_step_nbr=time_step_nbr,
        dl=dl,
        cells=cells,
        refinement="tagging",
        max_nbr_levels=1,
        hyper_resistivity=0.001,
        resistivity=0.001,
        diag_options={
            "format": "phareh5",
            "options": {"dir": diag_outputs, "mode": "overwrite"},
        },
        # restart_options={
        #     "dir": "checkpoints",
        #     "mode": "overwrite",
        #     "elapsed_timestamps": [3600, 7200, 10800, 14400, 36000, 79000],
        #     # "restart_time": start_time,
        # }
        # strict=True,
    )

    def density(x, y, z):
        L = sim.simulation_domain()[1]
        return (
            0.2
            + 1.0 / np.cosh((y - L * 0.3) / 0.5) ** 2
            + 1.0 / np.cosh((y - L * 0.7) / 0.5) ** 2
        )

    def S(y, y0, l):
        return 0.5 * (1.0 + np.tanh((y - y0) / l))

    def by(x, y, z):
        Lx = sim.simulation_domain()[0]
        Ly = sim.simulation_domain()[1]
        w1 = 0.2
        w2 = 1.0
        x0 = x - 0.5 * Lx
        y1 = y - 0.3 * Ly
        y2 = y - 0.7 * Ly
        w3 = np.exp(-(x0 * x0 + y1 * y1) / (w2 * w2))
        w4 = np.exp(-(x0 * x0 + y2 * y2) / (w2 * w2))
        w5 = 2.0 * w1 / w2
        return (w5 * x0 * w3) + (-w5 * x0 * w4)

    def bx(x, y, z):
        Lx = sim.simulation_domain()[0]
        Ly = sim.simulation_domain()[1]
        w1 = 0.2
        w2 = 1.0
        x0 = x - 0.5 * Lx
        y1 = y - 0.3 * Ly
        y2 = y - 0.7 * Ly
        w3 = np.exp(-(x0 * x0 + y1 * y1) / (w2 * w2))
        w4 = np.exp(-(x0 * x0 + y2 * y2) / (w2 * w2))
        w5 = 2.0 * w1 / w2
        v1 = -1
        v2 = 1.0
        return (
            v1
            + (v2 - v1) * (S(y, Ly * 0.3, 0.5) - S(y, Ly * 0.7, 0.5))
            + (-w5 * y1 * w3)
            + (+w5 * y2 * w4)
        )

    def bz(x, y, z):
        return 0.1

    def b2(x, y, z):
        return bx(x, y, z) ** 2 + by(x, y, z) ** 2 + bz(x, y, z) ** 2

    def T(x, y, z):
        K = 1
        temp = 1.0 / density(x, y, z) * (K - b2(x, y, z) * 0.5)
        assert np.all(temp > 0)
        return temp

    def vxyz(x, y, z):
        return 0.0

    def vthxyz(x, y, z):
        return np.sqrt(T(x, y, z))

    C = "xyz"
    vvv = {
        **{f"vbulk{c}": vxyz for c in C},
        **{f"vth{c}": vthxyz for c in C},
        "nbr_part_per_cell": 50,
    }
    protons = {"charge": 1, "density": density, **vvv, "init": {"seed": 12334}}
    ph.MaxwellianFluidModel(bx=bx, by=by, bz=bz, protons=protons)
    ph.ElectronModel(closure="isothermal", Te=0.0)

    pop = "protons"
    ph.FluidDiagnostics(quantity="bulkVelocity", write_timestamps=timestamps)
    ph.FluidDiagnostics(
        quantity="density", write_timestamps=timestamps, population_name=pop
    )
    for quantity in ["E", "B"]:
        ph.ElectromagDiagnostics(quantity=quantity, write_timestamps=timestamps)
    ph.InfoDiagnostics(quantity="particle_count")  # defaults all coarse time steps

    return sim


if __name__ == "__main__":
    startMPI()
    Simulator(config(), print_one_line=False).run()
