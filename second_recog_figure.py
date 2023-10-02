from fury import actor, window
import numpy as np
from dipy.io.streamline import load_trk
from PIL import Image, ImageChops
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
import nibabel as nib
from dipy.align import resample
import os

cwd = os.getcwd()

def bbox(img):
    img = np.sum(img, axis=-1)
    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    return cmin, rmin, cmax, rmax

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    #diff = ImageChops.add(diff, diff, 2.0, -100)
    this_bbox = bbox(diff)
    if this_bbox:
        return im.crop(this_bbox)

def add_img(x_coord, y_coord, fname, reduct_count=2, subplot_label_ypos=1.0, legend=None, legend_kwargs={}, add_panel_label=True):
    global subplot_count
    ax = fig.add_subplot(grid[y_coord, x_coord])
    im1 = Image.open(fname)
    for _ in range(reduct_count):
        im1 = trim(im1)
    if legend is not None:
        patches = []
        for value, color in legend.items():
            patches.append(mpatches.Patch(
                color=color,
                label=value))
        ax.legend(handles=patches, borderaxespad=0., **legend_kwargs)
    if add_panel_label:
        trans = mtransforms.ScaledTranslation(10/72, -5/72, fig.dpi_scale_trans)
        ax.text(0.1, subplot_label_ypos, f"{chr(65+subplot_count)})", transform=ax.transAxes + trans,
                fontsize='medium', verticalalignment="top", fontfamily='serif',
                bbox=dict(facecolor='0.7', edgecolor='none', pad=3.0))
    ax.imshow(np.asarray(im1), aspect=1)
    ax.axis('off')
    subplot_count = subplot_count + 1
    return ax

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
            roi_actor0 = actor.contour_from_roi(
                roi0_resampled, img.affine, [1, 0, 0], 0.5)
            b_actor = actor.line(
                trk.streamlines, opacity=0)
            scene.add(roi_actor0)
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

fig = plt.figure(figsize=(6, 9))
grid = plt.GridSpec(3, 2, hspace=0, wspace=0)
subplot_count = 0
for ii in range(len(steps)):
    add_img(ii%2, ii//2, f'b_figure_{ii}.png')
fname = f"{bundle}_fig.png"
fig.tight_layout()
fig.savefig(fname)
im1 = Image.open(fname)
im1 = trim(im1)
im1.save(fname)

rb_bundles = {"IFOF_L": 2, "CNII_L": 1}
slice_actor = actor.slicer(data, img.affine, value_range, opacity=0.8)
for jj, (bname, slice_frac) in enumerate(rb_bundles.items()):
    scene = window.Scene()
    scene.background([1, 1, 1])
    model_trk = load_trk(
            f"reco_models/{bname}_model.trk",
            "same")
    b_actor = actor.line(
        model_trk.streamlines, [0, 0, 1], opacity=0.2)
    b_actor.GetProperty().SetRenderLinesAsTubes(1)
    b_actor.GetProperty().SetLineWidth(8)
    scene.add(b_actor)
    actual_trk = load_trk(
            cwd + f"/hbn_bids/HBN/derivatives/reco/sub-NDARAV554TP2/bundles/sub-NDARAV554TP2_ses-HBNsiteRU_acq-64dir_space-T1w_desc-preproc_dwi_space-RASMM_model-probCSD_algo-reco80_desc-{bname.replace('_','')}_tractography.trk",
            "same")
    b_actor = actor.line(
        actual_trk.streamlines, opacity=1.0)
    b_actor.GetProperty().SetRenderLinesAsTubes(1)
    b_actor.GetProperty().SetLineWidth(10)
    scene.add(b_actor)
    is_slicepoint = int(np.round((data.shape[2] * slice_frac) / 5))
    slice_actor.display_extent(
        0, data.shape[0] - 1,
        0, data.shape[1] - 1,
        is_slicepoint, is_slicepoint)
    scene.add(slice_actor)
    window.record(scene, out_path=f'rb_figure_{jj}.png', size=record_size)
    scene.clear()

fig = plt.figure(figsize=(6, 3))
grid = plt.GridSpec(1, 2, hspace=0, wspace=0)
subplot_count = 0
add_img(0, 0, f'rb_figure_0.png')
add_img(1, 0, f'rb_figure_1.png')
fname = f"rb_fig.png"
fig.tight_layout()
fig.savefig(fname)
im1 = Image.open(fname)
im1 = trim(im1)
im1.save(fname)
