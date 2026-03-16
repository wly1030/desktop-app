#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Yade DEM Direct Shear Box Test Simulation
==========================================
Usage:
    yade -x yade_simulation.py <params_json_file>

Output:
    Progress messages go to stderr.
    On success, prints one line to stdout:
        RESULT_JSON:<json_data>

Parameters (all values may be numeric literals or simple Python expressions):
    in_radius                  particle radius [mm]
    young1 / poisson1          sphere Young's modulus [Pa] / Poisson's ratio
    friction_angle1_radians    sphere friction angle [degrees, despite the name]
    density1                   sphere density [kg/m^3]
    young2 / poisson2          wall Young's modulus / Poisson's ratio
    friction_angle2            wall friction angle [degrees]
    density2                   wall density [kg/m^3]
    damping                    Newton integrator damping coefficient
    vel                        shear velocity [mm/s] (sign = direction)
    normal_stiffness           normal stiffness coefficient [N/m]
    dt                         timestep multiplier for PWaveTimeStep (0–1)
    alpha                      additional stiffness multiplier (reserved)
    interaction_detection_factor  collider sweep factor
    aabb_enlarge_factor        AABB enlargement factor
    geom_facet_box1_1_1/2      upper box half-size x/y [m]
    geom_facet_box1_1_3        upper box top-face z position [m or expression]
    geom_facet_box2_1_3        lower box bottom-face z position [m or expression]
    geom_facet_box2_2_3        shear-plane z position [m or expression]
    set_perm_f1/f2/f3          permanent force components on top plate [N]
    mass                       top loading plate mass [kg]
    gravity                    gravity vector "gx,gy,gz"
    o_iter1                    consolidation phase iterations
    o_iter2                    shear phase max iterations
    dspl                       target shear displacement [m]
    iter_period                recording interval [iterations]
"""

from __future__ import print_function

import sys
import json
import os
import math

# ---------------------------------------------------------------------------
# Safe expression evaluator (no builtins, math available)
# ---------------------------------------------------------------------------
_SAFE_NS = {"__builtins__": {}, "math": math}


def _ev(raw, default=0.0):
    """Evaluate *raw* as a float expression; fall back to *default*."""
    s = str(raw).strip().lstrip('%').strip()
    try:
        return float(eval(s, _SAFE_NS))
    except Exception:
        try:
            return float(default)
        except Exception:
            return 0.0


def _load_params(path):
    if path and os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    return {}


def _get(P, key, default=0.0):
    return _ev(P.get(key, default), default)


def _get_expr(P, key, default_expr):
    raw = str(P.get(key, default_expr)).strip()
    try:
        return float(eval(raw, _SAFE_NS))
    except Exception:
        return float(eval(str(default_expr), _SAFE_NS))


def _get_vec3(P, key, default='0,0,0'):
    raw = str(P.get(key, default))
    try:
        parts = raw.split(',')
        return [float(p.strip()) for p in parts]
    except Exception:
        return [0.0, 0.0, 0.0]


# ---------------------------------------------------------------------------
# Main simulation
# ---------------------------------------------------------------------------
def run_simulation(P):
    # ── Material parameters ─────────────────────────────────────────────────
    r_mm    = _get(P, 'in_radius', 15)
    r       = r_mm * 1e-3                               # mm → m

    young1  = _get(P, 'young1', 1e9)
    nu1     = _get(P, 'poisson1', 0.4)
    # NOTE: named "…_radians" historically; the value is expected in *degrees* and is
    # converted to radians below with math.radians().
    phi1    = math.radians(_get(P, 'friction_angle1_radians', 40))
    rho1    = _get(P, 'density1', 2650)

    young2  = _get(P, 'young2', 1e9)
    nu2     = _get(P, 'poisson2', 0.4)
    phi2    = math.radians(_get(P, 'friction_angle2', 0))
    rho2    = _get(P, 'density2', 2600)

    # ── Simulation control ───────────────────────────────────────────────────
    damp        = _get(P, 'damping', 0.4)
    shear_vel   = _get(P, 'vel', -0.681462)             # mm/s
    shear_vel_m = shear_vel * 1e-3                       # m/s
    dt_fac      = _get(P, 'dt', 0.5)
    idf         = _get(P, 'interaction_detection_factor', 1.0)
    aef         = _get(P, 'aabb_enlarge_factor', 1.0)

    # ── Box geometry ─────────────────────────────────────────────────────────
    bx       = _get(P, 'geom_facet_box1_1_1', 0.5)     # half-size x [m]
    by_      = _get(P, 'geom_facet_box1_1_2', 0.5)     # half-size y [m]
    top_z    = _get_expr(P, 'geom_facet_box1_1_3', '0.6124/2+0.05')
    bot_z    = _get_expr(P, 'geom_facet_box2_1_3', '-0.6124/2-0.005')
    split_z  = _get_expr(P, 'geom_facet_box2_2_3', '0.6124/2')

    # ── Loading ───────────────────────────────────────────────────────────────
    pf1      = _get(P, 'set_perm_f1', 0)
    pf2      = _get(P, 'set_perm_f2', 0)
    pf3      = _get(P, 'set_perm_f3', -1)
    top_mass = _get(P, 'mass', 1e6)
    grav     = _get_vec3(P, 'gravity', '0,0,0')

    # ── Iteration control ─────────────────────────────────────────────────────
    o_iter1  = max(1, int(_get(P, 'o_iter1', 50000)))
    o_iter2  = max(1, int(_get(P, 'o_iter2', 100000)))
    dspl_max = abs(_get(P, 'dspl', 0.01))
    period   = max(1, int(_get(P, 'iter_period', 10)))

    area     = (2 * bx) * (2 * by_)                    # shear plane area [m^2]

    print("INFO: Parameters loaded.", file=sys.stderr)
    print("INFO:   Sphere r={:.4f} m  E={:.2e} Pa  phi={:.1f} deg  rho={:.0f}".format(
        r, young1, math.degrees(phi1), rho1), file=sys.stderr)
    print("INFO:   Box  x=[-{bx},{bx}]  y=[-{by},{by}]  z=[{bot:.3f},{top:.3f}]  split_z={sp:.3f}".format(
        bx=bx, by=by_, bot=bot_z, top=top_z, sp=split_z), file=sys.stderr)
    print("INFO:   Phase1={} iters  Phase2={} iters  dspl_max={} m".format(
        o_iter1, o_iter2, dspl_max), file=sys.stderr)

    # ── Materials ─────────────────────────────────────────────────────────────
    mat_sph = O.materials.append(FrictMat(
        young=young1, poisson=nu1, frictionAngle=phi1,
        density=rho1, label='sphere'))
    mat_wall = O.materials.append(FrictMat(
        young=young2, poisson=nu2, frictionAngle=phi2,
        density=rho2, label='wall'))

    # ── Box walls ─────────────────────────────────────────────────────────────
    # Lower box: bottom + 4 sides (wallMask 31 = bits 0-4, no +z top)
    lower_center_z  = (bot_z + split_z) / 2.0
    lower_half_h    = (split_z - bot_z) / 2.0
    lower_ids = O.bodies.append(
        utils.facetBox(
            center=Vector3(0, 0, lower_center_z),
            halfSize=Vector3(bx, by_, lower_half_h),
            wallMask=31,
            material=mat_wall,
            fixed=True
        )
    )

    # Upper box: top + 4 sides (wallMask 47 = bits 0-3,5 = no -z bottom)
    upper_center_z  = (split_z + top_z) / 2.0
    upper_half_h    = (top_z - split_z) / 2.0
    upper_ids = O.bodies.append(
        utils.facetBox(
            center=Vector3(0, 0, upper_center_z),
            halfSize=Vector3(bx, by_, upper_half_h),
            wallMask=47,
            material=mat_wall,
            fixed=False
        )
    )
    # Clump upper facets into one rigid body
    upper_clump = O.bodies.clump(upper_ids)

    # Block upper box: only x-translation allowed (z-translation via plate)
    O.bodies[upper_clump].state.blockedDOFs = 'yzXYZ'

    # ── Top loading plate ──────────────────────────────────────────────────────
    top_plate_id = O.bodies.append(
        utils.wall(top_z, axis=2, sense=-1, material=mat_wall)
    )
    top_plate = O.bodies[top_plate_id]
    top_plate.state.mass   = top_mass
    top_plate.state.inertia = Vector3(1, 1, 1)
    top_plate.state.blockedDOFs = 'xyXYZ'   # only z-translation

    # ── Sphere packing ────────────────────────────────────────────────────────
    print("INFO: Packing spheres...", file=sys.stderr)
    sp = pack.SpherePack()
    sp.makeCloud(
        minCorner=Vector3(-bx + r * 1.05, -by_ + r * 1.05, bot_z + r * 1.05),
        maxCorner=Vector3( bx - r * 1.05,  by_ - r * 1.05, split_z - r * 1.05),
        rMean=r, rRelFuzz=0.2, num=-1,
        periodic=False
    )
    sp.toSimulation(material=mat_sph)
    print("INFO: {} spheres created.".format(
        sum(1 for b in O.bodies if isinstance(b.shape, Sphere))), file=sys.stderr)

    # ── Engines ──────────────────────────────────────────────────────────────
    O.engines = [
        ForceResetter(),
        InsertionSortCollider(
            [Bo1_Sphere_Aabb(aabbEnlargeFactor=max(aef, idf)),
             Bo1_Wall_Aabb(),
             Bo1_Facet_Aabb()],
            verletDist=r * 0.5
        ),
        InteractionLoop(
            [Ig2_Sphere_Sphere_ScGeom(),
             Ig2_Wall_Sphere_ScGeom(),
             Ig2_Facet_Sphere_ScGeom()],
            [Ip2_FrictMat_FrictMat_FrictPhys()],
            [Law2_ScGeom_FrictPhys_CundallStrack()]
        ),
        NewtonIntegrator(
            damping=damp,
            gravity=Vector3(grav[0], grav[1], grav[2])
        ),
        PyRunner(command='_record()', iterPeriod=period, label='recorder')
    ]

    O.dt = dt_fac * PWaveTimeStep()
    print("INFO: dt = {:.3e} s".format(O.dt), file=sys.stderr)

    # ── Data accumulators ─────────────────────────────────────────────────────
    ph1_i   = []   # iteration
    ph1_ub  = []   # unbalanced force
    ph1_ty  = []   # top plate z-position
    ph2_d   = []   # shear displacement
    ph2_tau = []   # shear stress [kPa]

    _phase     = [1]
    _upper_x0  = [0.0]
    _iter_shear_start = [0]

    def _record():
        ub  = unbalancedForce()
        ty  = O.bodies[top_plate_id].state.pos[2]
        ph1_i.append(O.iter)
        ph1_ub.append(float(ub))
        ph1_ty.append(float(ty))

        if _phase[0] == 2:
            # Shear displacement of the upper clump
            ux = O.bodies[upper_clump].state.pos[0] - _upper_x0[0]
            # Shear force = reaction on lower box side walls (x-component)
            fx = sum(float(O.forces.f(bid)[0]) for bid in lower_ids)
            tau = abs(fx) / area * 1e-3   # Pa → kPa
            ph2_d.append(abs(float(ux)))
            ph2_tau.append(float(tau))
            # Stop if target displacement reached
            if abs(ux) >= dspl_max:
                O.pause()

    # ── Phase 1: Consolidation ────────────────────────────────────────────────
    # Apply normal (vertical) force on top plate each step via constant force
    O.forces.setPermF(top_plate_id, Vector3(pf1, pf2, pf3 * abs(top_mass * 9.81)))

    print("INFO: Phase 1 – consolidation ({} iters)...".format(o_iter1), file=sys.stderr)
    O.run(o_iter1, wait=True)
    print("INFO: Consolidation done. unbalanced = {:.4f}".format(unbalancedForce()),
          file=sys.stderr)

    # ── Phase 2: Shear ────────────────────────────────────────────────────────
    _phase[0] = 2
    _upper_x0[0] = float(O.bodies[upper_clump].state.pos[0])
    _iter_shear_start[0] = O.iter

    # Apply shear velocity
    O.bodies[upper_clump].state.vel = Vector3(shear_vel_m, 0, 0)
    O.bodies[upper_clump].state.blockedDOFs = 'yXYZ'   # allow x and z now

    print("INFO: Phase 2 – shear (vel={:.3e} m/s, dspl_max={} m, {} iters)...".format(
        shear_vel_m, dspl_max, o_iter2), file=sys.stderr)
    O.run(o_iter2, wait=True)
    print("INFO: Shear done.", file=sys.stderr)

    # ── Output ────────────────────────────────────────────────────────────────
    result = {
        'i':           ph1_i,
        'unbalanced':  ph1_ub,
        # Key named 'top_y' for frontend compatibility; value is the top plate z-position.
        'top_y':       ph1_ty,
        'dspl':        ph2_d,
        'shearStress': ph2_tau,
    }
    line = "RESULT_JSON:" + json.dumps(result)
    print(line)
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Entry point (works with both `yade -x script.py` and `python script.py`)
# ---------------------------------------------------------------------------
if __name__ == '__main__' or 'yade' in sys.modules or 'O' in dir():
    P = _load_params(sys.argv[1] if len(sys.argv) > 1 else None)
    try:
        run_simulation(P)
    except Exception as exc:
        import traceback
        traceback.print_exc(file=sys.stderr)
        err_result = {
            'i': [], 'unbalanced': [], 'top_y': [],
            'dspl': [], 'shearStress': [],
            'error': str(exc)
        }
        print("RESULT_JSON:" + json.dumps(err_result))
        sys.stdout.flush()
        sys.exit(1)
