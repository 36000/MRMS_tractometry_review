from fury import actor, window
from fury.actor import colormap_lookup_table
import numpy as np
from dipy.io.streamline import load_trk
import nibabel as nib
from dipy.align import resample
import os
from AFQ.viz.utils import PanelFigure

cwd = os.getcwd()

img = nib.load(cwd + "/hbn_bids/HBN/derivatives/qsiprep/sub-NDARAV554TP2/anat/sub-NDARAV554TP2_desc-preproc_T1w.nii.gz")
data = img.get_fdata()
value_range = (120, 240)
slice_actor = actor.slicer(data, img.affine, value_range, opacity=0.8)
is_slicepoint = int(np.round((data.shape[2] * 2) / 5))
slice_actor.display_extent(
    0, data.shape[0] - 1,
    0, data.shape[1] - 1,
    is_slicepoint, is_slicepoint)

bundle = "IFO_L"
record_size = (2400, 1800)

steps = {
    "Prob. Map": "prob_map",  
    "Cross Mid.": "",
    "startpoint": "start",
    "endpoint": "end",
    "include": "include",
    "Mahalanobis": ""
}

roi_folder = cwd + "/hbn_bids/HBN/derivatives/afq/sub-NDARAV554TP2/ROIs/"
for ii, step in enumerate(steps.keys()):
    scene = window.Scene()
    scene.background([1, 1, 1])
    trk = load_trk(
            f"afq_sls/sls_after_{step}_for_{bundle}.trk",
            "same")
    trk.to_rasmm()

    if step not in ["Mahalanobis", "Cross Mid."]:
        roi0 = nib.load(f"{roi_folder}sub-NDARAV554TP2_ses-HBNsiteRU_acq-64dir_space-T1w_desc-preproc_dwi_space-subject_desc-{bundle.replace('_', '')}{steps[step]}0_mask.nii.gz")

        if step == "Prob. Map":
            roi0_resampled = resample(
                roi0.get_fdata(),
                data,
                roi0.affine,
                img.affine).get_fdata()
            roi0_resampled[:, :, :is_slicepoint] = 0
            roi0_resampled[:, :, is_slicepoint+1:] = 0
            # roi_actor0 = actor.contour_from_roi(
            #     roi0_resampled, img.affine, [1, 0, 0], 0.5)
            lut_args = dict(scale_range=(0, 1),
                            hue_range=(1, 0),
                            saturation_range=(0, 1),
                            value_range=(0.35, 1))
            slice_actor_roi = actor.slicer(
                roi0_resampled, img.affine,
                lookup_colormap=colormap_lookup_table(**lut_args), opacity=0.5)
            slice_actor_roi.display_extent(
                0, data.shape[0] - 1,
                0, data.shape[1] - 1,
                is_slicepoint, is_slicepoint)
            b_actor = actor.line(
                trk.streamlines, opacity=0)
            scene.add(slice_actor_roi)
        else:
            b_actor = actor.line(
                trk.streamlines, opacity=1.0)
            roi_actor0 = actor.contour_from_roi(
                roi0.get_fdata(), roi0.affine, [0, 0, 1], 1.0)
            scene.add(roi_actor0)
        if step == "include":
            roi1 = nib.load(f"{roi_folder}sub-NDARAV554TP2_ses-HBNsiteRU_acq-64dir_space-T1w_desc-preproc_dwi_space-subject_desc-{bundle.replace('_', '')}{steps[step]}1_mask.nii.gz")
            roi_actor1 = actor.contour_from_roi(
                roi1.get_fdata(), roi0.affine, [0, 0, 1], 0.7)
            scene.add(roi_actor1)
    else:
        b_actor = actor.line(
            trk.streamlines, opacity=1.0)
        if step == "Cross Mid.":
            roi_shape = roi0.get_fdata().shape
            midline = actor.rectangle(
                nib.affines.apply_affine(
                    roi0.affine,
                    np.asarray([[roi_shape[0]//2, roi_shape[1]//2, roi_shape[2]//2+20]])),
                directions=(1, 0, 0),
                colors=(1, 0, 0),
                scales=(1, 160, 1))
            scene.add(midline)

    b_actor.GetProperty().SetRenderLinesAsTubes(1)
    b_actor.GetProperty().SetLineWidth(8)
    scene.add(b_actor)
    scene.add(slice_actor)
    window.record(scene, out_path=f'b_figure_{ii}.png', size=record_size)
    scene.clear()

pf_panel_label_kwargs = dict(
    fontfamily="Helvetica-Bold",
    fontsize="xx-large",
    color="white",
    fontweight='bold',
    # fontstyle="normal",
    bbox=dict(
        facecolor='none',
        edgecolor='none'))
pf = PanelFigure(3, 2, 6, 9, pf_panel_label_kwargs)
for ii in range(len(steps)):
    pf.add_img(f'b_figure_{ii}.png', ii%2, ii//2)
pf.format_and_save_figure(f"{bundle}_fig.png", trim_final=True)
