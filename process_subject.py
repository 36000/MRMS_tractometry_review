import os
from AFQ.api.participant import ParticipantAFQ
from dipy.data import fetch_hbn


cwd = os.getcwd()
reco_path = cwd + "/hbn_bids/HBN/derivatives/reco/sub-NDARAV554TP2/"
os.makedirs(reco_path, exist_ok=True)
afq_path = cwd + "/hbn_bids/HBN/derivatives/afq/sub-NDARAV554TP2/"
os.makedirs(afq_path, exist_ok=True)
qsi_dwi_path = cwd + "/hbn_bids/HBN/derivatives/qsiprep/sub-NDARAV554TP2/ses-HBNsiteRU/dwi/"

fetch_hbn(["NDARAV554TP2"], path=cwd + "/hbn_bids")

qsi_base_path = qsi_dwi_path + "sub-NDARAV554TP2_ses-HBNsiteRU_acq-64dir_space-T1w_desc-preproc_dwi"

myafq = ParticipantAFQ(
    qsi_base_path + ".nii.gz",
    qsi_base_path + ".bval",
    qsi_base_path + ".bvec",
    afq_path,
    tracking_paras={"n_seeds": 2},
    segmentation_params={
        "save_intermediates": cwd + "/afq_sls/",
        "prob_threshold": 0.10,
        "parallel_segmentation": {"engine": "serial"}})
#myafq.cmd_outputs(cmd="rm", dependent_on="recog")
myafq.export_all()

# copy results into reco folder, then clear everything
# dependent on bundle recognition
myafq.cmd_outputs(cmd="cp", suffix=reco_path)
myafq = ParticipantAFQ(
    qsi_base_path + ".nii.gz",
    qsi_base_path + ".bval",
    qsi_base_path + ".bvec",
    reco_path,
    tracking_paras={"n_seeds": 2},
    segmentation_params={
        "seg_algo": "reco80",
        "save_intermediates": cwd + "/reco_models/",
        "parallel_segmentation": {"engine": "serial"}})
myafq.cmd_outputs(cmd="rm", dependent_on="recog")
myafq.export_all()

