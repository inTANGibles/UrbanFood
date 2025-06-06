import os
import copy

import matplotlib.pyplot as plt
import matplotlib.cm as cm


import numpy as np
import pandas as pd

from datetime import datetime


# def correlationAnalysis(beardata, jsonfile_name, objectFilename, figureDir, featureExclusionList, valid=True, overwrite=False, correlationHeatmapType='fixation duration', 
#     fixationFilename=None, objectiveTimeFilename=None):

def correlationAnalysis(inputfilename, figureDir):
    ########### correlation analysis Figure 3.1 correlation heatmap ###########
    # refer to 5 CorrelationAnalysisVisualization
    # generating correlation matrices
    # all features
    print(f"[{datetime.now()}] INFO: Generating correlation matrix heatmap for all features...")
    # mata = dfa.corr()
    mata = pd.read_csv(inputfilename, index_col=0)



    # create a color map
    cmap = cm.colors.LinearSegmentedColormap.from_list("", ["blue", "white", "red"])

    # Create a heatmap
    plt.figure(figsize=(12, 10), dpi=1200)  # Increase figure size
    corrl = copy.deepcopy(mata)
    corrl.values[np.triu_indices(len(mata))] = 0

    plt.imshow(corrl, cmap=cmap, interpolation='nearest', vmin=-1, vmax=1)
    
    # Create a color bar
    cbar = plt.colorbar()
    cbar.set_ticks([-1, -0.5, -0.3, -0.1, 0, 0.1, 0.3, 0.5, 1])

    # Set tick font size
    cbar.ax.tick_params(axis='y', labelsize=10)

    # Remove the boundary of the color bar
    cbar.outline.set_visible(False)

    # Write text on the color bar
    cbar.ax.text(0.5, 0.75, "***", ha="center", va="center", fontsize=15)
    cbar.ax.text(0.5, 0.4, "**", ha="center", va="center", fontsize=15)
    cbar.ax.text(0.5, 0.2, "*", ha="center", va="center", fontsize=15)
    cbar.ax.text(0.5, -0.2, "*", ha="center", va="center", fontsize=15)
    cbar.ax.text(0.5, -0.4, "**", ha="center", va="center", fontsize=15)
    cbar.ax.text(0.5, -0.75, "***", ha="center", va="center", fontsize=15)

    cbar.ax.tick_params(axis='y', length=0)  # Remove short tick bars

    # Add label values to the heatmap
    h, w = mata.values.shape

    if h > 15:
        mapFontSize = 8
    else:
        mapFontSize = 10

    # define correlation coefficient group threshold
    threshold = [0.1, 0.3, 0.5, 1]

    for i in range(h):
        for j in range(i + 1, w):
            # i, j represents the upper triangle
            alpha = abs(mata.values[i, j])
            color = cmap((mata.values[i, j] + 1) / 2)
            if abs(mata.values[i, j]) > threshold[0]:
                # top-right triangle, show value with different transparency
                plt.text(j, i, f"{mata.values[i, j]:.2f}", ha="center", va="center", color=(color[0], color[1], color[2], alpha), fontsize=mapFontSize)
                # lower-left triangle, show different number of asterials with corresponding groups
                for k in range(len(threshold)):
                    index = len(threshold) - 1 - k
                    if abs(mata.values[i, j]) >= threshold[index]:
                        plt.text(i, j, '*' * (index + 1), ha="center", va="center", color=(0, 0, 0, alpha), fontsize=mapFontSize)
                        break

    # Set x and y ticks to feature names
    plt.xticks(range(w), mata.columns, rotation=90)
    plt.yticks(range(h), mata.columns)

    # Remove the black boundary around the heatmap
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    
    plt.tight_layout()

    outputfilename = os.path.join(figureDir, 'Figure Correlation matrix heatmap.png')
    plt.savefig(outputfilename, dpi=1200)
    plt.close()
    print(f"[{datetime.now()}] INFO: Save {outputfilename}!")






# 输入文件名，只能是csv文件，excel要另存为csv
inputfilename = r'G:\CODE\UrbanFood\correlation_matrix.csv'

# 图像存储的路径
figureDir=r'G:\CODE\UrbanFood\processing_data'

correlationAnalysis(inputfilename, figureDir)
