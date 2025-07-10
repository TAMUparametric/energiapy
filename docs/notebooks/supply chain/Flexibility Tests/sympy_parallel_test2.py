import sympy as sp
from sympy import symbols, exp
import numpy as np
import itertools
import time
from typing import List, Tuple, Union
import multiprocessing as mp
import pickle

def factor_expr(i_expr):
    i, expr = i_expr
    print(f"Starting iteration {i}")
    return sp.factor(expr)

if __name__ == '__main__':
    # ---------------------- SYMBOLIC SETUP ----------------------

    # --- Define Symbols ---
    theta_syms = sp.symbols('theta_1 theta_2')
    d_syms = sp.symbols('d1 d2')
    theta_1, theta_2 = theta_syms
    d1, d2 = d_syms

    n_gl_list = [3, 3]

    # Bounds arrays
    theta1_bounds_array = np.array([
        [[0.0, 0.0, 0.0], [0.0, 0.0, 4.0]],  # d0 ± 10
        [[0.75, -1.5, -1.25], [0.0, 0.0, 4.0]]  # d1 ± 5
    ])

    theta2_bounds_array = np.array([
        [[-8/3, 2.0, -4.0, 2/3], [0.0, 0.0, 0.0, 4.0]],  # θ1 ± d2
        [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 4.0]],  # θ1 ± 2d2
        [[1/3, -0.5, 0.5, -1/3], [0.0, 0.0, 0.0, 4.0]]  # θ1 ± 3d2
    ])

    # PDF
    joint_pdf_expr = (2/sp.pi) * sp.exp(-2 * ((theta_1 - 2) ** 2 + (theta_2 - 2) ** 2))

    # Critical regions (CRs)
    # theta1_critical_regions: constraints in terms of d (shape: n_regions × n_ineqs × (m+1))
    theta1_critical_regions = np.array([
        [[1, -2, -5/3]],
        [[-1, 2, 5/3]]
    ], dtype=object)

    # theta2_critical_regions: constraints in terms of [theta1, d0, d1, const]
    theta2_critical_regions = np.array([
        [[-8/3, 2, -4, -10/3], [8/3, -2, 4, -2/3]],
        [[8/3, -4.0, 4.0, -8/3], [-8/3, 2, -4, 2/3]],
        [[-8/3, 4, -4, 8/3]]
    ], dtype=object)

    # --- Setup lists ---
    theta_bounds_list = [theta1_bounds_array, theta2_bounds_array]
    theta_regions_list = [theta1_critical_regions, theta2_critical_regions]

    # ---------------------- HELPER FUNCTIONS ----------------------

    # def compute_all_sf_expressions_generalized(
    #         theta_bounds_list,  # List of shape (n_regions_i, 2, coeff_len) for each θᵢ
    #         theta_regions_list,  # List of region constraint matrices for each θᵢ
    #         joint_pdf_expr,  # sympy expression in θ₁...θₙ
    #         d_syms,  # sympy symbols for uncertain parameters
    #         n_gl_list,  # List of quadrature points per θᵢ
    #         theta_syms  # [θ₁, θ₂, ..., θₙ]
    # ):
    #     n_theta = len(theta_syms)
    #     assert len(theta_bounds_list) == n_theta
    #     assert len(theta_regions_list) == n_theta
    #     assert len(n_gl_list) == n_theta
    #
    #     quadrature_data = [np.polynomial.legendre.leggauss(n) for n in n_gl_list]
    #     sf_exprs = []
    #     sf_regions = []
    #
    #     # First loop over θ₁ regions
    #     n_t1_regions = theta_bounds_list[0].shape[0]
    #     n_q1 = n_gl_list[0]
    #     xi_1, wi_1 = quadrature_data[0]
    #
    #     for t1_region_idx in range(n_t1_regions):
    #         # θ₁ bounds (only depend on d_syms)
    #         t1_min_expr = affine_expr(theta_bounds_list[0][t1_region_idx, 0], d_syms)
    #         t1_max_expr = affine_expr(theta_bounds_list[0][t1_region_idx, 1], d_syms)
    #
    #         # θ₁ quadrature points
    #         # theta1_points = [
    #         #     sp.simplify(0.5 * (t1_max_expr - t1_min_expr) * xi + 0.5 * (t1_max_expr + t1_min_expr))
    #         #     for xi in xi_1
    #         # ]
    #         theta1_points = [
    #             0.5 * (t1_max_expr - t1_min_expr) * xi + 0.5 * (t1_max_expr + t1_min_expr) for xi in xi_1
    #         ]
    #         # θ₁ region constraints
    #         t1_region_constraints = theta_regions_list[0][t1_region_idx]
    #         t1_ineqs = [
    #             sum(c * d for c, d in zip(row[:-1], d_syms)) + row[-1] <= 0
    #             for row in t1_region_constraints
    #         ]
    #
    #         # For each θ₁ point, now we consider all combinations of θ₂ region indices (per θ₁ point)
    #         n_t2_regions = theta_bounds_list[1].shape[0]
    #         t2_region_choices = list(itertools.product(range(n_t2_regions), repeat=n_q1))
    #
    #         for t2_combo in t2_region_choices:
    #             sf_sum = 0
    #             region_ineqs = list(t1_ineqs)
    #
    #             for i in range(n_q1):
    #                 t1 = theta1_points[i]
    #                 w1 = wi_1[i]
    #                 t2_region_idx = t2_combo[i]
    #
    #                 # θ₂ bounds depend on θ₁ and d
    #                 t2_min_expr = affine_expr(theta_bounds_list[1][t2_region_idx, 0], [t1] + list(d_syms))
    #                 t2_max_expr = affine_expr(theta_bounds_list[1][t2_region_idx, 1], [t1] + list(d_syms))
    #                 xi_2, wi_2 = quadrature_data[1]
    #                 n_q2 = n_gl_list[1]
    #
    #                 # θ₂ region constraints
    #                 for row in theta_regions_list[1][t2_region_idx]:
    #                     θ1_coeff = row[0]
    #                     d_coeffs = row[1:-1]
    #                     const = row[-1]
    #                     ineq = θ1_coeff * t1 + sum(c * d for c, d in zip(d_coeffs, d_syms)) + const <= 0
    #                     # region_ineqs.append(sp.simplify(ineq))
    #                     region_ineqs.append(ineq)
    #
    #                 for j in range(n_q2):
    #                     t2 = 0.5 * (t2_max_expr - t2_min_expr) * xi_2[j] + 0.5 * (t2_max_expr + t2_min_expr)
    #                     # pdf_val = joint_pdf_expr.subs({theta_syms[0]: t1, theta_syms[1]: sp.simplify(t2)})
    #                     pdf_val = joint_pdf_expr.subs({theta_syms[0]: t1, theta_syms[1]: t2})
    #                     weight = w1 * wi_2[j]
    #                     scale = 0.25 * (t1_max_expr - t1_min_expr) * (t2_max_expr - t2_min_expr)
    #                     sf_sum += weight * scale * pdf_val
    #
    #             # sf_exprs.append(sp.simplify(sf_sum))
    #             sf_exprs.append(sf_sum)
    #             sf_regions.append(region_ineqs)
    #
    #     return sf_exprs, sf_regions

    def affine_expr(coeffs, symbols):
        return sum(c * s for c, s in zip(coeffs[:-1], symbols)) + coeffs[-1]


    def generate_region_combos(region_sizes, n_gl):
        """Generate region index combinations based on critical region structure."""
        n_theta = len(region_sizes)
        region_combo_shape = []
        for k in range(n_theta):
            n_paths = int(np.prod(n_gl[:k])) if k > 0 else 1
            region_combo_shape.extend([range(region_sizes[k])] * n_paths)
        return list(itertools.product(*region_combo_shape))


    def compute_sf_expressions_region_combo_based(
            theta_bounds_list,
            theta_regions_list,
            joint_pdf_expr,
            d_syms,
            n_gl_list,
            theta_syms
    ):
        n_theta = len(theta_syms)
        quad_data = [np.polynomial.legendre.leggauss(n) for n in n_gl_list]
        region_sizes = [bounds.shape[0] for bounds in theta_bounds_list]
        region_combos = generate_region_combos(region_sizes, n_gl_list)

        sf_exprs = []
        sf_regions = []

        for region_combo in region_combos:
            combo_ptr = 0
            paths = [([], 1, 1, [])]  # (theta_vals, weight, scale, constraints)

            for level in range(n_theta):
                xi, wi = quad_data[level]
                new_paths = []

                # Determine how many paths we’re expanding at this level
                n_existing_paths = len(paths)
                for path_idx in range(n_existing_paths):
                    theta_vals, weight, scale, constraints = paths[path_idx]
                    region_idx = region_combo[combo_ptr]
                    combo_ptr += 1

                    # Compute bounds
                    bound_inputs = theta_vals + list(d_syms)
                    bounds = theta_bounds_list[level][region_idx]
                    t_min = affine_expr(bounds[0], bound_inputs)
                    t_max = affine_expr(bounds[1], bound_inputs)

                    # Add region constraints
                    rows = theta_regions_list[level][region_idx]
                    new_constraints = list(constraints)
                    for row in rows:
                        t_coeffs = row[:level]
                        d_coeffs = row[level:-1]
                        const = row[-1]
                        lhs = sum(c * theta_vals[i] for i, c in enumerate(t_coeffs)) + \
                              sum(c * d for c, d in zip(d_coeffs, d_syms)) + const
                        new_constraints.append(sp.simplify(lhs <= 0))

                    for q in range(len(xi)):
                        t = 0.5 * (t_max - t_min) * xi[q] + 0.5 * (t_max + t_min)
                        new_theta_vals = theta_vals + [sp.simplify(t)]
                        new_weight = weight * wi[q]
                        new_scale = scale * 0.5 * (t_max - t_min)
                        new_paths.append((new_theta_vals, new_weight, new_scale, new_constraints))

                paths = new_paths

            # Final integration over all quadrature paths for this region combo
            sf_sum = 0
            for theta_vals, weight, scale, constraints in paths:
                theta_subs = {sym: val for sym, val in zip(theta_syms, theta_vals)}
                pdf_val = joint_pdf_expr.subs(theta_subs)
                sf_sum += weight * scale * pdf_val

            sf_exprs.append(sp.simplify(sf_sum))
            sf_regions.append(paths[0][3])  # constraints same for all in this combo

        return sf_exprs, sf_regions, len(region_combos)


    # ---------------------- EXECUTE ----------------------
    print('Starting exhaustive SF expression computation')
    s = time.time()
    sf_exprs, sf_regions, num_regions = compute_sf_expressions_region_combo_based(
        theta_bounds_list,
        theta_regions_list,
        joint_pdf_expr,
        [d1, d2],
        n_gl_list,
        theta_syms
    )
    e = time.time()
    print(f'Time to compute all SF expressions: {e - s}')
    print(f'Number of expressions generated: {len(sf_exprs)}')
    print(f'Number of critical regions generated: {len(sf_regions)}')

    # print('Starting factoring SF expressions')
    # s = time.time()
    # with mp.Pool(processes=mp.cpu_count()) as pool:
    #     factored_sf_exprs = pool.map(factor_expr, enumerate(sf_exprs))
    # e = time.time()
    # print(f'Time to factor SF expressions: {e-s}')
    #
    # print(factored_sf_exprs[0])

    with open('sf_exprs.pkl', 'wb') as f:
        pickle.dump(sf_exprs, f)

    with open('sf_regions.pkl', 'wb') as f:
        pickle.dump(sf_regions, f)