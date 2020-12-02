

void makeratioplots() {

TFile* datafile_root = new TFile(sys.argv[1],"READ")
TFile* eff090_root = new TFile(sys.argv[2],"READ")
TFile* eff100_root = new TFile(sys.argv[3],"READ")
TFile* eff110_root = new TFile(sys.argv[4],"READ")
TFile* eff120_root = new TFile(sys.argv[5],"READ")

TH1F* data_allazmuth = (TH1F*) datafile_root->Get("zenith_all")
data_allazmuth->Scale(1./data_allazmuth->Integral())
data_allazmuth->SetStats(0)
TH1F* eff090_allazmuth = (TH1F*) eff090_root->Get("zenith_all")
eff090_allazmuth->Scale(1./eff090_allazmuth->Integral())
eff090_allazmuth->SetStats(0)
TH1F* ratio_eff090_allazmuth = (TH1F*) data_allazmuth->Clone()
ratio_eff090_allazmuth->Divide(eff090_allazmuth) 
TH1F* eff100_allazmuth = (TH1F*) eff100_root->Get("zenith_all")
eff100_allazmuth->Scale(1./eff100_allazmuth->Integral())
eff100_allazmuth->SetStats(0) 
TH1F* ratio_eff100_allazmuth = (TH1F*) data_allazmuth->Clone()
ratio_eff100_allazmuth->Divide(eff100_allazmuth) 
TH1F* eff110_allazmuth = (TH1F*) eff110_root->Get("zenith_all")
eff110_allazmuth->Scale(1./eff110_allazmuth->Integral())
eff110_allazmuth->SetStats(0)
TH1F* ratio_eff110_allazmuth = (TH1F*) data_allazmuth->Clone()
ratio_eff110_allazmuth->Divide(eff110_allazmuth)  
TH1F* eff120_allazmuth = (TH1F*) eff120_root->Get("zenith_all")
eff120_allazmuth->Scale(1./eff120_allazmuth->Integral())
eff120_allazmuth->SetStats(0)
TH1F* ratio_eff120_allazmuth = (TH1F*) data_allazmuth->Clone()
ratio_eff120_allazmuth->Divide(eff120_allazmuth) 

TH1F* data_analysisazmuth = (TH1F*) datafile_root->Get("Zenith_IC")
data_analysisazmuth->Scale(1./data_analysisazmuth->Integral())
data_analysisazmuth->SetStats(0)
TH1F* eff090_analysisazmuth = (TH1F*) eff090_root->Get("Zenith_IC")
eff090_analysisazmuth->Scale(1./eff090_analysisazmuth->Integral()) 
eff090_analysisazmuth->SetStats(0)
TH1F* ratio_eff090_analysisazmuth = (TH1F*) data_analysisazmuth->Clone()
ratio_eff090_analysisazmuth->Divide(eff090_analysisazmuth) 
TH1F* eff100_analysisazmuth = (TH1F*) eff100_root->Get("Zenith_IC")
eff100_analysisazmuth->Scale(1./eff100_analysisazmuth->Integral()) 
eff100_analysisazmuth->SetStats(0)
TH1F* ratio_eff100_analysisazmuth = (TH1F*) data_analysisazmuth->Clone()
ratio_eff100_analysisazmuth->Divide(eff100_analysisazmuth) 
TH1F* eff110_analysisazmuth = (TH1F*) eff110_root->Get("Zenith_IC")
eff110_analysisazmuth->Scale(1./eff110_analysisazmuth->Integral()) 
eff110_analysisazmuth->SetStats(0)
TH1F* ratio_eff110_analysisazmuth = (TH1F*) data_analysisazmuth->Clone()
ratio_eff110_analysisazmuth->Divide(eff110_analysisazmuth) 
TH1F* eff120_analysisazmuth = (TH1F*) eff120_root->Get("Zenith_IC")
eff120_analysisazmuth->Scale(1./eff120_analysisazmuth->Integral())
eff120_analysisazmuth->SetStats(0)
TH1F* ratio_eff120_analysisazmuth = (TH1F*) data_analysisazmuth->Clone()
ratio_eff120_analysisazmuth->Divide(eff120_analysisazmuth) 

TH1F* data_allimpact = (TH1F*) datafile_root->Get("ImpactAll_IC")
data_allimpact->Scale(1./data_allimpact->Integral())
data_allimpact->SetStats(0)
TH1F* eff090_allimpact = (TH1F*) eff090_root->Get("ImpactAll_IC")
eff090_allimpact->Scale(1./eff090_allimpact->Integral())
eff090_allimpact->SetStats(0)
TH1F* ratio_eff090_allimpact = (TH1F*) data_allimpact->Clone()
ratio_eff090_allimpact->Divide(eff090_allimpact) 
TH1F* eff100_allimpact = (TH1F*) eff100_root->Get("ImpactAll_IC")
eff100_allimpact->Scale(1./eff100_allimpact->Integral()) 
eff100_allimpact->SetStats(0)
TH1F* ratio_eff100_allimpact = (TH1F*) data_analysisazmuth->Clone()
ratio_eff100_allimpact->Divide(eff100_allimpact) 
TH1F* eff110_allimpact = (TH1F*) eff110_root->Get("ImpactAll_IC")
eff110_allimpact->Scale(1./eff110_allimpact->Integral()) 
eff110_allimpact->SetStats(0)
TH1F* ratio_eff110_allimpact = (TH1F*) data_allimpact->Clone()
ratio_eff110_allimpact->Divide(eff110_allimpact) 
TH1F* eff120_allimpact = (TH1F*) eff120_root->Get("ImpactAll_IC")
eff120_allimpact->Scale(1./eff120_allimpact->Integral())
eff120_allimpact->SetStats(0)
TH1F* ratio_eff120_allimpact = (TH1F*) data_allimpact->Clone()
ratio_eff120_allimpact->Divide(eff120_allimpact) 

TH1F* data_peimpact = (TH1F*) datafile_root->Get("ImpactseeMPE_IC")
data_peimpact->Scale(1./data_peimpact.Integral())
data_peimpact->SetStats(0)
TH1F* eff090_peimpact = (TH1F*) eff090_root->Get("ImpactseeMPE_IC")
eff090_peimpact->Scale(1./eff090_peimpact->Integral())
eff090_peimpact->SetStats(0) 
TH1F* ratio_eff090_peimpact = (TH1F*) data_peimpact->Clone()
ratio_eff090_peimpact->Divide(eff090_peimpact) 
TH1F* eff100_peimpact = (TH1F*) eff100_root->Get("ImpactseeMPE_IC")
eff100_peimpact->Scale(1./eff100_peimpact->Integral())
eff100_peimpac->SetStats(0) 
TH1F* ratio_eff100_peimpact = (TH1F*) data_peimpact->Clone()
ratio_eff100_peimpact->Divide(eff100_peimpact) 
TH1F* eff110_peimpact = (TH1F*) eff110_root->Get("ImpactseeMPE_IC")
eff110_peimpact->Scale(1./eff110_peimpact->Integral())
eff110_peimpact->SetStats(0) 
TH1F* ratio_eff110_peimpact = (TH1F*) data_peimpact->Clone()
ratio_eff110_peimpact->Divide(eff110_peimpact) 
TH1F* eff120_peimpact = (TH1F*) eff120_root->Get("ImpactseeMPE_IC")
eff120_peimpact->Scale(1./eff120_peimpact->Integral())
eff120_peimpact->SetStats(0)
TH1F* ratio_eff120_peimpact = (TH1F*) data_peimpact->Clone()
ratio_eff120_peimpact->Divide(eff120_peimpact) 

TH1F* data_endpointx = (TH1F*) datafile_root->Get("EndPointX_IC")
data_endpointx->Scale(1./data_endpointx->Integral())
data_endpointx->SetStats(0)
TH1F* eff090_endpointx = (TH1F*) eff090_root->Get("EndPointX_IC")
eff090_endpointx->Scale(1./eff090_endpointx->Integral())
eff090_endpointx->SetStats(0) 
TH1F* ratio_eff090_endpointx = (TH1F*) data_endpointx->Clone()
ratio_eff090_endpointx->Divide(eff090_endpointx) 
TH1F* eff100_endpointx = (TH1F*) eff100_root->Get("EndPointX_IC")
eff100_endpointx->Scale(1./eff100_endpointx->Integral())
eff100_endpointx->SetStats(0) 
TH1F* ratio_eff100_endpointx = (TH1F*) data_endpointx->Clone()
ratio_eff100_endpointx->Divide(eff100_endpointx) 
TH1F* eff110_endpointx = (TH1F*) eff110_root->Get("EndPointX_IC")
eff110_endpointx->Scale(1./eff110_endpointx->Integral())
eff110_endpointx->SetStats(0) 
TH1F* ratio_eff110_endpointx = (TH1F*) data_endpointx->Clone()
ratio_eff110_endpointx->Divide(eff110_endpointx) 
TH1F* eff120_endpointx = (TH1F*) eff120_root->Get("EndPointX_IC")
eff120_endpointx->Scale(1./eff120_endpointx->Integral())
eff120_endpointx->SetStats(0)
TH1F* ratio_eff120_endpointx = (TH1F*) data_endpointx->Clone()
ratio_eff120_endpointx->Divide(eff120_endpointx) 

TH1F* data_boarderdist = (TH1F*) datafile_root->Get("BoarderDist_IC")
data_boarderdist->Scale(1./data_boarderdist->Integral())
data_boarderdist->SetStats(0)
TH1F* eff090_boarderdist = (TH1F*) eff090_root->Get("BoarderDist_IC")
eff090_boarderdist->Scale(1./eff090_boarderdist->Integral())
eff090_boarderdist->SetStats(0) 
TH1F* ratio_eff090_boarderdist = (TH1F*) data_boarderdist->Clone()
ratio_eff090_boarderdist->Divide(eff090_boarderdist) 
TH1F* eff100_boarderdist = eff100_root->Get("BoarderDist_IC")
eff100_boarderdist->Scale(1./eff100_boarderdist->Integral())
eff100_boarderdist->SetStats(0) 
TH1F* ratio_eff100_boarderdist = (TH1F*) data_boarderdist->Clone()
ratio_eff100_boarderdist->Divide(eff100_boarderdist) 
TH1F* eff110_boarderdist = (TH1F*) eff110_root->Get("BoarderDist_IC")
eff110_boarderdist->Scale(1./eff110_boarderdist->Integral())
eff110_boarderdist->SetStats(0) 
TH1F* ratio_eff110_boarderdist = (TH1F*) data_boarderdist->Clone()
ratio_eff110_boarderdist->Divide(eff110_boarderdist) 
TH1F* eff120_boarderdist = (TH1F*) eff120_root->Get("BoarderDist_IC")
eff120_boarderdist->Scale(1./eff120_boarderdist->Integral())
eff120_boarderdist->SetStats(0)
TH1F* ratio_eff120_endpointx = (TH1F*) data_endpointx->Clone()
ratio_eff120_endpointx->Divide(eff120_endpointx) 

TFile* fout = new TFile(sys.argv[6],"RECREATE")

data_allazmuth->Write("data_allazmuth");
eff090_allazmuth->Write("eff090_allazmuth"); 
ratio_eff090_allazmuth->Write("ratio_eff090_allazmuth");
eff100_allazmuth->Write("eff100_allazmuth");
ratio_eff100_allazmuth->Write("ratio_eff100_allazmuth");
eff110_allazmuth->Write("eff110_allazmuth");
ratio_eff110_allazmuth->Write("ratio_eff110_allazmuth");
eff120_allazmuth->Write("eff120_allazmuth");
ratio_eff120_allazmuth->Write("ratio_eff120_allazmuth");

data_analysisazmuth->Write("data_analysisazmuth");
eff090_analysisazmuth->Write("eff090_analysisazmuth");
ratio_eff090_analysisazmuth->Write("ratio_eff090_analysisazmuth");
eff100_analysisazmuth->Write("eff100_analysisazmuth");
ratio_eff100_analysisazmuth->Write("ratio_eff100_analysisazmuth");
eff110_analysisazmuth->Write("eff110_analysisazmuth");
ratio_eff110_analysisazmuth->Write("ratio_eff110_analysisazmuth");
eff120_analysisazmuth->Write("eff120_analysisazmuth");
ratio_eff120_analysisazmuth->Write("ratio_eff120_analysisazmuth");

data_allimpact->Write("data_allimpact");
eff090_allimpact->Write("eff090_allimpact");
ratio_eff090_allimpact->Write("ratio_eff090_allimpact");
eff100_allimpact->Write("eff100_allimpact");
ratio_eff100_allimpact->Write("ratio_eff100_allimpact");
eff110_allimpact->Write("eff110_allimpact");
ratio_eff110_allimpact->Write("ratio_eff110_allimpact");
eff120_allimpact->Write("eff120_allimpact");
ratio_eff120_allimpact->Write("ratio_eff120_allimpact");

data_peimpact->Write("data_peimpact");
eff090_peimpact->Write("eff090_peimpact");
ratio_eff090_peimpact->Write("atio_eff090_peimpact");
eff100_peimpact->Write("eff100_peimpact");
ratio_eff100_peimpact->Write("ratio_eff100_peimpact");
eff110_peimpact->Write("eff110_peimpact");
ratio_eff110_peimpact->Write("ratio_eff110_peimpact");
eff120_peimpact->Write("eff120_peimpact");
ratio_eff120_peimpact->Write("ratio_eff120_peimpact");

data_endpointx->Write("data_endpointx");
eff090_endpointx->Write("eff090_endpointx");
ratio_eff090_endpointx->Write("ratio_eff090_endpointx");
eff100_endpointx->Write("eff100_endpointx");
ratio_eff100_endpointx->Write("ratio_eff100_endpointx");
eff110_endpointx->Write("eff110_endpointx");
ratio_eff110_endpointx->Write("ratio_eff110_endpointx");
eff120_endpointx->Write("eff120_endpointx");
ratio_eff120_endpointx->Write("ratio_eff120_endpointx");

data_boarderdist->Write("data_boarderdist");
eff090_boarderdist->Write("eff090_boarderdist");
ratio_eff090_boarderdist->Write("ratio_eff090_boarderdist");
eff100_boarderdist->Write("eff100_boarderdist");
ratio_eff100_boarderdist->Write("ratio_eff100_boarderdist");
eff110_boarderdist->Write("eff110_boarderdist");
ratio_eff110_boarderdist->Write("atio_eff110_boarderdist");
eff120_boarderdist->Write("eff120_boarderdist");
ratio_eff120_endpointx->Write("ratio_eff120_endpointx");

fout->Close();

}


