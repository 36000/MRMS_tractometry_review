# Tractometry of the human visual white matter pathways in health and disease, Figures

This repository contains code for reproducing some of the figures in "Tractometry of the human visual white matter pathways in health and disease" by Takemura et. al.


All code is in python and uses pip-installable packages. 


Figure 2, demonstrating the process of tractometry, is based on publically available data from an HBN subject. It can be processed using process_subject.py and the figure can be made with figure2.py .

The figure containing ROIs and streamlines for all the visual white matter tracts discussed is from an HCP subject. The streamlines and ROIs are available here:

https://figshare.com/articles/dataset/Visual_White_Matter_bundles_and_ROIs_in_HCP_subject_100206_from_Tractometry_of_the_human_visual_white_matter_pathways_in_health_and_disease_/25526845

Its T1 must be obtained to plot the background, but simply remove that code if you don't have access to HCP. The code to find these tracts is also available in `process_hcp_subject.py`.
