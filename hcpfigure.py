import os
import os.path as op
import nibabel as nib
from fury import actor, window
import numpy as np
from dipy.io.streamline import load_trk
from AFQ.viz.utils import tableau_20, PanelFigure

record_size = (2400, 1800)

roi_colors_dict = {
    "start": [0, 1, 0],
    "end": [0, 1, 0],
    "include": [0, 0, 1],
}

background_opacity = 0.6
sl_opacity = 1.0
roi_opacity = 0.2

cwd = os.getcwd()
img = nib.load(cwd + "/hcp_bundles_rois/sub-100206_T1w.nii.gz")
data = img.get_fdata()
value_range = (0, 2000)
def get_slice_actor(slice_loc):
    slice_actor = actor.slicer(data, img.affine, value_range, opacity=background_opacity)
    is_slicepoint = int(np.round((data.shape[2] * slice_loc) / 10))
    slice_actor.display_extent(
        0, data.shape[0] - 1,
        0, data.shape[1] - 1,
        is_slicepoint, is_slicepoint)
    return slice_actor

slice_locs = [2, 3, 4, 3, 5, 0]

bundle_names = [
    "LeftOpticNerve", "RightOpticNerve",
    "LeftOpticTract", "RightOpticTract",
    "LeftOpticRadiation", "RightOpticRadiation",
    "LeftVerticalOccipital", "RightVerticalOccipital",
    "ForcepsMajor"]

def rotate_sagittal(scene):
    direc = np.fromiter((-0.5, 0, 0), dtype=int)
    data_shape = np.asarray(img.get_fdata().shape)
    scene.set_camera(
        position=(
            data_shape[0] // 2,
            data_shape[0] // 4,
            data_shape[0] // 2),
        focal_point=direc * data_shape,
        view_up=(0, 0, 1))
    scene.dolly(150)
    return scene

mega_scene = window.Scene()
mega_scene.background([1, 1, 1])
mega_scene.add(get_slice_actor(4))
scene = window.Scene()
scene.background([1, 1, 1])
scene.add(get_slice_actor(slice_locs[0]))
fc = 0
for ii, bundle in enumerate(bundle_names):
    trk = load_trk(
            (f"hcp_bundles_rois/bundles/sub-100206_coordsys-RASMM_trkmethod-probCSD_"
                f"recogmethod-AFQ_desc-{bundle}_tractography.trk"),
            "same")
    trk.to_rasmm()
    rois = []
    roi_colors = []
    for step in ["start", "end", "include"]:
        for kk in range(0, 4):
            roi_fname = (
                f"hcp_bundles_rois/ROIs/sub-100206_space-subject_"
                f"desc-{bundle}{step}{kk}_mask.nii.gz")
            if op.exists(roi_fname):
                roi = nib.load(roi_fname)
                rois.append(roi)
                roi_colors.append(step)
            else:
                break
    b_actor = actor.line(
        trk.streamlines, opacity=sl_opacity, colors=tableau_20[ii])
    for roi, roi_color in zip(rois, roi_colors):
        roi_actor = actor.contour_from_roi(
            roi.get_fdata(), roi.affine,
            roi_colors_dict[roi_color], roi_opacity)
        scene.add(roi_actor)
    b_actor.GetProperty().SetRenderLinesAsTubes(1)
    b_actor.GetProperty().SetLineWidth(8)
    scene.add(b_actor)
    mega_scene.add(b_actor)
    if "Left" not in bundle:
        window.record(scene, out_path=f'hcp_figure_{fc}_0.png', size=record_size)
        window.record(rotate_sagittal(scene), out_path=f'hcp_figure_{fc}_1.png', size=record_size)
        scene.clear()
        fc += 1
        scene = window.Scene()
        scene.background([1, 1, 1])
        scene.add(get_slice_actor(slice_locs[fc]))
window.record(mega_scene, out_path=f'hcp_mega_figure_0.png', size=record_size)
window.record(
    rotate_sagittal(mega_scene), out_path=f'hcp_mega_figure_1.png',
    size=record_size)
mega_scene.clear()
scene.clear()

pf_panel_label_kwargs = dict(
    fontfamily="Helvetica-Bold",
    fontsize="xx-large",
    color="black",
    fontweight='bold',
    # fontstyle="normal",
    bbox=dict(
        facecolor='white',
        edgecolor='none'))
pf = PanelFigure(3, 4, 12, 9, pf_panel_label_kwargs)
for jj in range(2):
    for ii in [0, 2, 4, 1, 3]:
        pf.add_img(f'hcp_figure_{ii}_{jj}.png', ii%2+jj*2, ii//2)
    pf.add_img(f'hcp_mega_figure_{jj}.png', 1+2*jj, 2)
# pf.fig.set_facecolor((0.4, 0.4, 0.4))
pf.format_and_save_figure(f"hcp_fig.png", trim_final=True)
