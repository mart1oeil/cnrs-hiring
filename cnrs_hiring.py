# coding: utf-8 
from bs4 import BeautifulSoup
import urllib
import re
import time
from operator import attrgetter
import json

class arreteCR:
    ''''''
    def __init__(self,url):
        self.year=1970
        self.classe=""
        self.url=url
        self.postes={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0,24:0,25:0,26:0,27:0,28:0,29:0,30:0,31:0,32:0,33:0,34:0,35:0,36:0,37:0,38:0,39:0,40:0,41:0,"Interdisciplinaires":0}
        
    def __str__(self):
        return  "Arrêté postes CNRS Année %s, classe %s" % (self.year, self.classe)


    def postescnrs(self):
        #ouverture de l'arrêté sur legifrance        
        r = urllib.request.urlopen(self.url).read()
        soup = BeautifulSoup(r,'lxml')
        body=soup.find('body')
        title=soup.find('title')
        # récupération de la date
        expressionTitle=r".*autorisant au titre de l'année (?P<datePubli>[0-9]+) .*"
        p = re.compile(expressionTitle)    
        titleData=re.search(p, str(title))
        #récupération de la classe
        expressionTitle2=".*recrutement de chargés de recherche de (?P<classe>[0-9]+).*"   
        p2 = re.compile(expressionTitle2)    
        titleData2=re.search(p2, str(title))        
        print(self.url)
        if titleData is not None:
            self.year=int(titleData.group('datePubli'))
            print(self.year)
            
        if titleData2 is not None:            
            self.classe=titleData2.group('classe')
            print(self.classe)
        else:
            self.classe='classe normale'

            
        # correspondance sections avant 2013 et après 2013
        correspondances={1:41,3:1,6:3,7:[6,7],20:30,21:20,22:21,23:22,24:[24,25,27],25:24,26:22,27:26,28:23,30:28}

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
                            self.postes["Interdisciplinaires"]=self.postes["Interdisciplinaires"]+totalComm
                    #On supprime de la section toutes les commissions        
                    text=commissions[0]                          
                
                #On compte le nombre de postes attribués à la Section    
                postesTable=re.findall(r"N° *[0-9]+/[0-9]+[ .-]*[0-9]+", text)
                for postes in postesTable:
                    nbrPostes=re.match(r"N° *[0-9]+/[0-9]+[ .-]*([0-9]+)",postes)
                    totalSection=totalSection+int(nbrPostes.group(1))
                numSection=int(sectionTable[0][0])
                # On attribue à l'indice du tableau correspondant au numéro de section le nombre de postes attribués  
                # En prenant compte du tableau des correspondances de sections avant 2013
                
                
                if self.year<2013 and  (numSection in correspondances):
                    
                    #si les postes sont redistrubés dans plusieurs sections, on redistribue 
                    if type(correspondances[numSection]).__name__ == 'list':
                        #redistribution équiproportionnelle
                        postescorresp=totalSection/len(correspondances[numSection])
                        postescorresp = totalSection // len(correspondances[numSection])
                        nbReste = totalSection % len(correspondances[numSection])
                        for newSection in correspondances[numSection]:
                            self.postes[newSection]=self.postes[newSection]+postescorresp
                        #ajout du relicat de la redistribution à la dernière section
                        self.postes[correspondances[numSection][-1]]=self.postes[correspondances[numSection][-1]]+nbReste
                    # sinon on ajoute à la section correspondante
                    else:
                        self.postes[correspondances[numSection]]=self.postes[correspondances[numSection]]+totalSection
                        
                else:                      
                    self.postes[numSection]=self.postes[numSection]+totalSection
                    
            total=total+totalSection
        self.postes["total"]=total
        return self.postes

# Liste des urls des arrêtés de création de poste de chargé de recherche au CNRS
urlsArretesCR=[]
with open("arretes-cnrs.txt","r") as arretesFile:
    urlsArretesCR=arretesFile.read().splitlines()
    


arretesCR=[]
#Pour chaque arrete on récupère les infos et on stocke
for urlArret in urlsArretesCR:
    arret=arreteCR(urlArret)
    arret.postescnrs()  
    arretesCR.append(arret)
#On trie par année
arretesCRSorted=sorted(arretesCR, key=attrgetter('year')) 
jsontab=[]
jsonTabClasse1=[]
jsonTabClasse2=[]

sectionsdico={1:"Interactions, particules, noyaux, du laboratoire au cosmos",2:"Théories physiques : méthodes, modèles et applications",3:"Matière condensée : structures et propriétés électroniques",4:"Atomes et molécules, optique et lasers, plasmas chauds",5:"Matière condensée : organisation et dynamique",6:"Sciences de l'information : fondements de l'informatique, calculs, algorithmes, représentations, exploitations",7:"Sciences de l'information : signaux, images, langues, automatique, robotique, interactions, systèmes intégrés matériel-logiciel",8:"Micro- et nanotechnologies, micro- et nanosystèmes, photonique, électronique, électromagnétisme, énergie électrique",9:"Mécanique des solides. Matériaux et structures. Biomécanique. Acoustique",10:"Milieux fluides et réactifs : transports, transferts, procédés de transformation",11:"Systèmes et matériaux supra et macromoléculaires : élaboration, propriétés, fonctions",12:"Architectures moléculaires : synthèses, mécanismes et propriétés",13:"Chimie physique, théorique et analytique",14:"Chimie de coordination, catalyse, interfaces et procédés",15:"Chimie des matériaux, nanomatériaux et procédés",16:"Chimie et vivant",17:"Système solaire et univers lointain",18:"Terre et planètes telluriques : structure, histoire, modèles",19:"Système terre : enveloppes superficielles",20:"Biologie moléculaire et structurale, biochimie",21:"Organisation, expression, évolution des génomes. Bioinformatique et biologie des systèmes",22:"Biologie cellulaire, développement, évolution-développement",23:"Biologie végétale intégrative",24:"Physiologie, vieillissement, tumorigenèse",25:"Neurobiologie moléculaire et cellulaire, neurophysiologie",26:"Cerveau, cognition, comportement",27:"Relations hôte-pathogène, immunologie, inflammation",28:"Pharmacologie-ingénierie et technologies pour la santé-imagerie biomédicale",29:"Biodiversité, évolution et adaptations biologiques : des macromolécules aux communautés",30:"Surface continentale et interfaces",31:"Hommes et milieux : évolution, interactions",32:"Mondes anciens et médiévaux",33:"Mondes modernes et contemporains",34:"Sciences du langage",35:"Sciences philosophiques et philologiques, sciences de l'art",36:"Sociologie et sciences du droit",37:"Economie et gestion",38:"Anthropologie et étude comparative des sociétés contemporaines",39:"Espaces, territoires et sociétés",40:"Politique, Pouvoir, Organisation",41:"Mathématiques et interactions des mathématiques","Interdisciplinaires":"Commissions interdisciplinaires"}


#Création de l'arborescence des json
for numsection,namesection  in sectionsdico.items():   
    if numsection == "Interdisciplinaires":
        key=numsection
    else:
        key="Section "+str(numsection)
    jsonSec={"key": key,"name": namesection,"values":[]}
    jsonSecClasse1={"key": key,"name": namesection,"values":[]}
    jsonSecClasse2={"key": key,"name": namesection,"values":[]}
    for arret in arretesCRSorted:
        if arret.classe=="1": 
            jsonSec["values"].append([arret.year,arret.postes[numsection]])
            jsonSecClasse1["values"].append([arret.year,arret.postes[numsection]])
        elif arret.classe=="2":           
            classe1=jsonSec["values"][-1][-1]
            classe2=classe1+arret.postes[numsection]
            jsonSec["values"][-1]=[arret.year,classe2]
            jsonSecClasse2["values"].append([arret.year,arret.postes[numsection]])
        elif arret.classe=="classe normale":
             jsonSec["values"].append([arret.year,arret.postes[numsection]])            
    jsontab.append(jsonSec)
    jsonTabClasse1.append(jsonSecClasse1)
    jsonTabClasse2.append(jsonSecClasse2)
    
with open("postes-CR-CNRS.json","w") as out_file:
    json.dump(jsontab,out_file, indent=4)     
    
with open("postes-CR-CNRS-Classe1.json","w") as out_file:
    json.dump(jsonTabClasse1,out_file, indent=4)   
    
with open("postes-CR-CNRS-Classe2.json","w") as out_file:
    json.dump(jsonTabClasse2,out_file, indent=4)   
