# coding: utf-8 
#from __future__ import unicode_literals
from bs4 import BeautifulSoup
import urllib
import re
import time
from nvd3 import lineChart
from nvd3 import stackedAreaChart
from operator import itemgetter, attrgetter, methodcaller
from datetime import date
from datetime import datetime
from datetime import date
class arrete:
    ''''''
    def __init__(self,url):
        self.year=datetime(1970,1,1)
        self.classe=""
        self.url=url
        self.postes={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0,24:0,25:0,26:0,27:0,28:0,29:0,30:0,31:0,32:0,33:0,34:0,35:0,36:0,37:0,38:0,39:0,40:0,41:0,42:0,43:0,44:0,45:0,46:0,47:0,48:0,51:0,52:0,53:0,54:0}
        
    def __str__(self):
        return  "Arrêté postes CNRS Année %s, classe %s" % (self.year, self.classe)


    def postescnrs(self):
        #tableau avec les nouveaux postes pour l'année de l'arrêté, indicé par numéro de section ou de commission interdisciplinaire
        #table={}
        #ouverture de l'arrêté sur legifrance
        
#        <title>
#			Arrêté du 13 novembre 2015 autorisant au titre de l'année 2016 l'ouverture de concours sur titres et travaux pour le recrutement de chargés de recherche de 1re classe du Centre national de la recherche scientifique (CNRS) | Legifrance</title>

        
        r = urllib.request.urlopen(self.url).read()
        soup = BeautifulSoup(r,'lxml')
        body=soup.find('body')
        title=soup.find('title')
        expressionTitle=r".*Arrêté du.* (?P<datePubli>[0-9]+) autorisant.*recrutement de chargés de recherche de (?P<classe>[0-9]+).*"
        p = re.compile(expressionTitle)    
        titleData=re.search(p, str(title))
        if titleData is not None:
            self.year=datetime(int(titleData.group('datePubli')),1,1)
            self.classe=titleData.group('classe')
        #Récupération du document coupé selon les sections
        sections=re.split("Section ",str(body),flags=re.S)
        total=0
        for section in sections:
            #Pour chaque section, on récupère son numéro et on vire les retours à la ligne
            expression=r"^([0-9]+)(.*)"
            p = re.compile(expression)  
            sectionTable=re.findall(p,section.replace('\n',''))
            totalSection=0
            if len(sectionTable)>0:
                text=sectionTable[0][1]
                #On a coupé par section mais on a aussi des commissions interdisciplinaires. Récupérons dans les sections!
                commissions=re.split("Commission interdisciplinaire",str(sectionTable[0]),flags=re.S)
                #Si on a des commissions, il faut les intégrer au tableau
                if len(commissions)>1:
                    for commission in commissions[1:]:
                        totalComm=0
                        #recupération du numéro de commission
                        expression=r".*n° +(?P<numComm>[0-9]+).*"
                        p = re.compile(expression)  
                        comm=re.search(p, commission)
                        if comm is not None:
                            numComm=comm.group('numComm')   
                            #On compte le nombre de postes attribués à la commission
                            postesTable=re.findall(r"N° *[0-9]+/[0-9]+[ .-]*[0-9]+", commission)
                            for postes in postesTable:
                                nbrPostes=re.match(r"N° *[0-9]+/[0-9]+[ .-]*([0-9]+)",postes)
                                totalComm=totalComm+int(nbrPostes.group(1))
                            total=total+totalComm
                            #On attribue à l'indice du tableau correspondant au numéro de commission le nombre de postes attribués
                            self.postes[int(numComm)]=totalComm
                    #On supprime de la section toutes les commissions        
                    text=commissions[0]                          
                #On compte le nombre de postes attribués à la Section    
                postesTable=re.findall(r"N° *[0-9]+/[0-9]+[ .-]*[0-9]+", text)
                for postes in postesTable:
                    nbrPostes=re.match(r"N° *[0-9]+/[0-9]+[ .-]*([0-9]+)",postes)
                    totalSection=totalSection+int(nbrPostes.group(1))
                #On attribue à l'indice du tableau correspondant au numéro de commission le nombre de postes attribués    
                self.postes[int(sectionTable[0][0])]=totalSection
            total=total+totalSection
        self.postes["total"]=total
        return self.postes



#{1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0,24:0,25:0,26:0,27:0,28:0,29:0,30:0,31:0,32:0,33:0,34:0,35:0,36:0,37:0,38:0,39:0,40:0,41:0,42:0,43:0,44:0,45:0,46:0,47:0,48:0,51:0,52:0,53:0,54:0}    
a=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000033480025&dateTexte=&categorieLien=id")
b=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000033480019&dateTexte=&categorieLien=id")
c=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000031490422&dateTexte=&categorieLien=id")
d=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000031490420&dateTexte=&categorieLien=id")
e=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000029813331")
f=arrete("https://www.legifrance.gouv.fr/eli/arrete/2014/11/28/MENZ1401228A/jo")
g=arrete("https://www.legifrance.gouv.fr/affichTexte.do;jsessionid=BEBA6FEC29B8F77879D8D969E3C03AD9.tpdila12v_1?cidTexte=JORFTEXT000028254219&dateTexte=&oldAction=rechJO&categorieLien=id&idJO=JORFCONT000028253873")
h=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000028254221&dateTexte=&categorieLien=id")
i=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000026706545&dateTexte=&categorieLien=id")
j=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000026706549&dateTexte=&categorieLien=id")
k=arrete("https://www.legifrance.gouv.fr/affichTexte.do;jsessionid=21FA7807711039CC01C3F0495E63C172.tpdila18v_3?cidTexte=JORFTEXT000024874335&dateTexte=&oldAction=rechJO&categorieLien=id&idJO=JORFCONT000024873109")
l=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000024874337&dateTexte=&categorieLien=id")
m=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000023149440")
n=arrete("https://www.legifrance.gouv.fr/affichTexte.do;jsessionid=94074D80BF1B2F67F44A9954C071179B.tpdila22v_1?cidTexte=JORFTEXT000023149444&dateTexte=&oldAction=rechJO&categorieLien=id&idJO=JORFCONT000023149317")
o=arrete("https://www.legifrance.gouv.fr/affichTexte.do;jsessionid=ADF7A19107CADD7CD34A852F28C4B7DD.tpdila13v_2?cidTexte=JORFTEXT000021358052&dateTexte=&oldAction=rechJO&categorieLien=id&idJO=JORFCONT000021357990")
p=arrete("https://www.legifrance.gouv.fr/eli/arrete/2009/11/10/ESRZ0900458A/jo")
q=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000019857342&dateTexte=")
r=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000019857344&categorieLien=id")
s=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000017572706&categorieLien=id")
t=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000017572708&categorieLien=id")
u=arrete("https://www.legifrance.gouv.fr/affichTexte.do;jsessionid=74DB883A02229D7A7258060ACDB6E500.tpdila13v_3?cidTexte=JORFTEXT000000241564&categorieLien=id")
v=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000000790865")
w=arrete("https://www.legifrance.gouv.fr/eli/arrete/2005/11/22/RECZ0500201A/jo/texte")
x=arrete("https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000000607247&categorieLien=id")

    
arretes=[a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x]
#Pour chaque arrete on récupère les infos et on stocke
for arret in arretes:
    arret.postescnrs()  
#On trie par année
arretesSorted=sorted(arretes, key=attrgetter('year')) 


xdata=[]
ysdata={}
    
sections=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,51,52,53,54]
for section in sections:
    ysdata[section]=[]
    
for arret in arretesSorted:
    if arret.classe=="1":       
        
        xdata.append(time.mktime(arret.year.timetuple())*1000)
        for section in arret.postes:
            if section is not "total":
                ysdata[section].append(arret.postes[section])     
    else:
        for section in arret.postes:
            if section is not "total":
                #ysdata[section].append(arret.postes[section])     
                ysdata[section][-1]=ysdata[section][-1]+arret.postes[section]
            

chart = stackedAreaChart(name='stackedAreaChart', height=800, width=1024, x_is_date=True,, x_axis_format="%d %b %Y")
#extra_serie = {"tooltip": {"y_start": "", "y_end": " ext"},"date_format":"%d %b %Y"}
extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " min"},"date_format":"%Y"}

for ydata in ysdata:
    if ydata is not 'total' :
        chart.add_serie(name="Section "+str(ydata), y=ysdata[ydata], x=xdata, extra=extra_serie)
        
chart.buildhtml()
fo = open("cnrs-hiring.html", "w")
fo.write(chart.htmlcontent)
fo.close()