#!/usr/bin/env python3
# =============================================================================
## @file   BICClustAngReso.py
#  @author Derek Anderson
#  @date   12.09.2025
# -----------------------------------------------------------------------------
## @brief Script to compute angular resolutions (in
#    eta, phi, etc.) for a specified particle species
#    from BIC clusters.
#
#  Usage if executed directly:
#    ./BICClustAngReso.py \
#        -i <input file> \
#        -o <output file> \
#        -c <coordinate> \
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
CoordDefault  = "phi"
PDGDefault    = 11
BranchDefault = "EcalBarrelClusterAssociations"


def CalculateClustAngReso(
    ifile  = IFileDefault,
    ofile  = OFileDefault,
    coord  = CoordDefault,
    pdg    = PDGDefault,
    branch = BranchDefault
):
    """CalculateClustAngReso

    A function to calculate angular resolution for a 
    specified species of particle from BIC clusters.

    Args:
      ifile:  input file name
      ofile:  output file name
      coord:  coordinate to calculate resolution on
      pdg:    PDG code of particle species
      branch: EICrecon branch to analyze
    Returns:
      calculated resolution
    """

    # sanitize coordinate input
    coord = coord.lower()

    # set up histograms, etc. -------------------------------------------------

    # set variable for axis accordingly 
    var = "x"
    match coord:
        case "eta":
            var = "#eta"
        case "phi":
            var = "#phi"
        case _:
            raise ValueError("Unknown coordinate specified!")

    # construct axis title
    axis = ";(" + var + "_{clust} - " + var + "_{par}) / " + var + "_{par}"

    # create histogram from extracting resolution
    hres = ROOT.TH1D("hAngRes", axis, 50, -2., 3.)
    hres.Sumw2()

    # event loop --------------------------------------------------------------

    # loop through all events
    reader = get_reader(ifile)
    for iframe, frame in enumerate(reader.get("events")):

        # grab truth-cluster associations
        assocs = frame.get(branch)

        # now hunt down clusters associated with electron
        for assoc in assocs:

            # associated truth particle should be the 
            # identified species
            if assoc.getSim().getPDG() != pdg:
                continue

            # calculate eta/phi of truth particle
            # at the vertex
            psim = ROOT.Math.XYZVector(
                assoc.getSim().getMomentum().x,
                assoc.getSim().getMomentum().y,
                assoc.getSim().getMomentum().z
            )
            asim = np.nan
            match coord:
                case "eta":
                    asim = psim.Eta()
                case "phi":
                    asim = psim.Phi()
                case _:
                    raise ValueError("Unknown coordinate specified!")

            # if sim is _exactly_ 0 somehow, perturb it by epsilon
            if asim == 0.0:
                asim = asim + np.finfo(float).eps

            # since these are single particle events, use the start vertex
            # of the truth particle as the primary vertex
            pvtx = assoc.getSim().getVertex()

            # calculate the position of the cluster wrt to the
            # primary vertex 
            rvtx = ROOT.Math.XYZVector(
                pvtx.x,
                pvtx.y,
                pvtx.z
            )
            rrec = ROOT.Math.XYZVector(
                assoc.getRec().getPosition().x,
                assoc.getRec().getPosition().y,
                assoc.getRec().getPosition().z
            )
            drec = rrec - rvtx

            # next calculate eta/phi of reconstructed cluster 
            arec = np.nan
            match coord:
                case "eta":
                    arec = drec.Eta()
                case "phi":
                    arec = drec.Phi()
                case _:
                    raise ValueError("Unknown coordinate specified!")

            # and now we should be looking at a cluster
            # connected to _the_ primary
            ares = (arec - asim) / asim
            hres.Fill(ares)

    # resolution calculation --------------------------------------------------

    # fit spectrum with a gaussian to extract peak 
    fres = ROOT.TF1("fAngRes", "gaus(0)", -0.5, 0.5)
    fres.SetParameter(0, hres.Integral())
    fres.SetParameter(1, hres.GetMean())
    fres.SetParameter(2, hres.GetRMS())
    hres.Fit(fres, "r")

    # wrap up script ----------------------------------------------------------

    # save objects
    with ROOT.TFile(ofile, "recreate") as out:
        out.WriteObject(hres, "hAngRes")
        out.WriteObject(fres, "fAngRes")
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
        "-c",
        "--coordinate",
        help = "Coordinate to calculate resolution on",
        nargs = '?',
        const = CoordDefault,
        default = CoordDefault,
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
    CalculateAngReso(args.input, args.output, args.coordinate, args.pdg)

# end =========================================================================
