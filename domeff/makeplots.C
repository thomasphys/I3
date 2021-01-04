

void makeplots() { 

TFile* datafile_root = new TFile("Level2pass2a_FullYear_cutanalysis_lowe.root","READ");
TFile* eff090_root = new TFile("MC090_cutanalysis_40_70.root","READ");
TFile* eff100_root = new TFile("MC100_cutanalysis_lowe.root","READ");
TFile* eff110_root = new TFile("MC110_cutanalysis_40_70.root","READ");
TFile* eff120_root = new TFile("MC120_cutanalysis_40_70.root","READ");

TGraphErrors* data_chargedist_IC = (TGraphErrors*) datafile_root->Get("Charge_Distance_IC");
double* data_chargedist_IC_Xvalue = data_chargedist_IC->GetX();
double* data_chargedist_IC_Yvalue = data_chargedist_IC->GetY();
double* data_chargedist_IC_Yerror = data_chargedist_IC->GetEY();
TGraphErrors* eff090_chargedist_IC = (TGraphErrors*) eff090_root->Get("Charge_Distance_IC");
double* eff090_chargedist_IC_Xvalue = eff090_chargedist_IC->GetX();
double* eff090_chargedist_IC_Yvalue = eff090_chargedist_IC->GetY();
double* eff090_chargedist_IC_Yerror = eff090_chargedist_IC->GetEY();
TGraphErrors* eff100_chargedist_IC = (TGraphErrors*) eff100_root->Get("Charge_Distance_IC");
double* eff100_chargedist_IC_Xvalue = eff100_chargedist_IC->GetX();
double* eff100_chargedist_IC_Yvalue = eff100_chargedist_IC->GetY();
double* eff100_chargedist_IC_Yerror = eff100_chargedist_IC->GetEY();
TGraphErrors* eff110_chargedist_IC = (TGraphErrors*) eff110_root->Get("Charge_Distance_IC");
double* eff110_chargedist_IC_Xvalue = eff110_chargedist_IC->GetX();
double* eff110_chargedist_IC_Yvalue = eff110_chargedist_IC->GetY();
double* eff110_chargedist_IC_Yerror = eff110_chargedist_IC->GetEY();
TGraphErrors* eff120_chargedist_IC = (TGraphErrors*) eff120_root->Get("Charge_Distance_IC");
double* eff120_chargedist_IC_Xvalue = eff120_chargedist_IC->GetX();
double* eff120_chargedist_IC_Yvalue = eff120_chargedist_IC->GetY();
double* eff120_chargedist_IC_Yerror = eff120_chargedist_IC->GetEY();

int n = data_chargedist_IC->GetN();

for(int i=0; i<n; ++i){
	eff090_chargedist_IC_Yvalue[i] /= data_chargedist_IC_Yvalue[i];
	double error_data = data_chargedist_IC_Yerror[i]/data_chargedist_IC_Yvalue[i];
	double error_eff090 = eff090_chargedist_IC_Yerror[i]/eff090_chargedist_IC_Yvalue[i];
	eff090_chargedist_IC_Yerror[i] = eff090_chargedist_IC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff090*error_eff090);
	eff090_chargedist_IC_Xvalue[i] = 0.5*(eff090_chargedist_IC_Xvalue[i]+data_chargedist_IC_Xvalue[i]);
}
TGraphErrors* eff090_ratio_IC = new TGraphErrors(data_chargedist_IC->GetN(),eff090_chargedist_IC_Xvalue,eff090_chargedist_IC_Yvalue,0,eff090_chargedist_IC_Yerror);

for(int i=0; i<n; ++i){
	eff100_chargedist_IC_Yvalue[i] /= data_chargedist_IC_Yvalue[i];
	double error_data = data_chargedist_IC_Yerror[i]/data_chargedist_IC_Yvalue[i];
	double error_eff100 = eff100_chargedist_IC_Yerror[i]/eff100_chargedist_IC_Yvalue[i];
	eff100_chargedist_IC_Yerror[i] = eff100_chargedist_IC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff100*error_eff100);
	eff100_chargedist_IC_Xvalue[i] = 0.5*(eff100_chargedist_IC_Xvalue[i]+data_chargedist_IC_Xvalue[i]);
}
TGraphErrors* eff100_ratio_IC = new TGraphErrors(data_chargedist_IC->GetN(),eff100_chargedist_IC_Xvalue,eff100_chargedist_IC_Yvalue,0,eff100_chargedist_IC_Yerror);

for(int i=0; i<n; ++i){
	eff110_chargedist_IC_Yvalue[i] /= data_chargedist_IC_Yvalue[i];
	double error_data = data_chargedist_IC_Yerror[i]/data_chargedist_IC_Yvalue[i];
	double error_eff110 = eff110_chargedist_IC_Yerror[i]/eff110_chargedist_IC_Yvalue[i];
	eff110_chargedist_IC_Yerror[i] = eff110_chargedist_IC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff110*error_eff110);
	eff110_chargedist_IC_Xvalue[i] = 0.5*(eff110_chargedist_IC_Xvalue[i]+data_chargedist_IC_Xvalue[i]);
}
TGraphErrors* eff110_ratio_IC = new TGraphErrors(data_chargedist_IC->GetN(),eff110_chargedist_IC_Xvalue,eff110_chargedist_IC_Yvalue,0,eff110_chargedist_IC_Yerror);

for(int i=0; i<n; ++i){
	eff120_chargedist_IC_Yvalue[i] /= data_chargedist_IC_Yvalue[i];
	double error_data = data_chargedist_IC_Yerror[i]/data_chargedist_IC_Yvalue[i];
	double error_eff120 = eff120_chargedist_IC_Yerror[i]/eff120_chargedist_IC_Yvalue[i];
	eff120_chargedist_IC_Yerror[i] = eff120_chargedist_IC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff120*error_eff120);
	eff120_chargedist_IC_Xvalue[i] = 0.5*(eff120_chargedist_IC_Xvalue[i]+data_chargedist_IC_Xvalue[i]);
}
TGraphErrors* eff120_ratio_IC = new TGraphErrors(data_chargedist_IC->GetN(),eff120_chargedist_IC_Xvalue,eff120_chargedist_IC_Yvalue,0,eff120_chargedist_IC_Yerror);


TGraphErrors* data_chargedist_DC = (TGraphErrors*) datafile_root->Get("Charge_Distance_DC");
double* data_chargedist_DC_Xvalue = data_chargedist_DC->GetX();
double* data_chargedist_DC_Yvalue = data_chargedist_DC->GetY();
double* data_chargedist_DC_Yerror = data_chargedist_DC->GetEY();
TGraphErrors* eff090_chargedist_DC = (TGraphErrors*) eff090_root->Get("Charge_Distance_DC");
double* eff090_chargedist_DC_Xvalue = eff090_chargedist_DC->GetX();
double* eff090_chargedist_DC_Yvalue = eff090_chargedist_DC->GetY();
double* eff090_chargedist_DC_Yerror = eff090_chargedist_DC->GetEY();
TGraphErrors* eff100_chargedist_DC = (TGraphErrors*) eff100_root->Get("Charge_Distance_DC");
double* eff100_chargedist_DC_Xvalue = eff100_chargedist_DC->GetX();
double* eff100_chargedist_DC_Yvalue = eff100_chargedist_DC->GetY();
double* eff100_chargedist_DC_Yerror = eff100_chargedist_DC->GetEY();
TGraphErrors* eff110_chargedist_DC = (TGraphErrors*) eff110_root->Get("Charge_Distance_DC");
double* eff110_chargedist_DC_Xvalue = eff110_chargedist_DC->GetX();
double* eff110_chargedist_DC_Yvalue = eff110_chargedist_DC->GetY();
double* eff110_chargedist_DC_Yerror = eff110_chargedist_DC->GetEY();
TGraphErrors* eff120_chargedist_DC = (TGraphErrors*) eff120_root->Get("Charge_Distance_DC");
double* eff120_chargedist_DC_Xvalue = eff120_chargedist_DC->GetX();
double* eff120_chargedist_DC_Yvalue = eff120_chargedist_DC->GetY();
double* eff120_chargedist_DC_Yerror = eff120_chargedist_DC->GetEY();

for(int i=0; i<n; ++i){
	eff090_chargedist_DC_Yvalue[i] /= data_chargedist_DC_Yvalue[i];
	double error_data = data_chargedist_DC_Yerror[i]/data_chargedist_DC_Yvalue[i];
	double error_eff090 = eff090_chargedist_DC_Yerror[i]/eff090_chargedist_DC_Yvalue[i];
	eff090_chargedist_DC_Yerror[i] = eff090_chargedist_DC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff090*error_eff090);
	eff090_chargedist_DC_Xvalue[i] = 0.5*(eff090_chargedist_DC_Xvalue[i]+data_chargedist_DC_Xvalue[i]);
}
TGraphErrors* eff090_ratio_DC = new TGraphErrors(data_chargedist_DC->GetN(),eff090_chargedist_DC_Xvalue,eff090_chargedist_DC_Yvalue,0,eff090_chargedist_DC_Yerror);

for(int i=0; i<n; ++i){
	eff100_chargedist_DC_Yvalue[i] /= data_chargedist_DC_Yvalue[i];
	double error_data = data_chargedist_DC_Yerror[i]/data_chargedist_DC_Yvalue[i];
	double error_eff100 = eff100_chargedist_DC_Yerror[i]/eff100_chargedist_DC_Yvalue[i];
	eff100_chargedist_DC_Yerror[i] = eff100_chargedist_DC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff100*error_eff100);
	eff100_chargedist_DC_Xvalue[i] = 0.5*(eff100_chargedist_DC_Xvalue[i]+data_chargedist_DC_Xvalue[i]);
}
TGraphErrors* eff100_ratio_DC = new TGraphErrors(data_chargedist_DC->GetN(),eff100_chargedist_DC_Xvalue,eff100_chargedist_DC_Yvalue,0,eff100_chargedist_DC_Yerror);

for(int i=0; i<n; ++i){
	eff110_chargedist_DC_Yvalue[i] /= data_chargedist_DC_Yvalue[i];
	double error_data = data_chargedist_DC_Yerror[i]/data_chargedist_DC_Yvalue[i];
	double error_eff110 = eff110_chargedist_DC_Yerror[i]/eff110_chargedist_DC_Yvalue[i];
	eff110_chargedist_DC_Yerror[i] = eff110_chargedist_DC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff110*error_eff110);
	eff110_chargedist_DC_Xvalue[i] = 0.5*(eff110_chargedist_DC_Xvalue[i]+data_chargedist_DC_Xvalue[i]);
}
TGraphErrors* eff110_ratio_DC = new TGraphErrors(data_chargedist_DC->GetN(),eff110_chargedist_IC_Xvalue,eff110_chargedist_IC_Yvalue,0,eff110_chargedist_IC_Yerror);

for(int i=0; i<n; ++i){
	eff120_chargedist_DC_Yvalue[i] /= data_chargedist_DC_Yvalue[i];
	double error_data = data_chargedist_DC_Yerror[i]/data_chargedist_DC_Yvalue[i];
	double error_eff120 = eff120_chargedist_DC_Yerror[i]/eff120_chargedist_DC_Yvalue[i];
	eff120_chargedist_DC_Yerror[i] = eff120_chargedist_DC_Yvalue[i]*TMath::Sqrt(error_data*error_data + error_eff120*error_eff120);
	eff120_chargedist_DC_Xvalue[i] = 0.5*(eff120_chargedist_DC_Xvalue[i]+data_chargedist_DC_Xvalue[i]);
}
TGraphErrors* eff120_ratio_DC = new TGraphErrors(data_chargedist_DC->GetN(),eff120_chargedist_DC_Xvalue,eff120_chargedist_DC_Yvalue,0,eff120_chargedist_DC_Yerror);


TH1F* data_allzenith = (TH1F*) datafile_root->Get("NotOnlySun");
//TH1F* data_allzenith = (TH1F*) datafile_root->Get("zenith_all");
data_allzenith->Scale(1.0/data_allzenith->GetBinContent(70));
data_allzenith->SetStats(0);
data_allzenith->SetLineColor(kBlack);
TH1F* eff090_allzenith = (TH1F*) eff090_root->Get("zenith_all");
eff090_allzenith->Scale(1./eff090_allzenith->GetBinContent(70));
eff090_allzenith->SetStats(0);
eff090_allzenith->SetLineColor(kRed);
TH1F* ratio_eff090_allzenith = (TH1F*) data_allzenith->Clone();
ratio_eff090_allzenith->Divide(eff090_allzenith);
TH1F* eff100_allzenith = (TH1F*) eff100_root->Get("zenith_all");
eff100_allzenith->Scale(1.0/eff100_allzenith->GetBinContent(70));
eff100_allzenith->SetStats(0); 
TH1F* ratio_eff100_allzenith = (TH1F*) data_allzenith->Clone();
ratio_eff100_allzenith->Divide(eff100_allzenith); 
TH1F* eff110_allzenith = (TH1F*) eff110_root->Get("zenith_all");
eff110_allzenith->Scale(1./eff110_allzenith->GetBinContent(70));
eff110_allzenith->SetStats(0);
TH1F* ratio_eff110_allzenith = (TH1F*) data_allzenith->Clone();
ratio_eff110_allzenith->Divide(eff110_allzenith);
TH1F* eff120_allzenith = (TH1F*) eff120_root->Get("zenith_all");
eff120_allzenith->Scale(1./eff120_allzenith->GetBinContent(70));
eff120_allzenith->SetStats(0);
TH1F* ratio_eff120_allzenith = (TH1F*) data_allzenith->Clone();
ratio_eff120_allzenith->Divide(eff120_allzenith);

TH1F* data_analysiszenith = (TH1F*) datafile_root->Get("Zenith_IC");
data_analysiszenith->Scale(1./data_analysiszenith->Integral());
data_analysiszenith->SetStats(0);
TH1F* eff090_analysiszenith = (TH1F*) eff090_root->Get("Zenith_IC");
eff090_analysiszenith->Scale(1./eff090_analysiszenith->Integral()) ;
eff090_analysiszenith->SetStats(0);
TH1F* ratio_eff090_analysiszenith = (TH1F*) data_analysiszenith->Clone();
ratio_eff090_analysiszenith->Divide(eff090_analysiszenith) ;
TH1F* eff100_analysiszenith = (TH1F*) eff100_root->Get("Zenith_IC");
eff100_analysiszenith->Scale(1./eff100_analysiszenith->Integral()); 
eff100_analysiszenith->SetStats(0);
TH1F* ratio_eff100_analysiszenith = (TH1F*) data_analysiszenith->Clone();
ratio_eff100_analysiszenith->Divide(eff100_analysiszenith); 
TH1F* eff110_analysiszenith = (TH1F*) eff110_root->Get("Zenith_IC");
eff110_analysiszenith->Scale(1./eff110_analysiszenith->Integral()) ;
eff110_analysiszenith->SetStats(0);
TH1F* ratio_eff110_analysiszenith = (TH1F*) data_analysiszenith->Clone();
ratio_eff110_analysiszenith->Divide(eff110_analysiszenith) ;
TH1F* eff120_analysiszenith = (TH1F*) eff120_root->Get("Zenith_IC");
eff120_analysiszenith->Scale(1./eff120_analysiszenith->Integral());
eff120_analysiszenith->SetStats(0);
TH1F* ratio_eff120_analysiszenith = (TH1F*) data_analysiszenith->Clone();
ratio_eff120_analysiszenith->Divide(eff120_analysiszenith) ;

TH1F* data_allimpact = (TH1F*) datafile_root->Get("ImpactAll_IC");
data_allimpact->Scale(1./data_allimpact->Integral());
data_allimpact->SetStats(0);
TH1F* eff090_allimpact = (TH1F*) eff090_root->Get("ImpactAll_IC");
eff090_allimpact->Scale(1./eff090_allimpact->Integral());
eff090_allimpact->SetStats(0);
TH1F* ratio_eff090_allimpact = (TH1F*) data_allimpact->Clone();
ratio_eff090_allimpact->Divide(eff090_allimpact);
TH1F* eff100_allimpact = (TH1F*) eff100_root->Get("ImpactAll_IC");
eff100_allimpact->Scale(1./eff100_allimpact->Integral());
eff100_allimpact->SetStats(0);
TH1F* ratio_eff100_allimpact = (TH1F*) data_allimpact->Clone();
ratio_eff100_allimpact->Divide(eff100_allimpact);
TH1F* eff110_allimpact = (TH1F*) eff110_root->Get("ImpactAll_IC");
eff110_allimpact->Scale(1./eff110_allimpact->Integral());
eff110_allimpact->SetStats(0);
TH1F* ratio_eff110_allimpact = (TH1F*) data_allimpact->Clone();
ratio_eff110_allimpact->Divide(eff110_allimpact);
TH1F* eff120_allimpact = (TH1F*) eff120_root->Get("ImpactAll_IC");
eff120_allimpact->Scale(1./eff120_allimpact->Integral());
eff120_allimpact->SetStats(0);
TH1F* ratio_eff120_allimpact = (TH1F*) data_allimpact->Clone();
ratio_eff120_allimpact->Divide(eff120_allimpact);

TH1F* data_peimpact = (TH1F*) datafile_root->Get("ImpactseeMPE_IC");
data_peimpact->Scale(1./data_peimpact->Integral());
data_peimpact->SetStats(0);
TH1F* eff090_peimpact = (TH1F*) eff090_root->Get("ImpactseeMPE_IC");
eff090_peimpact->Scale(1./eff090_peimpact->Integral());
eff090_peimpact->SetStats(0);
TH1F* ratio_eff090_peimpact = (TH1F*) data_peimpact->Clone();
ratio_eff090_peimpact->Divide(eff090_peimpact) ;
TH1F* eff100_peimpact = (TH1F*) eff100_root->Get("ImpactseeMPE_IC");
eff100_peimpact->Scale(1./eff100_peimpact->Integral());
eff100_peimpact->SetStats(0);
TH1F* ratio_eff100_peimpact = (TH1F*) data_peimpact->Clone();
ratio_eff100_peimpact->Divide(eff100_peimpact) ;
TH1F* eff110_peimpact = (TH1F*) eff110_root->Get("ImpactseeMPE_IC");
eff110_peimpact->Scale(1./eff110_peimpact->Integral());
eff110_peimpact->SetStats(0);
TH1F* ratio_eff110_peimpact = (TH1F*) data_peimpact->Clone();
ratio_eff110_peimpact->Divide(eff110_peimpact) ;
TH1F* eff120_peimpact = (TH1F*) eff120_root->Get("ImpactseeMPE_IC");
eff120_peimpact->Scale(1./eff120_peimpact->Integral());
eff120_peimpact->SetStats(0);
TH1F* ratio_eff120_peimpact = (TH1F*) data_peimpact->Clone();
ratio_eff120_peimpact->Divide(eff120_peimpact);

TH1F* data_endpointx = (TH1F*) datafile_root->Get("EndPointX_IC");
data_endpointx->Scale(1./data_endpointx->GetMaximum());
data_endpointx->SetStats(0);
TH1F* eff090_endpointx = (TH1F*) eff090_root->Get("EndPointX_IC");
eff090_endpointx->Scale(1./eff090_endpointx->GetMaximum());
eff090_endpointx->SetStats(0);
TH1F* ratio_eff090_endpointx = (TH1F*) data_endpointx->Clone();
ratio_eff090_endpointx->Divide(eff090_endpointx) ;
TH1F* eff100_endpointx = (TH1F*) eff100_root->Get("EndPointX_IC");
eff100_endpointx->Scale(1./eff100_endpointx->GetMaximum());
eff100_endpointx->SetStats(0);
TH1F* ratio_eff100_endpointx = (TH1F*) data_endpointx->Clone();
ratio_eff100_endpointx->Divide(eff100_endpointx) ;
TH1F* eff110_endpointx = (TH1F*) eff110_root->Get("EndPointX_IC");
eff110_endpointx->Scale(1./eff110_endpointx->GetMaximum());
eff110_endpointx->SetStats(0);
TH1F* ratio_eff110_endpointx = (TH1F*) data_endpointx->Clone();
ratio_eff110_endpointx->Divide(eff110_endpointx) ;
TH1F* eff120_endpointx = (TH1F*) eff120_root->Get("EndPointX_IC");
eff120_endpointx->Scale(1./eff120_endpointx->GetMaximum());
eff120_endpointx->SetStats(0);
TH1F* ratio_eff120_endpointx = (TH1F*) data_endpointx->Clone();
ratio_eff120_endpointx->Divide(eff120_endpointx);

TH1F* data_boarderdist = (TH1F*) datafile_root->Get("BoarderDist_IC");
data_boarderdist->Scale(1./data_boarderdist->GetMaximum());
data_boarderdist->SetStats(0);
TH1F* eff090_boarderdist = (TH1F*) eff090_root->Get("BoarderDist_IC");
eff090_boarderdist->Scale(1./eff090_boarderdist->GetMaximum());
eff090_boarderdist->SetStats(0);
TH1F* ratio_eff090_boarderdist = (TH1F*) data_boarderdist->Clone();
ratio_eff090_boarderdist->Divide(eff090_boarderdist) ;
TH1F* eff100_boarderdist = (TH1F*) eff100_root->Get("BoarderDist_IC");
eff100_boarderdist->Scale(1./eff100_boarderdist->GetMaximum());
eff100_boarderdist->SetStats(0);
TH1F* ratio_eff100_boarderdist = (TH1F*) data_boarderdist->Clone();
ratio_eff100_boarderdist->Divide(eff100_boarderdist) ;
TH1F* eff110_boarderdist = (TH1F*) eff110_root->Get("BoarderDist_IC");
eff110_boarderdist->Scale(1./eff110_boarderdist->GetMaximum());
eff110_boarderdist->SetStats(0);
TH1F* ratio_eff110_boarderdist = (TH1F*) data_boarderdist->Clone();
ratio_eff110_boarderdist->Divide(eff110_boarderdist) ;
TH1F* eff120_boarderdist = (TH1F*) eff120_root->Get("BoarderDist_IC");
eff120_boarderdist->Scale(1./eff120_boarderdist->GetMaximum());
eff120_boarderdist->SetStats(0);
TH1F* ratio_eff120_boarderdist = (TH1F*) data_boarderdist->Clone();
ratio_eff120_boarderdist->Divide(eff120_endpointx) ;

TFile* fout = new TFile("RatioPlots_lowe.root","RECREATE");

eff090_ratio_IC->Write("eff090_ratio_IC");
eff100_ratio_IC->Write("eff100_ratio_IC");
eff110_ratio_IC->Write("eff110_ratio_IC");
eff120_ratio_IC->Write("eff120_ratio_IC");

eff090_ratio_DC->Write("eff090_ratio_DC");
eff100_ratio_DC->Write("eff100_ratio_DC");
eff110_ratio_DC->Write("eff110_ratio_DC");
eff120_ratio_DC->Write("eff120_ratio_DC");

data_allzenith->Write("data_allzenith");
eff090_allzenith->Write("eff090_allzenith"); 
ratio_eff090_allzenith->Write("ratio_eff090_allzenith");
eff100_allzenith->Write("eff100_allzenith");
ratio_eff100_allzenith->Write("ratio_eff100_allzenith");
eff110_allzenith->Write("eff110_allzenith");
ratio_eff110_allzenith->Write("ratio_eff110_allzenith");
eff120_allzenith->Write("eff120_allzenith");
ratio_eff120_allzenith->Write("ratio_eff120_allzenith");

data_analysiszenith->Write("data_analysiszenith");
eff090_analysiszenith->Write("eff090_analysiszenith");
ratio_eff090_analysiszenith->Write("ratio_eff090_analysiszenith");
eff100_analysiszenith->Write("eff100_analysiszenith");
ratio_eff100_analysiszenith->Write("ratio_eff100_analysiszenith");
eff110_analysiszenith->Write("eff110_analysiszenith");
ratio_eff110_analysiszenith->Write("ratio_eff110_analysiszenith");
eff120_analysiszenith->Write("eff120_analysiszenith");
ratio_eff120_analysiszenith->Write("ratio_eff120_analysiszenith");

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
ratio_eff120_endpointx->Write("ratio_eff120_boarderdist");

fout->Close();

}


