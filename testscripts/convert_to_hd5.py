from icecube import icetray, dataio
from I3Tray import I3Tray
from icecube.hdfwriter import I3HDFWriter
import argparse

parser = argparse.ArgumentParser(description='Get Files') 
parser.add_argument("-i", "--infile",default=[], type=str, nargs='+', dest="INFILE", help="Read input from INFILE (.i3{.gz} format)")
parser.add_argument("-o", "--outfile",default=[], type=str, dest="OUTFILE",help="Write output to FILE")
args = parser.parse_args()

tray = I3Tray()    
tray.AddModule('I3Reader',filenamelist = args.INFILE)

tray.AddSegment(I3HDFWriter,                                                    
                output=args.OUTFILE,                                            
                SubEventStreams=['InIceSplit'],                                 
#               BookEverything = True,                                         
                keys = ['I3MCTree',
                'I3EventHeader',
                'I3MCWeightDict'],         
               )

tray.Execute()
