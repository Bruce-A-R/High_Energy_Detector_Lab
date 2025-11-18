python
! git clone https://github.com/Bruce-A-R/High_Energy_Detector_Lab.git

import numpy as np
import matplotlib.pyplot as plt

filepath = "/content/High_Energy_Detector_Lab/BGO_detector/Co BGO.Spe"# change this for the particular file you want to scan
detector = "BGO"
regions = [(500, 575), (100, 300)]    # change these co-ordinates for each file

lines = open(filepath, "r", errors="ignore").read().splitlines()

start = 0
for i, line in enumerate(lines):
    if "DATA" in line.upper():
        start = i + 1
        break

counts = []
for line in lines[start:]:
    try:
        counts.append(float(line.strip()))
    except:
        pass

counts = np.array(counts)

# find peaks in regions (max value)
peaks = []
for low, high in regions:
    if high < len(counts):
        roi = counts[low:high+1]
        if len(roi) > 0:
            peak = low + int(np.argmax(roi))
            peaks.append(peak)

plt.plot(counts) # plot with red lines
for p in peaks:
    plt.axvline(p, color="red")
plt.title(f"{detector} - {filepath}")
plt.xlabel("Channel")
plt.ylabel("Counts")
plt.show()

with open("peaks_output.txt", "a") as f: # save to a text file
    f.write("Detector: " + detector + "\n")
    f.write("File: " + filepath + "\n")
    f.write("Regions: " + str(regions) + "\n")
    f.write("Peaks: " + str(peaks) + "\n\n")

print("Peaks found:", peaks)
print("Saved to peaks_output.txt")
