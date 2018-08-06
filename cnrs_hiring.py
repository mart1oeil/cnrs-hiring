# coding: utf-8

'''
Ce module permet de connaitre l'évolution de la
création de poste de chercheurs au CNRS.
'''

import json
from operator import attrgetter
import urllib
import re
from bs4 import BeautifulSoup

class ArreteCR:
    '''
    Un arreteCR est une page web de legifrance créée chaque année
    qui contient le nombre de création de postes pour chaque section.
    '''
    def __init__(self, url):
        self.year = 1970
        self.classe = ""
        self.url = url
        self.postes = ({1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0,
                        12:0, 13:0, 14:0, 15:0, 16:0, 17:0, 18:0, 19:0, 20:0, 21:0, 22:0, 23:0,
                        24:0, 25:0, 26:0, 27:0, 28:0, 29:0, 30:0, 31:0, 32:0, 33:0, 34:0, 35:0,
                        36:0, 37:0, 38:0, 39:0, 40:0, 41:0, "Interdisciplinaires":0, "Total":0})

    def __str__(self):
        return  "Arrêté postes CNRS Année %s, classe %s" % (self.year, self.classe)

    def attib_postes(self, num_section, total_section):
        '''
        On attribue à l'indice du tableau correspondant
        au numéro de section le nombre de postes attribués
        En prenant compte du tableau des corresps
        de sections avant 2013
        '''
        # correspondance sections avant 2013 et après 2013
        corresps = ({1:41, 3:1, 6:3, 7:[6, 7], 20:30, 21:20, 22:21, 23:22, 24:[24, 25, 27],
                     25:24, 26:22, 27:26, 28:23, 30:28})

        if self.year < 2013 and  (num_section in corresps):

            #si les postes sont redistrubés dans plusieurs sections, on redistribue
            if type(corresps[num_section]).__name__ == 'list':
                #redistribution équiproportionnelle
                postescorresp = total_section/len(corresps[num_section])
                postescorresp = total_section // len(corresps[num_section])
                nb_reste = total_section % len(corresps[num_section])
                for new_section in corresps[num_section]:
                    self.postes[new_section] = self.postes[new_section]+postescorresp
                #ajout du relicat de la redistribution à la dernière section
                self.postes[corresps[num_section][-1]] = (self.postes[corresps[num_section][-1]]
                                                          +nb_reste)
            # sinon on ajoute à la section correspondante
            else:
                self.postes[corresps[num_section]] = (self.postes[corresps[num_section]]
                                                      +total_section)
        else:
            self.postes[num_section] = self.postes[num_section]+total_section
        self.postes["Total"] = self.postes["Total"] + total_section

    def fill_commissions(self, section_table):
        '''
        Traite l'existance des commissions interdisciplinaires
        '''
        text = section_table[0][1]
        commissions = (re.split("Commission interdisciplinaire",
                                str(section_table[0]), flags=re.S))
        #Si on a des commissions, il faut les intégrer au tableau
        if len(commissions) > 1:
            for commission in commissions[1:]:
                total_comm = 0
                #recupération du numéro de commission
                expression = r".*n° +(?P<numComm>[0-9]+).*"
                exp_comm = re.compile(expression)
                comm = re.search(exp_comm, commission)
                if comm is not None:
                    #On compte le nombre de postes attribués à la commission
                    postes_table = re.findall(r"N° *[0-9]+/[0-9]+[ .-]*[0-9]+", commission)
                    for postes in postes_table:
                        nbr_postes = re.match(r"N° *[0-9]+/[0-9]+[ .-]*([0-9]+)", postes)
                        total_comm = total_comm+int(nbr_postes.group(1))
                    self.postes["Total"] = self.postes["Total"] + total_comm
                    # On attribue à l'indice du tableau correspondant
                    # au numéro de commission le nombre de postes attribués
                    self.postes["Interdisciplinaires"] = (self.postes["Interdisciplinaires"]
                                                          +total_comm)
            text = commissions[0]
        return text

    def fill_section(self, section):
        '''
        cette méthode remplie le tableau pour la section donnée
        il retourne le total de postes calculé.
        '''
        #Pour chaque section, on récupère son numéro et on vire les retours à la ligne
        exp = r"^([0-9]+)(.*)"
        exp = re.compile(exp)
        section_table = re.findall(exp, section.replace('\n', ''))
        total_section = 0

        if section_table:
            text = self.fill_commissions(section_table)
            #On compte le nombre de postes attribués à la Section
            postes_table = re.findall(r"N° *[0-9]+/[0-9]+[ .-]*[0-9]+", text)
            for postes in postes_table:
                nbr_postes = re.match(r"N° *[0-9]+/[0-9]+[ .-]*([0-9]+)", postes)
                total_section = total_section+int(nbr_postes.group(1))
            num_section = int(section_table[0][0])
            # on attribue les postes à la section en cours
            self.attib_postes(num_section, total_section)
        self.postes["Total"] = self.postes["Total"] + total_section


    def postes_cnrs(self):
        '''
        Cette méthode permet de récupérer les nombres de postes dans un arrêté et
        à les attribuer à chaque section dans le tableau des postes.
        '''
        #ouverture de l'arrêté sur legifrance
        req = urllib.request.urlopen(self.url).read()
        soup = BeautifulSoup(req, 'lxml')
        body = soup.find('body')
        title = soup.find('title')
        # récupération de la date
        expression_title = r".*autorisant au titre de l'année (?P<datePubli>[0-9]+) .*"
        exp_title = re.compile(expression_title)
        title_data = re.search(exp_title, str(title))
        #récupération de la classe
        expression_title2 = ".*recrutement de chargés de recherche de (?P<classe>[0-9]+).*"
        exp_title2 = re.compile(expression_title2)
        title_data2 = re.search(exp_title2, str(title))
        if title_data is not None:
            self.year = int(title_data.group('datePubli'))

        if title_data2 is not None:
            self.classe = title_data2.group('classe')
        else:
            self.classe = 'classe normale'
        #Récupération du document coupé selon les sections
        sections = re.split("Section ", str(body), flags=re.S)
        for section in sections:
            self.fill_section(section)
        return self.postes

SECTIONS_DICO = ({1:"Interactions, particules, noyaux, du laboratoire au cosmos",
                  2:"Théories physiques : méthodes, modèles et applications",
                  3:"Matière condensée : structures et propriétés électroniques",
                  4:"Atomes et molécules, optique et lasers, plasmas chauds",
                  5:"Matière condensée : organisation et dynamique",
                  6:"Sciences de l'information : fondements de l'informatique, calculs,\
                  algorithmes, représentations, exploitations",
                  7:"Sciences de l'information : signaux, images, langues, automatique,\
                  robotique, interactions, systèmes intégrés matériel-logiciel",
                  8:"Micro- et nanotechnologies, micro- et nanosystèmes, photonique,\
                  électronique, électromagnétisme, énergie électrique",
                  9:"Mécanique des solides. Matériaux et structures. Biomécanique. Acoustique",
                  10:"Milieux fluides et réactifs : transports,\
                  transferts, procédés de transformation",
                  11:"Systèmes et matériaux supra et macromoléculaires\
                  : élaboration, propriétés, fonctions",
                  12:"Architectures moléculaires : synthèses, mécanismes et propriétés",
                  13:"Chimie physique, théorique et analytique",
                  14:"Chimie de coordination, catalyse, interfaces et procédés",
                  15:"Chimie des matériaux, nanomatériaux et procédés",
                  16:"Chimie et vivant",
                  17:"Système solaire et univers lointain",
                  18:"Terre et planètes telluriques : structure, histoire, modèles",
                  19:"Système terre : enveloppes superficielles",
                  20:"Biologie moléculaire et structurale, biochimie",
                  21:"Organisation, expression, évolution des génomes.\
                  Bioinformatique et biologie des systèmes",
                  22:"Biologie cellulaire, développement, évolution-développement",
                  23:"Biologie végétale intégrative",
                  24:"Physiologie, vieillissement, tumorigenèse",
                  25:"Neurobiologie moléculaire et cellulaire,\
                  neurophysiologie",
                  26:"Cerveau, cognition, comportement",
                  27:"Relations hôte-pathogène, immunologie, inflammation",
                  28:"Pharmacologie-ingénierie et technologies\
                  pour la santé-imagerie biomédicale",
                  29:"Biodiversité, évolution et adaptations biologiques\
                  : des macromolécules aux communautés",
                  30:"Surface continentale et interfaces",
                  31:"Hommes et milieux : évolution, interactions",
                  32:"Mondes anciens et médiévaux",
                  33:"Mondes modernes et contemporains",
                  34:"Sciences du langage",
                  35:"Sciences philosophiques et philologiques, sciences de l'art",
                  36:"Sociologie et sciences du droit",
                  37:"Economie et gestion",
                  38:"Anthropologie et étude comparative des sociétés contemporaines",
                  39:"Espaces, territoires et sociétés",
                  40:"Politique, Pouvoir, Organisation",
                  41:"Mathématiques et interactions des mathématiques",
                  "Interdisciplinaires":"Commissions interdisciplinaires"})

FILE_LIST_ARRETES = "arretes-cnrs.txt"

def liste_arretes_tries():
    '''
    Cette fonction crée la liste des arretes en fonction du fichier donné
    et les trie par année
    '''
    # Liste des urls des arrêtés de création de poste de chargé de recherche au CNRS
    urls_arretes_cr = []
    with open(FILE_LIST_ARRETES, "r") as arretes_file:
        urls_arretes_cr = arretes_file.read().splitlines()
    arretes_cr = []
    #Pour chaque arrete on récupère les infos et on stocke
    for url_arret in urls_arretes_cr:
        arret = ArreteCR(url_arret)
        arret.postes_cnrs()
        arretes_cr.append(arret)
    #On trie par année
    arretes_cr = sorted(arretes_cr, key=attrgetter('year'))
    return arretes_cr

def main():
    '''
    La fonction principale de ce module va récupérer la
    liste des arretes déclarants les créations de postes
    puis récuperer la liste des postes pour chaque arretes
    et enfin créer les json stockant la liste des postes par
    section et par année.
    '''

    arretes_cr = liste_arretes_tries()

    json_tab = []
    json_tab_classe1 = []
    json_tab_classe2 = []


    #Création de l'arborescence des json
    for num_sec, name_section in SECTIONS_DICO.items():
        if num_sec == "Interdisciplinaires":
            key = num_sec
        else:
            key = "Section "+str(num_sec)
        json_sec = {"key": key, "name": name_section, "values":[]}
        json_sec_classe1 = {"key": key, "name": name_section, "values":[]}
        json_sec_classe2 = {"key": key, "name": name_section, "values":[]}
        for arret in arretes_cr:
            if arret.classe == "1":
                json_sec["values"].append([arret.year, arret.postes[num_sec]])
                json_sec_classe1["values"].append([arret.year, arret.postes[num_sec]])
            elif arret.classe == "2":
                classe1 = json_sec["values"][-1][-1]
                classe2 = classe1+arret.postes[num_sec]
                json_sec["values"][-1] = [arret.year, classe2]
                json_sec_classe2["values"].append([arret.year, arret.postes[num_sec]])
            elif arret.classe == "classe normale":
                json_sec["values"].append([arret.year, arret.postes[num_sec]])
        json_tab.append(json_sec)
        json_tab_classe1.append(json_sec_classe1)
        json_tab_classe2.append(json_sec_classe2)
    with open("postes-CR-CNRS.json", "w") as out_file:
        json.dump(json_tab, out_file, indent=4)
    with open("postes-CR-CNRS-Classe1.json", "w")as out_file:
        json.dump(json_tab_classe1, out_file, indent=4)
    with open("postes-CR-CNRS-Classe2.json", "w")as out_file:
        json.dump(json_tab_classe2, out_file, indent=4)


if __name__ == "__main__":
    main()
