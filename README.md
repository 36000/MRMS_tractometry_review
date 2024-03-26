# Tractometry of the human visual white matter pathways in health and disease, Figures

This repository contains code for reproducing some of the figures in "Tractometry of the human visual white matter pathways in health and disease" by Takemura et. al.


All code is in python and uses pip-installable packages. 


Figure 2, demonstrating the process of tractometry, is based on publically available data from an HBN subject. It can be processed using process_subject.py and the figure can be made with figure2.py .


The figure containing ROIs and streamlines for all the visual white matter tracts discussed is from an HCP subject. Its T1 must be obtained to plot the background, but simply remove that code if you don't have access to HCP. Otherwise, it requires ROI and tract information which you can find here: TODO.
