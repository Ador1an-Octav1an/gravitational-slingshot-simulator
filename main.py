import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button   # ← Button added
from matplotlib.patches import Arc
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# ---------------- Constants ----------------
u = 13.1   # Jupiter orbital velocity (km/s)
R = 0.55
clear = 0.3
ANGLE_OFFSET = 0.70

# ---------------- Helpers ----------------
def norm(v): return np.hypot(v[0], v[1])

def compute_v2(v1, theta_deg, u=13.1):
    theta = np.deg2rad(theta_deg)
    return (v1 + 2*u) * np.sqrt(1 - (4*u*v1*(1 - np.cos(theta)))/((v1 + 2*u)**2))

def trajectory(theta_deg, incoming_angle_deg=50, R=0.55, clear=0.3, n=1000):
    deg = np.pi/180
    phi_in = -incoming_angle_deg*deg
    e = 1/np.sin(theta_deg*deg/2)
    rp = R + clear
    p = rp*(1+e)
    f_inf = np.arccos(-1/e)
    omega = phi_in + theta_deg*deg/2
    f = np.linspace(-f_inf + 1e-3, f_inf - 1e-3, n)
    r = p/(1 + e*np.cos(f))
    phi = omega + f
    x, y = r*np.cos(phi), r*np.sin(phi)
    return x, y

def outward_normal(p, t):
    n = np.array([-t[1], t[0]])
    if np.dot(p, n) < 0: n = -n
    return n / norm(n)

# ---------------- Figure (single window, bigger, graphs left) ----------------
fig = plt.figure(figsize=(16, 9))
gs  = GridSpec(nrows=3, ncols=2, width_ratios=[1.0, 3.0], height_ratios=[1,1,1],
               wspace=0.35, hspace=0.40)
fig.subplots_adjust(bottom=0.14)

# Left column: graphs stacked
ax_g1 = fig.add_subplot(gs[0, 0])
ax_g2 = fig.add_subplot(gs[1, 0])
ax_g3 = fig.add_subplot(gs[2, 0])

def nudge_up(ax, dy=0.03):
    p = ax.get_position()
    ax.set_position([p.x0, p.y0 + dy, p.width, p.height])
nudge_up(ax_g1, 0.03); nudge_up(ax_g2, 0.03); nudge_up(ax_g3, 0.03)

# Right column: main visual
ax_main = fig.add_subplot(gs[:, 1])
ax_main.set_aspect('equal')
ax_main.set_xlim(-6, 7); ax_main.set_ylim(-6, 6)
ax_main.axis('off')

planet = plt.Circle((0, 0), R, color='gray', ec='k', lw=1.8, zorder=10)
ax_main.add_artist(planet)
traj_line, = ax_main.plot([], [], 'k', lw=2.5)

V2_LABEL_POS = (2.6, 4.4)
text_v2 = ax_main.text(*V2_LABEL_POS, '', fontsize=12, weight='bold')

# Sliders
ax_theta = fig.add_axes([0.12, 0.075, 0.76, 0.028])
ax_v1    = fig.add_axes([0.12, 0.035, 0.76, 0.028])
slider_theta = Slider(ax_theta, 'Deflection θ°', 20, 100, valinit=60)
slider_v1    = Slider(ax_v1,    'v₁ (km/s)',      5,  25, valinit=10)

# Domains for curves (same as plots)
TH_MIN, TH_MAX = slider_theta.valmin, slider_theta.valmax
V1_MIN, V1_MAX = slider_v1.valmin, slider_v1.valmax
theta_grid = np.linspace(TH_MIN, TH_MAX, 300)
v1_grid    = np.linspace(V1_MIN, V1_MAX, 300)

# Graph 1
curve_g1, = ax_g1.plot(theta_grid, compute_v2(slider_v1.val, theta_grid, u), lw=2, color='black')
pt_g1,    = ax_g1.plot([slider_theta.val],
                       [compute_v2(slider_v1.val, slider_theta.val, u)],
                       'o', ms=6, color='red', zorder=5)
ax_g1.set_xlabel('Deflection angle θ (deg)')
ax_g1.set_ylabel('Exit velocity v₂ (km/s)')
ax_g1.set_title('v₂ vs θ (Jupiter)')
ax_g1.grid(True, alpha=0.3)

# Graph 2
curve_g2, = ax_g2.plot(v1_grid, compute_v2(v1_grid, slider_theta.val, u), lw=2, color='black')
pt_g2,    = ax_g2.plot([slider_v1.val],
                       [compute_v2(slider_v1.val, slider_theta.val, u)],
                       'o', ms=6, color='red', zorder=5)
ax_g2.set_xlabel('Entry velocity v₁ (km/s)')
ax_g2.set_ylabel('Exit velocity v₂ (km/s)')
ax_g2.set_title('v₂ vs v₁ (Jupiter)')
ax_g2.grid(True, alpha=0.3)

# Graph 3
v1_values = [5, 10, 15, 20, 25]
colors = plt.cm.viridis(np.linspace(0, 1, len(v1_values)))
for v1_i, c in zip(v1_values, colors):
    ax_g3.plot(theta_grid, compute_v2(v1_i, theta_grid, u), lw=2, color=c, label=f'v₁ = {v1_i:.0f} km/s')
ax_g3.set_xlabel('Deflection angle θ (deg)')
ax_g3.set_ylabel('Exit velocity v₂ (km/s)')
ax_g3.set_title('v₂ vs θ for different v₁ (Jupiter)')
ax_g3.legend(fontsize=8)
ax_g3.grid(True, alpha=0.3)

# Equation label
pos = ax_main.get_position()
eq_text = fig.text(
    pos.x0 + 0.005, pos.y0 + 0.025,
    r"$v_2=(v_1+2U)\,\sqrt{\,1-\dfrac{4\,U\,v_1\,(1-\cos\theta)}{(v_1+2U)^2}\,}$",
    ha='left', va='bottom', fontsize=16, color='black',
    bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.9, edgecolor='none')
)

# Dynamic placeholders
U_arrow = None; U_label = None; graphics = []; ax_inset = None

# ---------------- Update ----------------
def update(val):
    global U_arrow, U_label, graphics, ax_inset
    for g in graphics: g.remove()
    graphics = []
    if U_arrow is not None: U_arrow.remove()
    if U_label is not None: U_label.remove()
    if ax_inset is not None:
        try: ax_inset.remove()
        except Exception: pass
        ax_inset = None

    theta = slider_theta.val
    v1_mag = slider_v1.val
    v2_mag = compute_v2(v1_mag, theta, u)

    # Trajectory
    x, y = trajectory(theta)
    traj_line.set_data(x, y)
    idx_min = np.argmin(np.hypot(x, y))
    idx_v1 = max(0, idx_min - 420)
    idx_v2 = min(len(x)-1, idx_min + 300)

    dx, dy = np.gradient(x), np.gradient(y)
    def tangent(ix):
        t = np.array([dx[ix], dy[ix]])
        return t / norm(t)

    t1, t2 = tangent(idx_v1), tangent(idx_v2)
    if (t2[0] - t1[0]) <= 0:
        x = -x; dx = -dx
        t1, t2 = tangent(idx_v1), tangent(idx_v2)
    traj_line.set_data(x, y)
    p1 = np.array([x[idx_v1], y[idx_v1]])
    p2 = np.array([x[idx_v2], y[idx_v2]])

    # Arrows
    scale_v, head_w, head_l = 3.0, 0.28, 0.4
    a1 = ax_main.arrow(p1[0], p1[1], scale_v*t1[0], scale_v*t1[1],
                       head_width=head_w, head_length=head_l,
                       fc='#1E90FF', ec='#1E90FF', lw=2.5,
                       length_includes_head=True, zorder=20)
    a2 = ax_main.arrow(p2[0], p2[1], scale_v*t2[0], scale_v*t2[1],
                       head_width=head_w, head_length=head_l,
                       fc='#FF4040', ec='#FF4040', lw=2.5,
                       length_includes_head=True, zorder=20)
    graphics += [a1, a2]

    # Labels
    n1 = outward_normal(p1, t1); n2 = outward_normal(p2, t2)
    graphics += [
        ax_main.text(p1[0] + 0.55*t1[0] + 0.55*n1[0],
                     p1[1] + 0.55*t1[1] + 0.55*n1[1],
                     "v₁", fontsize=12, weight='bold', color='#1E90FF'),
        ax_main.text(p2[0] + 0.55*t2[0] + 0.55*n2[0],
                     p2[1] + 0.55*t2[1] + 0.55*n2[1],
                     "v₂", fontsize=12, weight='bold', color='#FF4040')
    ]

    # Planet velocity U from center
    U_dir = (-t1 + t2) / norm(-t1 + t2)
    L = 0.15 * u
    x0, y0 = 0.0, 0.0
    U_arrow = ax_main.arrow(x0, y0, L*U_dir[0], L*U_dir[1],
                            head_width=0.23, head_length=0.35,
                            fc='green', ec='green', lw=2.5,
                            length_includes_head=True, zorder=25)
    label_pos = np.array([x0 + L*U_dir[0], y0 + L*U_dir[1]]) + np.array([0.25, 0.15]) * U_dir
    U_label = ax_main.text(label_pos[0], label_pos[1],
                           f"U = {u:.1f} km/s (Jupiter)",
                           fontsize=11, weight='bold', color='green',
                           ha='left', va='bottom')

    # Angle inset BELOW the v2 text
    ax_inset = inset_axes(
        ax_main, width="14%", height="14%", loc="center",
        bbox_to_anchor=(V2_LABEL_POS[0], V2_LABEL_POS[1] - ANGLE_OFFSET, 0, 0),
        bbox_transform=ax_main.transData, borderpad=0
    )
    ax_inset.set_xlim(-1, 1); ax_inset.set_ylim(-1, 1)
    ax_inset.axis('off'); ax_inset.set_aspect('equal')
    rot = np.degrees(np.arctan2(t1[1], t1[0])); v_len = 0.8
    ax_inset.arrow(0, 0, v_len*np.cos(np.deg2rad(rot)),
                   v_len*np.sin(np.deg2rad(rot)),
                   head_width=0.07, head_length=0.1, fc='#1E90FF', ec='#1E90FF', lw=2.2)
    ax_inset.arrow(0, 0, v_len*np.cos(np.deg2rad(rot - theta)),
                   v_len*np.sin(np.deg2rad(rot - theta)),
                   head_width=0.07, head_length=0.1, fc='#FF4040', ec='#FF4040', lw=2.2)
    arc = Arc((0,0), 1.0, 1.0, angle=0, theta1=rot - theta, theta2=rot, lw=2, color='0.3')
    ax_inset.add_patch(arc)
    ax_inset.text(0.25*np.cos(np.deg2rad(rot - theta/2)),
                  0.25*np.sin(np.deg2rad(rot - theta/2)),
                  f"θ = {theta:.0f}°", fontsize=10, weight='bold', color='0.3')

    # Update left graphs
    y1 = compute_v2(v1_mag, theta_grid, u)
    curve_g1.set_data(theta_grid, y1)
    pt_g1.set_data([theta], [v2_mag]); ax_g1.set_ylim(np.min(y1)-1, np.max(y1)+1)

    y2 = compute_v2(v1_grid, theta, u)
    curve_g2.set_data(v1_grid, y2)
    pt_g2.set_data([v1_mag], [v2_mag]); ax_g2.set_ylim(np.min(y2)-1, np.max(y2)+1)

    text_v2.set_text(f"v₂ = {v2_mag:.2f} km/s")
    fig.canvas.draw_idle()
    # --- Clear old mini arrows before drawing new ones ---
    for artist in getattr(ax_main, 'mini_angle_artists', []):
        artist.remove()
    ax_main.mini_angle_artists = []

    # --- Small local mini angle sketch next to θ label ---
    x_text, y_text = V2_LABEL_POS[0]+0.62, V2_LABEL_POS[1] - 1.5 # near θ text; tweak as needed
    size = 0.4  # overall scale of the mini diagram

    # --- Clear old mini arrows before drawing new ones ---
    for artist in getattr(ax_main, 'mini_angle_artists', []):
        artist.remove()
    ax_main.mini_angle_artists = []

    # Create new arrows and arc once
    # mini schematic aligned with real trajectory
    rot = np.degrees(np.arctan2(t1[1], t1[0]))  # actual v1 direction
    blue_arrow = ax_main.arrow(x_text, y_text,
                            size*np.cos(np.deg2rad(rot)),
                            size*np.sin(np.deg2rad(rot)),
                            head_width=0.05, head_length=0.08,
                            fc='#1E90FF', ec='#1E90FF', lw=2)
    red_arrow = ax_main.arrow(x_text, y_text,
                            size*np.cos(np.deg2rad(rot - theta)),
                            size*np.sin(np.deg2rad(rot - theta)),
                            head_width=0.05, head_length=0.08,
                            fc='#FF4040', ec='#FF4040', lw=2)

    # gray arc between them (aligned to same reference)
    arc_theta = Arc((x_text, y_text), 0.7*size, 0.7*size, angle=rot,
                    theta1=-theta, theta2=0, lw=1.5, color='0.3')

    ax_main.add_patch(arc_theta)

    # Store to clear next time
    ax_main.mini_angle_artists = [blue_arrow, red_arrow, arc_theta]

# ---------------- Export CSV button ----------------
btn_ax = fig.add_axes([0.3, 0.525, 0.08, 0.05])  # bottom-right
export_btn = Button(btn_ax, 'Export CSV', color='#eeeeee', hovercolor='#dddddd')

def on_export(event):
    # recompute using current sliders
    v1_current = slider_v1.val
    theta_current = slider_theta.val

    # High-resolution sampling for export only
    theta_export = np.linspace(0, slider_theta.valmax, 5000)
    v1_export    = np.linspace(0, slider_v1.valmax, 5000)


    v2_theta = compute_v2(v1_current, theta_export, u)   # v2 vs theta
    v2_v1    = compute_v2(v1_export, theta_current, u)   # v2 vs v1

    data1 = np.column_stack([theta_export, v2_theta])
    data2 = np.column_stack([v1_export,    v2_v1])


    np.savetxt('v2_vs_theta.csv', data1, delimiter=',', fmt='%.6f',
               header='theta_deg,v2_km_s', comments='')
    np.savetxt('v2_vs_v1.csv', data2, delimiter=',', fmt='%.6f',
               header='v1_km_s,v2_km_s', comments='')

    print('Saved: v2_vs_theta.csv and v2_vs_v1.csv')

export_btn.on_clicked(on_export)

# Connect sliders & run
slider_theta.on_changed(update)
slider_v1.on_changed(update)
update(None)
plt.show()
