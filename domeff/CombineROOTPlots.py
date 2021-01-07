import os, sys
from tables import open_file
import ROOT
import numpy as np
import argparse
from tables import open_file
from icecube.weighting.fluxes import  GaisserH4a, GaisserH3a, GaisserH4a_IT, GaisserHillas, Hoerandel, Hoerandel5, Hoerandel_IT
from icecube.weighting import weighting
from event import *
from I3Tray import OMKey
from array import array

TotalCharge_IC = ROOT.TH1F("TotalCharge_IC","",1000,0,3000)
Zenith_IC = ROOT.TH1F("Zenith_IC","",200,-1.0,1.0)
RecEnergy_IC = ROOT.TH1F("RecEnergy_IC","",1000,min(reconstructedE_ic)*0.9,max(reconstructedE_ic)*1.1)
EndPointZ_IC = ROOT.TH1F("EndPointX_IC","",1000,min(recoEndpoint_ic)*0.9,max(recoEndpoint_ic)*1.1)
BoarderDist_IC = ROOT.TH1F("BoarderDist_IC","",1000,min(borderDistance_ic)*0.9,max(borderDistance_ic)*1.1)
StopLikeRatio_IC = ROOT.TH1F("StopLikeRatio_IC","",1000,min(stopLikeRatio_ic )*0.9,max(stopLikeRatio_ic)*1.1)
RecoLogL_IC = ROOT.TH1F("RecoLogL_IC","",1000,min(recoLogL_ic)*0.9,max(recoLogL_ic)*1.1)
DirectHits_IC = ROOT.TH1F("DirectHits_IC","",71,-0.5,70.5)
HitsOut_IC = ROOT.TH1F("HitsOut_IC","",1000,0,max(HitsOut_ic)*1.1)
TotalCharge_DC = ROOT.TH1F("TotalCharge_DC","",1000,0,3000)
Zenith_DC = ROOT.TH1F("Zenith_DC","",200,-1.0,1.0)
RecEnergy_DC = ROOT.TH1F("RecEnergy_DC","",1000,min(reconstructedE_dc)*0.9,max(reconstructedE_dc)*1.1)
EndPointZ_DC = ROOT.TH1F("EndPointX_DC","",1000,min(recoEndpoint_dc)*0.9,max(recoEndpoint_dc)*1.1)
BoarderDist_DC = ROOT.TH1F("BoarderDist_DC","",1000,min(borderDistance_dc)*0.9,max(borderDistance_dc)*1.1)
StopLikeRatio_DC = ROOT.TH1F("StopLikeRatio_DC","",1000,min(stopLikeRatio_dc)*0.9,max(stopLikeRatio_dc)*1.1)
RecoLogL_DC = ROOT.TH1F("RecoLogL_DC","",1000,min(recoLogL_dc)*0.9,max(recoLogL_dc)*1.1)
DirectHits_DC = ROOT.TH1F("DirectHits_DC","",(1+max(directHits_dc)-min(directHits_dc)),min(directHits_dc)-0.5,max(directHits_dc)+0.5)
HitsOut_DC = ROOT.TH1F("HitsOut_DC","",1000,min(HitsOut_dc)*0.9,max(HitsOut_dc)*1.1)

ImpactAll_ic = ROOT.TH1F("ImpactAll_IC","",1000,-1.0,1.0)
ImpactAll_dc = ROOT.TH1F("ImpactAll_DC","",1000,-1.0,1.0)
Impact_seeMPE_ic = ROOT.TH1F("ImpactseeMPE_IC","",1000,-1.0,1.0)
Impact_seeMPE_dc = ROOT.TH1F("ImpactseeMPE_DC","",1000,-1.0,1.0)

Impact_vs_Zenith_ic = ROOT.TH2F("Impact_vs_Zenith_IC","",200,-1.0,1.0,200,-1.0,1.0)
Impact_vs_Zenith_dc = ROOT.TH2F("Impact_vs_Zenith_DC","",200,-1.0,1.0,200,-1.0,1.0)

TotalCharge_vs_Zenith_ic = ROOT.TH2F("TotalCharge_vs_Zenith_IC","",200,-1.0,1.0,1000,0.0,3000.0)
TotalCharge_vs_Zenith_dc = ROOT.TH2F("TotalCharge_vs_Zenith_DC","",200,-1.0,1.0,1000,0.0,3000.0)

StoppingZ_vs_Zenith_ic = ROOT.TH2F("StoppingZ_vs_Zenith_ic","",200,-1.0,1.0,1000,-500.,500.)
StoppingZ_vs_Zenith_dc = ROOT.TH2F("StoppingZ_vs_Zenith_dc","",200,-1.0,1.0,1000,-500.,500.)
BorderDist_vs_Zenith_ic = ROOT.TH2F("BorderDist_vs_Zenith_ic","",200,-1.0,1.0,1000,-500.,500.)
BorderDist_vs_Zenith_dc = ROOT.TH2F("BorderDist_vs_Zenith_dc","",200,-1.0,1.0,1000,-500.,500.)
NChannel_vs_Zenith_ic = ROOT.TH2F("NChannel_vs_Zenith_ic","",200,-1.0,1.0,5000,0,5000.)
NChannel_vs_Zenith_dc = ROOT.TH2F("NChannel_vs_Zenith_dc","",200,-1.0,1.0,5000,0,5000.)
StopLike_vs_Zenith_ic = ROOT.TH2F("StopLike_vs_Zenith_ic","",200,-1.0,1.0,500,0,500.)
StopLike_vs_Zenith_dc = ROOT.TH2F("StopLike_vs_Zenith_dc","",200,-1.0,1.0,500,0,500.)
rLogL_vs_Zenith_ic = ROOT.TH2F("rLogL_vs_Zenith_ic","",200,-1.0,1.0,500,0,500.)
rLogL_vs_Zenith_dc = ROOT.TH2F("rLogL_vs_Zenith_dc","",200,-1.0,1.0,500,0,500.)


zenith_all = ROOT.TH1F("zenith_all","",100,0.0,1.0)
zenith_all_line = ROOT.TH1F("zenith_all_line","",100,0.0,1.0)
zenith_all_spe = ROOT.TH1F("zenith_all_spe","",100,0.0,1.0)
zenith_all_mpe = ROOT.TH1F("zenith_all_mpe","",100,0.0,1.0)
zenith_zenith = ROOT.TH1F("zenith_zenith","",100,0.0,1.0)
zenith_endpointz = ROOT.TH1F("zenith_endpointz","",100,0.0,1.0)
zenith_boarder = ROOT.TH1F("zenith_boarder","",100,0.0,1.0)
zenith_stopratio = ROOT.TH1F("zenith_stopratio","",100,0.0,1.0)
zenith_recoLogL = ROOT.TH1F("zenith_recoLogL","",100,0.0,1.0)
zenith_directHits = ROOT.TH1F("zenith_directHits","",100,0.0,1.0)

CascadeFilter_13 = ROOT.TH1F("CascadeFilter_13","",100,0.0,1.0)
NoCascade_13 = ROOT.TH1F("NoCascade","",100,0.0,1.0)
DeepCoreFilter_13 = ROOT.TH1F("DeepCoreFilter_13","",100,0.0,1.0)                  
DeepCoreFilter_TwoLayerExp_13 = ROOT.TH1F("DeepCoreFilter_TwoLayerExp_13","",100,0.0,1.0)      
EHEFilter_13 = ROOT.TH1F("EHEFilter_13","",100,0.0,1.0)                       
FSSCandidate_13 = ROOT.TH1F("FSSCandidate_13","",100,0.0,1.0)                    
FSSFilter_13 = ROOT.TH1F("FSSFilter_13","",100,0.0,1.0)                       
FilterMinBias_13 = ROOT.TH1F("FilterMinBias_13","",100,0.0,1.0)                   
FixedRateFilter_13 = ROOT.TH1F("FixedRateFilter_13","",100,0.0,1.0)                 
GCFilter_13 = ROOT.TH1F("GCFilter_13","",100,0.0,1.0)                        
I3DAQDecodeException = ROOT.TH1F("I3DAQDecodeException","",100,0.0,1.0)               
IceTopSTA3_13 = ROOT.TH1F("IceTopSTA3_13","",100,0.0,1.0)                      
IceTopSTA5_13 = ROOT.TH1F("IceTopSTA5_13","",100,0.0,1.0)                      
IceTop_InFill_STA3_13 = ROOT.TH1F("IceTop_InFill_STA3_13","",100,0.0,1.0)              
InIceSMT_IceTopCoincidence_13 = ROOT.TH1F("InIceSMT_IceTopCoincidence_13","",100,0.0,1.0)      
LID = ROOT.TH1F("LID","",100,0.0,1.0)                                
LowUp_13 = ROOT.TH1F("LowUp_13","",100,0.0,1.0)                           
MoonFilter_13 = ROOT.TH1F("MoonFilter_13","",100,0.0,1.0)                      
MuonFilter_13 = ROOT.TH1F("MuonFilter_13","",100,0.0,1.0)                      
OFUFilter_14 = ROOT.TH1F("OFUFilter_14","",100,0.0,1.0)                       
OnlineL2Filter_14 = ROOT.TH1F("OnlineL2Filter_14","",100,0.0,1.0)                  
SDST_FilterMinBias_13 = ROOT.TH1F("SDST_FilterMinBias_13","",100,0.0,1.0)              
SDST_IceTopSTA3_13 = ROOT.TH1F("SDST_IceTopSTA3_13","",100,0.0,1.0)                 
SDST_IceTop_InFill_STA3_13 = ROOT.TH1F("SDST_IceTop_InFill_STA3_13","",100,0.0,1.0)         
SDST_InIceSMT_IceTopCoincidence_13 = ROOT.TH1F("SDST_InIceSMT_IceTopCoincidence_13","",100,0.0,1.0) 
SlopFilter_13 = ROOT.TH1F("SlopFilter_13","",100,0.0,1.0)                      
SunFilter_13 = ROOT.TH1F("SunFilter_13","",100,0.0,1.0)                       
VEF_13 = ROOT.TH1F("VEF_13","",100,0.0,1.0)                             
InIceSMT = ROOT.TH1F("InIceSMT","",100,0.0,1.0)    
IceTopSMT = ROOT.TH1F("IceTopSMT","",100,0.0,1.0)   
InIceString = ROOT.TH1F("InIceString","",100,0.0,1.0) 
PhysMinBias = ROOT.TH1F("PhysMinBias","",100,0.0,1.0) 
DeepCoreSMT = ROOT.TH1F("DeepCoreSMT","",100,0.0,1.0) 
NotOnlySun = ROOT.TH1F("NotOnlySun","",100,0.0,1.0)

TimeResidual_IC = []
TimeResidual_DC = []

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--data', help='Directory of data files.',type=str,
				default = '/data/user/sanchezh/IC86_2015/Final_Level2_IC86_MPEFit_*.h5')
	parser.add_argument('-o', '--output', help='Name of output file.', type=str,
				default = "out.root")
	parser.add_argument('-n', '--nbins', help='Name of output file.', type=int,
				default = 8)

	args = parser.parse_args()

	# compute how many 20m bins to use.
	nbins = args.nbins

	TimeResidual_IC = [ROOT.TH1F(str("TimeResidual_IC_%d" % (i)),"",1000,-100.0,900.0) for i in range(nbins)]
	TimeResidual_DC = [ROOT.TH1F(str("TimeResidual_DC_%d" % (i)),"",1000,-100.0,900.0) for i in range(nbins)]

	file_list = []

	if "." in args.data :
		file_list = [args.data]
	else :
		files_dir = args.data
		file_list_aux = os.listdir(files_dir)
		file_list = list()
		for (dirpath, dirnames, filenames) in os.walk(files_dir):
			file_list += [os.path.join(dirpath,x) for x in filenames if '.root' in x]
    #remove duclicates
		file_list = list(set(file_list))
#	if args.flux == "data" :
#		file_list = [x for x in file_list_h5 if (args.eff in x and os.path.getsize(files_dir+x) > 12000000 )]
#	else :
#		file_list = [x for x in file_list_h5 if (args.eff in x)]

	nfiles = len(file_list)

	print(nfiles)

	fout = ROOT.TFile.Open(args.output+".root","RECREATE")

	fout.cd()

	
	nfiles = len(file_list)
	
	for filename in file_list :
		fin = ROOT.TFile.Open(filename,"READ")

		TotalCharge_IC.Add(fin.get(TotalCharge_IC.GetName()))
		Zenith_IC.Add(fin.get(Zenith_IC.GetName()))
		EndPointZ_IC.Add(fin.get(EndPointZ_IC.GetName()))
		BoarderDist_IC.Add(fin.get(BoarderDist_IC.GetName()))
		StopLikeRatio_IC.Add(fin.get(StopLikeRatio_IC.GetName()))
		RecoLogL_IC.Add(fin.get(RecoLogL_IC.GetName()))
		DirectHits_IC.Add(fin.get(DirectHits_IC.GetName()))
		HitsOut_IC.Add(fin.get(HitsOut_IC.GetName()))
		TotalCharge_DC.Add(fin.get(TotalCharge_DC.GetName()))
		Zenith_DC.Add(fin.get(Zenith_DC.GetName()))
		RecEnergy_DC.Add(fin.get(RecEnergy_DC.GetName()))
		EndPointZ_DC.Add(fin.get(EndPointZ_DC.GetName()))
		BoarderDist_DC.Add(fin.get(BoarderDist_DC.GetName()))
		StopLikeRatio_DC.Add(fin.get(StopLikeRatio_DC.GetName()))
		RecoLogL_DC.Add(fin.get(RecoLogL_DC.GetName()))
		DirectHits_DC.Add(fin.get(DirectHits_DC.GetName()))
		HitsOut_DC.Add(fin.get(HitsOut_DC.GetName()))

		ImpactAll_ic.Add(fin.get(ImpactAll_ic.GetName()))
		ImpactAll_dc.Add(fin.get(ImpactAll_dc.GetName()))
		Impact_seeMPE_ic.Add(fin.get(Impact_seeMPE_ic.GetName()))
		Impact_seeMPE_dc.Add(fin.get(Impact_seeMPE_dc.GetName()))

		Impact_vs_Zenith_ic.Add(fin.get(Impact_vs_Zenith_ic.GetName()))
		Impact_vs_Zenith_dc.Add(fin.get(Impact_vs_Zenith_dc.GetName()))

		TotalCharge_vs_Zenith_ic.Add(fin.get(TotalCharge_vs_Zenith_ic.GetName()))
		TotalCharge_vs_Zenith_dc.Add(fin.get(TotalCharge_vs_Zenith_dc.GetName()))

		StoppingZ_vs_Zenith_ic.Add(fin.get(StoppingZ_vs_Zenith_ic.GetName()))
		StoppingZ_vs_Zenith_dc.Add(fin.get(StoppingZ_vs_Zenith_dc.GetName()))
		BorderDist_vs_Zenith_ic.Add(fin.get(BorderDist_vs_Zenith_ic.GetName()))
		BorderDist_vs_Zenith_dc.Add(fin.get(BorderDist_vs_Zenith_dc.GetName()))
		NChannel_vs_Zenith_ic.Add(fin.get(NChannel_vs_Zenith_ic.GetName()))
		NChannel_vs_Zenith_dc.Add(fin.get(NChannel_vs_Zenith_dc.GetName()))
		StopLike_vs_Zenith_ic.Add(fin.get(StopLike_vs_Zenith_ic.GetName()))
		StopLike_vs_Zenith_dc.Add(fin.get(StopLike_vs_Zenith_dc.GetName()))
		rLogL_vs_Zenith_ic.Add(fin.get(rLogL_vs_Zenith_ic.GetName()))
		rLogL_vs_Zenith_dc.Add(fin.get(rLogL_vs_Zenith_dc.GetName()))


		zenith_all.Add(fin.get(zenith_all.GetName()))
		zenith_all_line.Add(fin.get(zenith_all_line.GetName()))
		zenith_all_spe.Add(fin.get(zenith_all_spe.GetName()))
		zenith_all_mpe.Add(fin.get(zenith_all_mpe.GetName()))
		zenith_zenith.Add(fin.get(zenith_zenith.GetName()))
		zenith_endpointz.Add(fin.get(zenith_endpointz.GetName()))
		zenith_boarder.Add(fin.get(zenith_boarder.GetName()))
		zenith_stopratio.Add(fin.get(zenith_stopratio.GetName()))
		zenith_recoLogL.Add(fin.get(zenith_recoLogL.GetName()))		
		zenith_directHits.Add(fin.get(zenith_directHits.GetName()))

		CascadeFilter_13.Add(fin.get(CascadeFilter_13.GetName()))
		NoCascade_13.Add(fin.get(NoCascade_13.GetName()))	
		DeepCoreFilter_13.Add(fin.get(DeepCoreFilter_13.GetName()))               
		DeepCoreFilter_TwoLayerExp_13.Add(fin.get(DeepCoreFilter_TwoLayerExp_13.GetName()))    
		EHEFilter_13.Add(fin.get(EHEFilter_13.GetName()))                    
		FSSCandidate_13.Add(fin.get(FSSCandidate_13.GetName()))                  
		FSSFilter_13.Add(fin.get(FSSFilter_13.GetName()))                   
		FilterMinBias_13.Add(fin.get(FilterMinBias_13.GetName()))                  
		FixedRateFilter_13.Add(fin.get(FixedRateFilter_13.GetName()))               
		GCFilter_13.Add(fin.get(GCFilter_13.GetName()))                       
		I3DAQDecodeException.Add(fin.get(I3DAQDecodeException.GetName()))               
		IceTopSTA3_13.Add(fin.get(IceTopSTA3_13.GetName()))                     
		IceTopSTA5_13.Add(fin.get(IceTopSTA5_13.GetName()))                      
		IceTop_InFill_STA3_13.Add(fin.get(IceTop_InFill_STA3_13.GetName()))             
		InIceSMT_IceTopCoincidence_13.Add(fin.get(InIceSMT_IceTopCoincidence_13.GetName()))     
		LID.Add(fin.get(LID.GetName()))                                
		LowUp_13.Add(fin.get(LowUp_13.GetName()))                         
		MoonFilter_13.Add(fin.get(MoonFilter_13.GetName()))                      
		MuonFilter_13.Add(fin.get(MuonFilter_13.GetName()))                      	
		OFUFilter_14.Add(fin.get(OFUFilter_14.GetName()))                       
		OnlineL2Filter_14.Add(fin.get(OnlineL2Filter_14.GetName()))                 
		SDST_FilterMinBias_13.Add(fin.get(SDST_FilterMinBias_13.GetName()))             
		SDST_IceTopSTA3_13.Add(fin.get(SDST_IceTopSTA3_13.GetName()))                	
		SDST_IceTop_InFill_STA3_13.Add(fin.get(SDST_IceTop_InFill_STA3_13.GetName()))        
		SDST_InIceSMT_IceTopCoincidence_13.Add(fin.get(SDST_InIceSMT_IceTopCoincidence_13.GetName()))
		SlopFilter_13.Add(fin.get(SlopFilter_13.GetName()))                      
		SunFilter_13.Add(fin.get(SunFilter_13.GetName()))                      	
		VEF_13.Add(fin.get(VEF_13.GetName()))                            
		InIceSMT.Add(fin.get(InIceSMT.GetName()))   
		IceTopSMT.Add(fin.get(IceTopSMT.GetName())) 
		InIceString.Add(fin.get(InIceString.GetName()))
		PhysMinBias.Add(fin.get(PhysMinBias.GetName()))
		DeepCoreSMT.Add(fin.get(DeepCoreSMT.GetName()))
		NotOnlySun.Add(fin.get(NotOnlySun.GetName()))

		for i in range(len(TimeResidual_IC)) : TimeResidual_IC[i].Add(fin.get(TimeResidual_IC[i].GetName()))
		for i in range(len(TimeResidual_DC)) : TimeResidual_DC[i].Add(fin.get(TimeResidual_DC[i].GetName()))
		
		fin.Close()
	
	fout.cd()

	TotalCharge_IC.Write()
	Zenith_IC.Write()
	RecEnergy_IC.Write()
	EndPointZ_IC.Write()
	BoarderDist_IC.Write()
	StopLikeRatio_IC.Write()
	RecoLogL_IC.Write()
	DirectHits_IC.Write()
	HitsOut_IC.Write()
	TotalCharge_DC.Write()
	Zenith_DC.Write()
	RecEnergy_DC.Write()
	EndPointZ_DC.Write()
	BoarderDist_DC.Write()
	StopLikeRatio_DC.Write()
	RecoLogL_DC.Write()
	DirectHits_DC.Write()
	HitsOut_DC.Write()
	ImpactAll_ic.Write()
	ImpactAll_dc.Write()
	Impact_seeMPE_ic.Write()
	Impact_seeMPE_dc.Write()
	Impact_vs_Zenith_ic.Write()
	Impact_vs_Zenith_dc.Write()
	TotalCharge_vs_Zenith_ic.Write()
	TotalCharge_vs_Zenith_dc.Write()
	StoppingZ_vs_Zenith_dc.Write()
	StoppingZ_vs_Zenith_ic.Write()
	BorderDist_vs_Zenith_dc.Write()
	BorderDist_vs_Zenith_ic.Write()
	NChannel_vs_Zenith_dc.Write()
	NChannel_vs_Zenith_ic.Write()
	StopLike_vs_Zenith_dc.Write()
	StopLike_vs_Zenith_ic.Write()
	rLogL_vs_Zenith_dc.Write()
	rLogL_vs_Zenith_ic.Write()
	zenith_all.Write()
	zenith_zenith.Write()
	zenith_endpointz.Write()
	zenith_boarder.Write()
	zenith_stopratio.Write()
	zenith_recoLogL.Write()
	zenith_directHits.Write()
	zenith_all_line.Write()
	zenith_all_spe.Write()
	zenith_all_mpe.Write()
	for i in range(len(TimeResidual_IC)) : TimeResidual_IC[i].Write()
	for i in range(len(TimeResidual_DC)) : TimeResidual_DC[i].Write()
	CascadeFilter_13.Write()
	DeepCoreFilter_13.Write()             
	DeepCoreFilter_TwoLayerExp_13.Write()   
	EHEFilter_13.Write()                     
	FSSCandidate_13.Write()                   
	FSSFilter_13.Write()                      
	FilterMinBias_13.Write()                  
	FixedRateFilter_13.Write()                
	GCFilter_13.Write()             
	I3DAQDecodeException.Write()        
	IceTopSTA3_13.Write()                  
	IceTopSTA5_13.Write()                    
	IceTop_InFill_STA3_13.Write()            
	InIceSMT_IceTopCoincidence_13.Write()     
	LID.Write()                              
	LowUp_13.Write()                         
	MoonFilter_13.Write()                   
	MuonFilter_13.Write()                     
	OFUFilter_14.Write()                      
	OnlineL2Filter_14.Write()                
	SDST_FilterMinBias_13.Write()          
	SDST_IceTopSTA3_13.Write()          
	SDST_IceTop_InFill_STA3_13.Write()       
	SDST_InIceSMT_IceTopCoincidence_13.Write() 
	SlopFilter_13.Write()                     
	SunFilter_13.Write()                      
	VEF_13.Write()                           
	InIceSMT.Write()    
	IceTopSMT.Write()   
	InIceString.Write()
	PhysMinBias.Write()
	DeepCoreSMT.Write()
	NotOnlySun.Write()
	NoCascade_13.Write()

	fout.Close()


