import os
from AFQ.api.participant import ParticipantAFQ
from AFQ.definitions.image import GQImage, RoiImage
from AFQ.api.bundle_dict import BundleDict, default18_bd
import AFQ.data.fetch as afd


or_rois = afd.read_or_templates()

# you need to get these from HCP:
dwi_folder = "TODO"
subject_b0 = "TODO"

# you can find the following on figshare:
# https://figshare.com/articles/dataset/Visual_White_Matter_bundles_and_ROIs_in_HCP_subject_100206_from_Tractometry_of_the_human_visual_white_matter_pathways_in_health_and_disease_/25526845
subject_ROC = "TODO"
subject_RON = "TODO"
subject_RTH = "TODO"
subject_LOC = "TODO"
subject_LON = "TODO"
subject_LTH = "TODO"

bundle_info_or = BundleDict({
    "Left Optic Radiation": {
        "include": [
            or_rois["left_OR_1"],
            or_rois["left_OR_2"]],
        "exclude": [
            or_rois["left_OP_MNI"],
            or_rois["left_TP_MNI"],
            or_rois["left_pos_thal_MNI"]],
        "start": or_rois['left_thal_MNI'],
        "end": or_rois['left_V1_MNI'],
        "cross_midline": False,
    },
    "Right Optic Radiation": {
        "include": [
            or_rois["right_OR_1"],
            or_rois["right_OR_2"]],
        "exclude": [
            or_rois["right_OP_MNI"],
            or_rois["right_TP_MNI"],
            or_rois["right_pos_thal_MNI"]],
        "start": or_rois['right_thal_MNI'],
        "end": or_rois['right_V1_MNI'],
        "cross_midline": False,
    }})
bundle_info_ot = BundleDict({
    "Left Optic Tract": {
        "start": subject_LOC,
        "end": subject_LTH,
        "cross_midline": False,
        "space": "subject",
        "mahal": {
            "distance_threshold": 2,
            "length_threshold": 2,
            "clean_rounds": 20,}
    },
    "Right Optic Tract": {
        "start": subject_ROC,
        "end": subject_RTH,
        "cross_midline": False,
        "space": "subject",
        "mahal": {
            "distance_threshold": 2,
            "length_threshold": 2,
            "clean_rounds": 20,}
    },
}, resample_subject_to=subject_b0)

bundle_info_on = BundleDict({
    "Left Optic Nerve": {
        "start": subject_LON,
        "end": subject_LOC,
        "cross_midline": False,
        "space": "subject",
        "min_len": 20,
        "max_len": 40,
        "mahal": {
            "distance_threshold": 2,
            "length_threshold": 2,
            "clean_rounds": 20,}
    },
    "Right Optic Nerve": {
        "start": subject_RON,
        "end": subject_ROC,
        "cross_midline": False,
        "space": "subject",
        "min_len": 20,
        "max_len": 40,
        "mahal": {
            "distance_threshold": 2,
            "length_threshold": 2,
            "clean_rounds": 20,}
    }}, resample_subject_to=subject_b0)


os.makedirs("hcp_100206_afq_or", exist_ok=True)
myafq = ParticipantAFQ(
    dwi_folder + "sub-100206_dwi.nii.gz",
    dwi_folder + "sub-100206_dwi.bval",
    dwi_folder + "sub-100206_dwi.bvec",
    "hcp_100206_afq_or",
    bundle_info = bundle_info_or,
    tracking_params={"n_seeds": 4,
                    "directions": "prob",
                    "odf_model": "CSD",
                    "seed_mask": RoiImage(use_endpoints=True)},
)
myafq.export_all()
os.makedirs("hcp_100206_afq_ot", exist_ok=True)
myafq.cmd_outputs("cp", suffix="hcp_100206_afq_ot/")

myafq = ParticipantAFQ(
    dwi_folder + "sub-100206_dwi.nii.gz",
    dwi_folder + "sub-100206_dwi.bval",
    dwi_folder + "sub-100206_dwi.bvec",
    "hcp_100206_afq_ot",
    bundle_info = bundle_info_ot,
    tracking_params={"n_seeds": 4,
                    "directions": "prob",
                    "odf_model": "CSD",
                    "seed_mask": RoiImage(use_endpoints=True)},
)
myafq.clobber(dependent_on="track")
myafq.export_all()
os.makedirs("hcp_100206_afq_on", exist_ok=True)
myafq.cmd_outputs("cp", suffix="hcp_100206_afq_on/")

myafq = ParticipantAFQ(
    dwi_folder + "sub-100206_dwi.nii.gz",
    dwi_folder + "sub-100206_dwi.bval",
    dwi_folder + "sub-100206_dwi.bvec",
    "hcp_100206_afq_on",
    brain_mask_definition = GQImage(),
    bundle_info = bundle_info_on,
    tracking_params={"n_seeds": 6,
                    "directions": "prob",
                    "odf_model": "CSD",
                    "minlen": 5,
                    "max_angle": 60,
                    "seed_mask": RoiImage(use_endpoints=True),
                    "stop_mask": RoiImage(use_endpoints=True)})
myafq.clobber(dependent_on="recog")
myafq.export_all()
os.makedirs("hcp_100206_afq_other", exist_ok=True)
myafq.cmd_outputs("cp", suffix="hcp_100206_afq_other/")

myafq = ParticipantAFQ(
    dwi_folder + "sub-100206_dwi.nii.gz",
    dwi_folder + "sub-100206_dwi.bval",
    dwi_folder + "sub-100206_dwi.bvec",
    "hcp_100206_afq_other",
    bundle_info = default18_bd()[
        "Forceps Major",
        "Left Vertical Occipital",
        "Right Vertical Occipital"],
    tracking_params={"n_seeds": 2,
                    "directions": "prob",
                    "odf_model": "CSD",
                    "seed_mask": RoiImage(use_endpoints=True)})
myafq.clobber(dependent_on="track")
myafq.export_all()
