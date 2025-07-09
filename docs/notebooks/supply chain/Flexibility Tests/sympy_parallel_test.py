import sympy as sp
from sympy import symbols, exp
import numpy as np
import itertools
import time
import multiprocessing as mp
import pickle

def factor_expr(i_expr):
    i, expr = i_expr
    print(f"Starting iteration {i}")
    return sp.factor(expr)

if __name__ == '__main__':
    # ---------------------- SYMBOLIC SETUP ----------------------

    # Design variables
    m = 2  # number of design variables
    d = sp.symbols(f'd0:{m}')  # d0, d1, ..., d{m-1}
    theta_1, theta_2 = sp.symbols('theta_1 theta_2')

    # Gauss–Legendre quadrature settings
    n_gl = [1, 1]
    xi_1, wi_1 = np.polynomial.legendre.leggauss(n_gl[0])
    xi_2, wi_2 = np.polynomial.legendre.leggauss(n_gl[1])

    # ---------------------- USER INPUT ----------------------

    # theta1_bounds_array: shape (n1, 2, m+1)
    # theta2_bounds_array: shape (n2, 2, m+2)
    theta1_bounds_array = np.array([
        [[0.0, 0.0, 0.0], [0.0, 0.0, 4.0]],  # d0 ± 10
        # [[0.75, -1.5, -1.25], [0.0, 0.0, 4.0]]  # d1 ± 5
    ])

    theta2_bounds_array = np.array([
        [[-8/3, 2.0, -4.0, 2/3], [0.0, 0.0, 0.0, 4.0]],  # θ1 ± d2
        # [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 4.0]],  # θ1 ± 2d2
        # [[1/3, -0.5, 0.5, -1/3], [0.0, 0.0, 0.0, 4.0]]  # θ1 ± 3d2
    ])

    # Joint PDF
    joint_pdf_expr = (2 / sp.pi) * sp.exp(-2 * ((theta_1 - 2) ** 2 + (theta_2 - 2) ** 2))


    # ---------------------- HELPER FUNCTIONS ----------------------

    def affine_expr(coeffs, symbols):
        return sum(c * s for c, s in zip(coeffs[:-1], symbols)) + coeffs[-1]


    def compute_all_sf_expressions(t1_bounds_array, t2_bounds_array, joint_pdf_expr, d_syms, n_gl):
        n_t1_regions = t1_bounds_array.shape[0]
        n_t2_regions = t2_bounds_array.shape[0]
        n_q1, n_q2 = n_gl

        # Generate all combinations of t2 region choices for each quadrature point of θ1
        t2_region_choices = list(itertools.product(range(n_t2_regions), repeat=n_q1))

        sf_exprs = []

        for t1_region_idx in range(n_t1_regions):
            t1_min_expr = affine_expr(t1_bounds_array[t1_region_idx, 0], d_syms)
            t1_max_expr = affine_expr(t1_bounds_array[t1_region_idx, 1], d_syms)

            # Precompute θ1 quadrature points
            theta1_points = []
            for i in range(n_q1):
                t1 = 0.5 * (t1_max_expr - t1_min_expr) * xi_1[i] + 0.5 * (t1_max_expr + t1_min_expr)
                theta1_points.append(sp.simplify(t1))

            for t2_combo in t2_region_choices:
                sf_sum = 0
                for i in range(n_q1):
                    t1 = theta1_points[i]
                    t2_region_idx = t2_combo[i]

                    t2_min_expr = affine_expr(t2_bounds_array[t2_region_idx, 0], [t1] + list(d_syms))
                    t2_max_expr = affine_expr(t2_bounds_array[t2_region_idx, 1], [t1] + list(d_syms))

                    for j in range(n_q2):
                        t2 = 0.5 * (t2_max_expr - t2_min_expr) * xi_2[j] + 0.5 * (t2_max_expr + t2_min_expr)
                        pdf_val = joint_pdf_expr.subs({theta_1: t1, theta_2: sp.simplify(t2)})
                        weight = wi_1[i] * wi_2[j]
                        scale = 0.25 * (t1_max_expr - t1_min_expr) * (t2_max_expr - t2_min_expr)
                        sf_sum += weight * scale * pdf_val

                sf_exprs.append(sf_sum)

        return sf_exprs


    # ---------------------- EXECUTE ----------------------
    print('Starting exhaustive SF expression computation')
    s = time.time()
    sf_exprs = compute_all_sf_expressions(theta1_bounds_array, theta2_bounds_array, joint_pdf_expr, d, n_gl)
    e = time.time()
    print(f'Time to compute all SF expressions: {e - s}')
    print(f'Number of expressions generated: {len(sf_exprs)}')

    # print('Starting factoring SF expressions')
    # s = time.time()
    # with mp.Pool(processes=mp.cpu_count()) as pool:
    #     factored_sf_exprs = pool.map(factor_expr, enumerate(sf_exprs))
    # e = time.time()
    # print(f'Time to factor SF expressions: {e-s}')
    #
    # print(factored_sf_exprs[0])

    with open('factored_sf_exprs.pkl', 'wb') as f:
        pickle.dump(sf_exprs, f)