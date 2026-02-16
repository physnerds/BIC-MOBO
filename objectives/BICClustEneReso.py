#!/usr/bin/env python3
# =============================================================================
## @file   BICClustEneReso.py
#  @author Derek Anderson
#  @date   08.28.2025
# -----------------------------------------------------------------------------
## @brief Script to compute energy resolution for a
#    specified particle species from BIC clusters.
#
#  Usage if executed directly:
#    ./BICClustEneReso.py \
#        -i <input file> \
#        -o <output file> \
#        -p <pdg code> \
#        -b <branch> (optional)
# =============================================================================

import argparse as ap
import numpy as np
import ROOT
import sys

from podio.reading import get_reader

# default arguments
IFileDefault  = "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.07.0/epic_craterlake/SINGLE/e-/5GeV/45to135deg/e-_5GeV_45to135deg.0099.eicrecon.edm4eic.root"
OFileDefault  = "test_reso.root"
PDGDefault    = 11
BranchDefault = "EcalBarrelClusterAssociations"


def CalculateClustEneReso(
    ifile  = IFileDefault,
    ofile  = OFileDefault,
    pdg    = PDGDefault,
    branch = BranchDefault
):
    """CalculateEneReso

    A function to calculate energy resolution for a 
    specified species of particle from BIC clusters.

    Args:
      ifile:  input file name
      ofile:  output file name
      pdg:    PDG code of particle species
      branch: EICrecon branch to analyze
    Returns:
      calculated resolution
    """

    # set up histograms, etc. -------------------------------------------------

    # create histogram from extracting resolution
    hres = ROOT.TH1D("hEneRes", ";(E_{clust} - E_{par}) / E_{par}", 50, -2., 3.)
    hres.Sumw2()

    # event loop --------------------------------------------------------------

    # loop through all events
    reader = get_reader(ifile)
    for iframe, frame in enumerate(reader.get("events")):

        # grab truth-cluster associations from frame
        assocs = frame.get(branch)

        # now hunt down clusters associated with electron
        for assoc in assocs:

            # associated truth particle should be the 
            # identified species
            if assoc.getSim().getPDG() != pdg:
                continue

            # calculate energy of truth particle
            msim  = assoc.getSim().getMass()
            pxsim = assoc.getSim().getMomentum().x
            pysim = assoc.getSim().getMomentum().y
            pzsim = assoc.getSim().getMomentum().z
            psim2 = pxsim**2 + pysim**2 + pzsim**2
            esim  = np.sqrt(psim2 + msim**2)

            # and now we should be looking at a cluster
            # connected to _the_ primary
            eres = (assoc.getRec().getEnergy() - esim) / esim
            hres.Fill(eres)

    # resolution calculation --------------------------------------------------

    # fit spectrum with a gaussian to extract peak 
    fres = ROOT.TF1("fEneRes", "gaus(0)", -0.5, 0.5)
    fres.SetParameter(0, hres.Integral())
    fres.SetParameter(1, hres.GetMean())
    fres.SetParameter(2, hres.GetRMS())
    hres.Fit(fres, "r")

    # wrap up script ----------------------------------------------------------

    # save objects
    with ROOT.TFile(ofile, "recreate") as out:
        out.WriteObject(hres, "hEneRes")
        out.WriteObject(fres, "fEneRes")
        out.Close()

    # grab objective and other info
    reso = fres.GetParameter(2)
    eres = fres.GetParError(2)
    mean = fres.GetParameter(1)
    emea = fres.GetParError(1)

    # write them out to a text file for extraction later
    otext = ofile.replace(".root", ".txt")
    with open(otext, 'w') as out:
        out.write(f"{reso}\n")
        out.write(f"{eres}\n")
        out.write(f"{mean}\n")
        out.write(f"{emea}")

    # and return calculated resolution
    return fres.GetParameter(2)

# main ========================================================================

if __name__ == "__main__":

    # set up argments
    parser = ap.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help = "Input file",
        nargs = '?',
        const = IFileDefault,
        default = IFileDefault,
        type = str
    )
    parser.add_argument(
        "-o",
        "--output",
        help = "Output file",
        nargs = '?',
        const = OFileDefault,
        default = OFileDefault,
        type = str
    )
    parser.add_argument(
        "-p",
        "--pdg",
        help = "PDG code to look for",
        nargs = '?',
        const = PDGDefault,
        default = PDGDefault,
        type = int
    )
    parser.add_argument(
        "-b",
        "--branch",
        help = "Branch to use",
        nargs = '?',
        const = BranchDefault,
        default = BranchDefault,
        type = str
    )

    # grab arguments
    args = parser.parse_args()

    # run analysis
    CalculateEneReso(args.input, args.output, args.pdg)

# end =========================================================================
