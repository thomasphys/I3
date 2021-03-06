#!/usr/bin/env python
import os, sys
import subprocess

basefolder = "datahd5/"
folderlist = ['Run00125791','Run00125827','Run00125872','Run00125915','Run00125939','Run00125963','Run00125982','Run00126001','Run00126034','Run00126479',
				'Run00125801','Run00125860','Run00125899','Run00125916','Run00125940','Run00125964','Run00125983','Run00126002','Run00126052','Run00126552',
				'Run00125792','Run00125828','Run00125890','Run00125917','Run00125942','Run00125965','Run00125984','Run00126003','Run00126061','Run00126572',
				'Run00125802','Run00125861','Run00125900','Run00125918','Run00125943','Run00125966','Run00125985','Run00126004','Run00126062','Run00126706',
				'Run00125793','Run00125829','Run00125891','Run00125919','Run00125944','Run00125967','Run00125986','Run00126005','Run00126069','Run00126750',
				'Run00125803','Run00125862','Run00125901','Run00125922','Run00125946','Run00125968','Run00125987','Run00126006','Run00126070','Run00126751',				
				'Run00125794','Run00125831','Run00125892','Run00125923','Run00125947','Run00125969','Run00125988','Run00126007','Run00126072','Run00127186',
				'Run00125820','Run00125863','Run00125902','Run00125924','Run00125948','Run00125970','Run00125989','Run00126008','Run00126073',
				'Run00125795','Run00125832','Run00125893','Run00125925','Run00125949','Run00125971','Run00125990','Run00126009','Run00126085',
				'Run00125821','Run00125864','Run00125903','Run00125926','Run00125950','Run00125972','Run00125991','Run00126015','Run00126091',
				'Run00125796','Run00125833','Run00125894','Run00125904','Run00125927','Run00125951','Run00125973','Run00125992','Run00126016','Run00126093',
				'Run00125822','Run00125868','Run00125905','Run00125928','Run00125952','Run00125974','Run00125993','Run00126017','Run00126094',
				'Run00125797','Run00125856','Run00125895','Run00125906','Run00125929','Run00125954','Run00125975','Run00125994','Run00126018','Run00126107',
				'Run00125824','Run00125869','Run00125908','Run00125930','Run00125955','Run00125976','Run00125995','Run00126026','Run00126113',
				'Run00125798','Run00125857','Run00125896','Run00125909','Run00125933','Run00125956','Run00125977','Run00125996','Run00126027','Run00126120',
				'Run00125825','Run00125870','Run00125910','Run00125934','Run00125957','Run00125978','Run00125997','Run00126028','Run00126135',
				'Run00125799','Run00125858','Run00125897','Run00125911','Run00125935','Run00125960','Run00125979','Run00125998','Run00126029','Run00126138',
				'Run00125826','Run00125871','Run00125913','Run00125936','Run00125961','Run00125980','Run00125999','Run00126030','Run00126139',
				'Run00125800','Run00125859','Run00125898','Run00125914','Run00125938','Run00125962','Run00125981','Run00126000','Run00126032','Run00126384']
#flux = "data"

#for folder in folderlist :
#	submit = subprocess.Popen(['mv','/data/user/tmcelroy/domeff/datahd5/'+folder+".h5",'/data/user/tmcelroy/domeff/datahd5/'+folder+"all.h5"])
#	submit.wait()

#folderlist = ['eff090','eff100','eff110','eff120']
#for folder in folderlist :
#	submit = subprocess.Popen(['mv','/data/user/tmcelroy/domeff/hd5/'+folder+".h5",'/data/user/tmcelroy/domeff/datahd5/'+folder+"all.h5"])
#	submit.wait()


basefolder = "hd5/"
folderlist = ['eff090all','eff090lowE','eff090highE','eff100all','eff100lowE','eff100highE','eff110all','eff110lowE','eff110highE','eff120all','eff120lowE','eff120highE']
flux = "GaisserH4a"

submit = subprocess.Popen(['python','ComputeChargeDist.py','-e', "all",  '-d', '/data/user/tmcelroy/domeff/datahd5', '-o', '/data/user/tmcelroy/domeff/datahd5/AllRuns_ChargeDist_all'])
submit.wait()
submit = subprocess.Popen(['python','ComputeChargeDist.py','-e', "lowE",  '-d', '/data/user/tmcelroy/domeff/datahd5', '-o', '/data/user/tmcelroy/domeff/datahd5/AllRuns_ChargeDist_lowE'])
submit.wait()
submit = subprocess.Popen(['python','ComputeChargeDist.py','-e', "highE",  '-d', '/data/user/tmcelroy/domeff/datahd5', '-o', '/data/user/tmcelroy/domeff/datahd5/AllRuns_ChargeDist_highE'])
submit.wait()

for folder in folderlist :
	if os.path.isfile('/data/user/tmcelroy/domeff/hd5/'+folder+"_ChargeDist.h5") :
		continue
	submit = subprocess.Popen(['python','ComputeChargeDist.py','-e', folder,  '-d', '/data/user/tmcelroy/domeff/hd5/', '-o', '/data/user/tmcelroy/domeff/hd5/'+folder+"_ChargeDist"])
	submit.wait()
	
