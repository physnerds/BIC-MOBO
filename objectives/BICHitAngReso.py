#!/usr/bin/env python3
# =============================================================================
## @file   BICHitAngReso.py
#  @author Derek Anderson
#  @date   02.11.2026
# -----------------------------------------------------------------------------
## @brief Script to compute angular resolutions (in
#    eta, phi, etc.) for a specified particle species
#    from BIC imaging hits according to this algorithm:
#
#      1. Find the imaging cluster associated to thrown
#         electron
#      2. Locate the most energetic hit in each layer
#         of the imaging cluster
#      3. From these, select the hit in the most
#         upstream layer and calculate the difference
#         in angle
#      4. Calculate the FWHM of the distribution
#         of angle differences
#
#  Usage if executed directly:
#      ./BICHitAngReso.py \
#          -i <input file> \
#          -o <output file> \
#          -c <coordinate> \
#          -p <pdg code> \
#          -b <branch> (optional)
# =============================================================================

from dataclasses import dataclass
import argparse as ap
import numpy as np
import ROOT
import sys

from podio.reading import get_reader

# default arguments
IFileDefault  = "root://dtn-eic.jlab.org//volatile/eic/EPIC/RECO/25.12.0/epic_craterlake/SINGLE/e-/5GeV/45to135deg/e-_5GeV_45to135deg.0099.eicrecon.edm4eic.root"
OFileDefault  = "test_reso.root"
CoordDefault  = "eta"
PDGDefault    = 11
HitsDefault   = "EcalBarrelImagingRecHits"
ParsDefault   = "MCParticles"
AssocDefault  = "EcalBarrelImagingClusterAssociations"


# utilities ===================================================================

@dataclass
class Info:
    """Hit and Particle Info

    Helper class to store key information
    on hits and particles

    Members:
      energy: energy of hit/particle
      angle:  anglular coordinate (theta, eta, ...)
      perp:   radial coordinate (r/pt) of hit/particle
      layer:  most upstream layer with hits
      vector: 3D position/momentum of hit/particle
    """
    energy: float = -999.0
    angle: float = -999.0
    perp: float = -999.0
    layer: int = -999
    vector: ROOT.Math.XYZVector = ROOT.Math.XYZVector(-999.0, -999.0, -999.0)

    def _SetVector(self, edmvec):
        self.vector = ROOT.Math.XYZVector(
            edmvec.x,
            edmvec.y,
            edmvec.z
        )

    def _SetAngle(self, coord):
        match coord:
            case "theta":
                self.angle = self.vector.Theta()
            case "eta":
                self.angle = self.vector.Eta()
            case "phi":
                self.angle = self.vector.Phi()
            case _:
                raise ValueError("Unknown coordinate specified!")

    def SetParInfo(self, cname, par):
        self._SetVector(par.getMomentum())
        self._SetAngle(cname)
        self.energy = par.getEnergy()
        self.perp   = self.vector.Rho()

    def SetHitInfo(self, cname, hit):
        self._SetVector(hit.getPosition())
        self._SetAngle(cname)
        self.energy = hit.getEnergy()
        self.perp   = self.vector.Rho()
        self.layer  = hit.getLayer()


# resolution calculation ======================================================

def CalculateHitAngReso(
    ifile     = IFileDefault,
    ofile     = OFileDefault,
    coord     = CoordDefault,
    pdg       = PDGDefault,
    hitcoll   = HitsDefault,
    parcoll   = ParsDefault,
    assoccoll = AssocDefault,
):
    """CalculateHitAngReso

    A function to calculate angular resolution for a 
    specified species of particle from BIC imaging
    hits according to this algorithm:

      1. Find the imaging cluster associated to thrown
         electron
      2. Locate the most energetic hit in each layer
         of the imaging cluster
      3. From these, select the hit in the most
         upstream layer and calculate the difference
         in angle
      4. Calculate the FWHM of the distribution
         of angle differences

    Args:
      ifile:     input file name
      ofile:     output file name
      coord:     coordinate to calculate resolution on
      pdg:       PDG code of particle species
      hitcoll:   calo reco hit collection to process
      parcoll:   mc particle collection to process
      assoccoll: cluster-particle associations to process
    Returns:
      calculated resolution
    """

    # sanitize coordinate input
    coord = coord.lower()

    # set up histograms, etc. -------------------------------------------------

    # set variable for axis accordingly 
    var = "x"
    match coord:
        case "theta":
            var = "#theta"
        case "eta":
            var = "#eta"
        case "phi":
            var = "#phi"
        case _:
            raise ValueError("Unknown coordinate specified!")

    # construct axis title
    axis = ";#delta" + var + " = " + var + "^{image}_{max hit} - " + var + "_{par}"

    # create histogram from extracting resolution
    hdiff = ROOT.TH1D("hAngRes", axis, 80, -0.2, 0.2)
    hdiff.Sumw2()

    # create utility histograms for tracking other
    # relevant info
    #   - TODO consolidate histograms into a helper class,
    #     automate creating most of them, automate
    #     Sumw2()ing
    hpar   = ROOT.TH1D("hParEne", "Particle energy;E_{par} [GeV]", 20, -0.5, 9.5)
    heff   = ROOT.TH1D("hEfficiency", "Efficiency as a function of particle energy;E_{par} [GeV]", 20, -0.5, 9.5)
    hclust = ROOT.TH1D("hClustEne", "Associated cluster energy;E_{clust} [GeV]", 20, -0.5, 9.5)
    hmax   = ROOT.TH1D("hMaxEneHit", "Energy of most energetic hit in most upstream layer;E^{image}_{max hit} [GeV]", 100, -0.5, 9.5)
    hlay   = ROOT.TH1D("hMinLayer", "Most upstream layer;Layer", 8, -0.5, 7.5)
    hmxl   = ROOT.TH2D("hMaxHitEneVsMinLayer", "Energy of most energetic hit vs. most upstream layer;Layer;E^{image}_{max hit} [GeV]", 8, -0.5, 7.5, 100, -0.5, 9.5)
    hpar.Sumw2()
    heff.Sumw2()
    hclust.Sumw2()
    hmax.Sumw2()
    hlay.Sumw2()
    hmxl.Sumw2()

    # TODO add other useful histograms
    #   - par (e, r, coord)
    #   - all hit (e, r, coord), (x, y, z)
    #   - max hit (e, r, coord), (x, y, z)
    #   - hit layer max hit E
    #   - hit layer vs. total energy
    #   - 1st nonzero layer hit positions
    #   - 1st nonzero layer index
    #   - hit efficiency
    #   - efficiency * reso
    #   - efficiency vs. par (e, eta, phi)

    # event loop --------------------------------------------------------------

    # loop through all events
    reader = get_reader(ifile)
    for iframe, frame in enumerate(reader.get("events")):

        # grab relevant branches
        rehits = frame.get(hitcoll)
        mcpars = frame.get(parcoll)
        assocs = frame.get(assoccoll)

        # pick out the primary particle
        primary = None
        for par in mcpars:
            status = par.getGeneratorStatus()
            if par.getPDG() == pdg and status == 1:
                primary = par
                break

        # if for some reason no primary was found,
        # skip event
        if primary is None:
            print(f"Warning! Frame {iframe} has no primary in file:\n  -- {ifile}")
            continue

        # scrape particle info for histogramming
        pinfo = Info()
        pinfo.SetParInfo(coord, primary)
        hpar.Fill(pinfo.energy)

        # dictionaries to keep track of max energy
        # hits in each layer
        maxenes = {
            1 : 0.0,
            2 : 0.0,
            3 : 0.0,
            4 : 0.0,
            5 : 0.0,
            6 : 0.0
        }
        maxhits = dict()

        # now identify the most energetic hit in 
        # each layer associated with the primary
        cluster = None
        for assoc in assocs:

            if primary != assoc.getSim():
                continue
            else:
                cluster = assoc.getRec()

            # loop through hits to check layers
            for hit in assoc.getRec().getHits():

                layer = hit.getLayer()
                if layer > 6:
                    print(f"Warning! Hit {hit.getObjectID().index} has a layer above 6 ({layer})!")
                    continue

                if hit.getEnergy() > maxenes[layer]:
                    maxenes[layer] = hit.getEnergy()
                    maxhits[layer] = hit

        if cluster is None:
            continue

        # fill hists for efficiency
        heff.Fill(pinfo.energy)
        hclust.Fill(cluster.getEnergy())

        # pick out most upstream layer from
        # most energetic hits
        minlayer = min(maxhits.keys())

        # scrape info from max hit in most
        # upstream layer
        hinfo = Info()
        hinfo.SetHitInfo(coord, maxhits[minlayer])

        # calculate difference
        hdiff.Fill(hinfo.angle - pinfo.angle)

        # fill hists
        hmax.Fill(hinfo.energy)
        hlay.Fill(minlayer)
        hmxl.Fill(minlayer, hinfo.energy)

    # eff + fwhm calculation --------------------------------------------------

    # calculate efficiency
    heff.Divide(heff, hpar, 1.0, 1.0)

    # extract hist properties to initialize fit
    muhist  = hdiff.GetMean()
    rmshist = hdiff.GetRMS()
    inthist = hdiff.Integral()

    # set up a gaussian to extract main peak
    #   - FIXME func range should be tied to hist range
    fdiff = ROOT.TF1("fAngRes", "gaus(0)", -0.2, 0.2)
    fdiff.SetParameters(
        inthist,
        muhist,
        rmshist
    )

    # fit histogram over nonzero bins
    ifirst   = hdiff.FindFirstBinAbove(0.0)
    ilast    = hdiff.FindLastBinAbove(0.0)
    first_lo = hdiff.GetBinLowEdge(ifirst)
    last_hi  = hdiff.GetBinLowEdge(ilast + 1)
    hdiff.Fit("fAngRes", "", "", first_lo, last_hi)

    # calculate full-width-half-max
    mumain     = fdiff.GetParameter(1)
    maximum    = fdiff.Eval(mumain)
    halfmax_lo = fdiff.GetX(maximum / 2.0, first_lo, mumain)
    halfmax_hi = fdiff.GetX(maximum / 2.0, mumain, last_hi)
    fwhm       = halfmax_hi - halfmax_lo

    # wrap up script ----------------------------------------------------------

    # save objects
    #   - TODO automate hist saving
    with ROOT.TFile(ofile, "recreate") as out:
        out.WriteObject(fdiff, "fAngRes")
        out.WriteObject(hdiff, "hAngRes")
        out.WriteObject(hpar, "hParEne")
        out.WriteObject(heff, "hEfficiency")
        out.WriteObject(hclust, "hClustEne")
        out.WriteObject(hmax, "hMaxHitEne")
        out.WriteObject(hlay, "hMinLayer")
        out.WriteObject(hmxl, "hMaxHitEneVsMinLayer")
        out.Close()

    # write out key info to a text file for
    # extraction later
    otext = ofile.replace(".root", ".txt")
    with open(otext, 'w') as out:
        out.write(f"{fwhm}\n")

    # and return fwhm as resolution
    return fwhm

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
        "-r",
        "--rechits",
        help = "Hit collection to use",
        nargs = '?',
        const = HitsDefault,
        default = HitsDefault,
        type = str
    )
    parser.add_argument(
        "-m",
        "--mcpars",
        help = "MC particle collection to use",
        nargs = '?',
        const = ParsDefault,
        default = ParsDefault,
        type = str
    )
    parser.add_argument(
        "-a",
        "--assocs",
        help = "Cluster-particle associations to use",
        nargs = '?',
        const = AssocDefault,
        default = AssocDefault,
        type = str
    )

    # grab arguments
    args = parser.parse_args()

    # run analysis
    CalculateHitAngReso(
        args.input,
        args.output,
        args.coordinate,
        args.pdg,
        args.rechits,
        args.mcpars,
        args.assocs,
    )

# end =========================================================================
