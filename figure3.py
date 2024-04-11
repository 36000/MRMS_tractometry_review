import numpy as np
from fury import actor, window
import numpy as np
from dipy.io.streamline import load_trk
import nibabel as nib
import os
from AFQ.viz.utils import PanelFigure
from AFQ.viz.fury_backend import single_bundle_viz
from AFQ.utils.streamlines import SegmentedSFT
import pandas as pd
import altair as alt
from PIL import Image, ImageDraw
import math

cwd = os.getcwd()
prof = pd.read_csv(cwd + "/hbn_bids/HBN/derivatives/afq/sub-NDARAV554TP2/sub-NDARAV554TP2_ses-HBNsiteRU_acq-64dir_coordsys-RASMM_trkmethod-probCSD_recogmethod-AFQ_desc-profiles_dwi.csv")
img = nib.load(cwd + "/hbn_bids/HBN/derivatives/qsiprep/sub-NDARAV554TP2/anat/sub-NDARAV554TP2_desc-preproc_T1w.nii.gz")
data = img.get_fdata()
value_range = (120, 240)
slice_actor = actor.slicer(data, img.affine, value_range, opacity=0.8)
is_slicepoint = int(np.round((data.shape[2] * 8) / 20))
slice_actor.display_extent(
    0, data.shape[0] - 1,
    0, data.shape[1] - 1,
    is_slicepoint, is_slicepoint)

bundle = "Left Optic Radiation"
record_size = (2400, 1800)
scene = window.Scene()
scene.background([1, 1, 1])

def rotate_sagittal(scene):
    # direc = np.fromiter((-0.5, 0, 0), dtype=int)
    # data_shape = np.asarray(img.get_fdata().shape)
    # scene.set_camera(
    #     position=(
    #         -data_shape[0] // 2,
    #         data_shape[0] // 4,
    #         data_shape[0] // 2),
    #     focal_point=direc * data_shape,
    #     view_up=(0, 0, 1))
    # scene.dolly(150)
    return scene


trk = load_trk(
        f"afq_sls/sls_after_Mahalanobis_for_{bundle}.trk",
        "same")
trk.to_rasmm()

b_actor = actor.line(
    trk.streamlines, opacity=1.0)

b_actor.GetProperty().SetRenderLinesAsTubes(1)
b_actor.GetProperty().SetLineWidth(8)
scene.add(b_actor)
scene.add(slice_actor)
scene = rotate_sagittal(scene)
window.record(scene, out_path=f'fig3_0.png', size=record_size)
scene.clear()

seg_sft = SegmentedSFT.fromfile(cwd + "/hbn_bids/HBN/derivatives/afq/sub-NDARAV554TP2/sub-NDARAV554TP2_ses-HBNsiteRU_acq-64dir_coordsys-RASMM_trkmethod-probCSD_recogmethod-AFQ_tractography.trk")
scene = window.Scene()
scene.background([1, 1, 1])
scene.add(slice_actor)
scene = single_bundle_viz(
    prof[prof.tractID=="Left Optic Radiation"].dki_fa.to_numpy(),
    seg_sft,
    bundle, "FA",
    labelled_nodes=[0, -1],
    figure=scene)
scene = rotate_sagittal(scene)
window.record(scene, out_path=f'fig3_1.png', size=record_size)

or_df = prof[prof.tractID=="Left Optic Radiation"]
alt_font_size=32
(
    alt.Chart(or_df).mark_line(opacity=0.3).encode(
        x=alt.X('nodeID', title="Position along tract (A->P)"),
        y=alt.Y('dki_fa', title="Fractional Anisotropy (FA)")) + \
    alt.Chart(or_df).mark_circle(size=100).encode(
        x=alt.X('nodeID', title="Position along tract (A->P)"),
        y=alt.Y('dki_fa', title="Fractional Anisotropy (FA)"),
        color=alt.Color('dki_fa', scale=alt.Scale(scheme="viridis"), legend=None))
).properties(
    width=1000,
    height=500,
).configure(
    font='Helvetica-Bold',
    axis=alt.AxisConfig(
        labelFontSize=alt_font_size,
        titleFontSize=alt_font_size),
    title=alt.TitleConfig(fontSize=alt_font_size)
).save('fig3_2.png')

pf = PanelFigure(2, 2, 6, 6)
pf.add_img(f'fig3_0.png', 0, 0)
pf.add_img(f'fig3_1.png', 1, 0)
pf.add_img(f'fig3_2.png', slice(0, 2, None), 1, panel_label_kwargs=dict(color="black"))
pf.format_and_save_figure(f"fig3.png", trim_final=True)

def draw_arrow(image_path, start, end):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)

        draw.line([start, end], fill="blue", width=10)

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)

        arrow_head_length = 40
        angle_offset = math.pi / 6  # 30 degrees for each side of the head

        right_x = end[0] - arrow_head_length * math.cos(angle - angle_offset)
        right_y = end[1] - arrow_head_length * math.sin(angle - angle_offset)

        left_x = end[0] - arrow_head_length * math.cos(angle + angle_offset)
        left_y = end[1] - arrow_head_length * math.sin(angle + angle_offset)

        draw.polygon([end, (right_x, right_y), (left_x, left_y)], fill="blue")

        img.save(image_path)

draw_arrow("fig3.png", (1146, 642), (1188, 879))
draw_arrow("fig3.png", (1113, 567), (924, 870))
