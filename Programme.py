import matplotlib.pyplot as plt
import networkx as nx
from collections import deque
import csv
import random


def dessiner_arbre(arbre):

    graph = nx.DiGraph()  # Crée un graphe orienté
    pos = {}  # Dictionnaire pour stocker les positions des nœuds

    # Fonction récursive pour ajouter les nœuds et leurs enfants au graphe
    def ajouter_noeud_et_enfants(noeud, parent=None, x=0, y=0, dx=1, dy=1):
        nonlocal graph, pos
        graph.add_node(noeud)
        pos[noeud] = (x, y)


        if parent is not None:
            graph.add_edge(parent, noeud)


        if len(noeud.enfants) > 0:
            dx /= len(noeud.enfants)
            for i, enfant in enumerate(noeud.enfants):

                ajouter_noeud_et_enfants(enfant, parent=noeud, x=x + (i + 1) * dx, y=y - dy, dx=dx, dy=dy)

    # Appel initial pour démarrer la récursion à partir de la racine de l'arbre
    if arbre.racine is not None:
        ajouter_noeud_et_enfants(arbre.racine)

    # Ajoute les attributs 'minaurant' et 'majaurant' comme étiquettes sur chaque nœud
    for noeud in graph.nodes:
        graph.nodes[noeud]['label'] = f"Min: {noeud.minaurant[0]}, Maj: {noeud.majaurant[0]}"

    return graph, pos



class Arbre:
    def __init__(self,poids,utilite,poids_sac1, poids_sac2):
        self.racine = None
        self.meilleure_solution = None
        self.poids = poids
        self.utilite = utilite
        self.poids_sac1=poids_sac1
        self.poids_sac2=poids_sac2


    def afficher_arbre(self, noeud, profondeur=0):
        sacs_str = f"Sac 1: {noeud.elements_sac1}, Sac 2: {noeud.elements_sac2}, Sac résultant (Majaurant): {noeud.elements_sac_maj}"
        print("  " * profondeur + f"|---- Min: {noeud.minaurant[0]}, Maj: {noeud.majaurant[0]}, {sacs_str}")

        for enfant in noeud.enfants:
            self.afficher_arbre(enfant, profondeur + 1)

    def creer_noeud_fils(self, parent, poids, utilite, poids_sac1, poids_sac2, parent_objet_pour_fils):
        objet_a_ajouter_sac1 = parent_objet_pour_fils
        objet_a_ajouter_sac2 = parent_objet_pour_fils

        fils1 = None
        fils2 = None
        fils3 = None

        if objet_a_ajouter_sac1:
            sum_weights = 0
            for index in objet_a_ajouter_sac1:
                adjusted_index = index - 1
                if 0 <= adjusted_index < len(poids):
                    sum_weights += poids[adjusted_index]
                else:
                    print("Indice invalide:", index)
            if sum_weights <= poids_sac1:
                fils1 = Noeud(poids, utilite, poids_sac1, poids_sac2, objet_a_ajouter_sac1, [], parent_objet_pour_fils)

        if objet_a_ajouter_sac2:
            sum_weights_sac2 = 0
            for index in objet_a_ajouter_sac2:
                adjusted_index = index - 1
                if 0 <= adjusted_index < len(poids):
                    sum_weights_sac2 += poids[adjusted_index]
                else:
                    print("Indice invalide:", index)
            if sum_weights_sac2 <= poids_sac2:
                fils2 = Noeud(poids, utilite, poids_sac1, poids_sac2, [], objet_a_ajouter_sac2, parent_objet_pour_fils)

        poids_modifie = poids.copy()
        if objet_a_ajouter_sac1 or objet_a_ajouter_sac2:
            for objet in parent.objet_pour_fils:
                poids_modifie[objet - 1] = 0
            fils3 = Noeud(poids_modifie, utilite, poids_sac1, poids_sac2, [], [], parent_objet_pour_fils)

        return fils1, fils2, fils3

    def etendre_arbre(self, noeud):
        if not noeud.est_ouvert:
            return

        fils_sac1, fils_sac2, fils3 = self.creer_noeud_fils(noeud, self.poids, noeud.utilite, self.poids_sac1,self.poids_sac2, noeud.objet_pour_fils)
        if fils_sac1:
            if fils_sac1.majaurant[0] <= self.meilleure_solution or fils_sac1.majaurant[0] == fils_sac1.minaurant[0]:
                fils_sac1.est_ouvert = False
            noeud.enfants.append(fils_sac1)
            if fils_sac1.minaurant[0] > self.meilleure_solution:
                self.meilleure_solution = fils_sac1.minaurant[0]

        if fils_sac2:
            if fils_sac2.majaurant[0] <= self.meilleure_solution or fils_sac2.majaurant[0] == fils_sac2.minaurant[0]:
                fils_sac2.est_ouvert = False
            noeud.enfants.append(fils_sac2)
            if fils_sac2.minaurant[0] > self.meilleure_solution:
                self.meilleure_solution = fils_sac2.minaurant[0]

        if fils3:
            if fils3.majaurant[0] <= self.meilleure_solution or fils3.majaurant[0] ==fils3.minaurant[0]:
                fils3.est_ouvert = False
            noeud.enfants.append(fils3)
            if fils3.minaurant[0] > self.meilleure_solution:
                self.meilleure_solution = fils3.minaurant[0]

class Noeud:
    def __init__(self, poids, utilite, poids_sac1, poids_sac2, elements_a_ajouter_sac1, elements_a_ajouter_sac2, parent_objet_pour_fils=None):
        self.poids = poids
        self.utilite = utilite
        self.poids_sac1 = poids_sac1
        self.poids_sac2 = poids_sac2
        self.elements_sac1 = []
        self.elements_sac2 = []
        self.elements_sac_maj = []
        self.objet_pour_fils = parent_objet_pour_fils.copy() if parent_objet_pour_fils else []
        self.est_ouvert = True
        self.enfants = []
        self.explore = False

        self.minaurant = self.calculer_min(poids, utilite, poids_sac1, poids_sac2, elements_a_ajouter_sac1, elements_a_ajouter_sac2)
        if elements_a_ajouter_sac1:
            elements_a_ajouter = elements_a_ajouter_sac1
        else:
            elements_a_ajouter = elements_a_ajouter_sac2
        self.majaurant = self.calculer_maj(poids, utilite, poids_sac1, poids_sac2, elements_a_ajouter)

        self.elements_sac1 = self.minaurant[1]
        self.elements_sac2 = self.minaurant[2]
        self.elements_sac_maj = self.majaurant[1]

        if self.elements_sac_maj:
            self.objet_pour_fils.append(self.elements_sac_maj[-1])

    def afficher_sacs(self):
        print("Sacs:")
        print("Sac 1:", self.elements_sac1)
        print("Sac 2:", self.elements_sac2)
        print("Sac résultant (Majaurant):", self.elements_sac_maj)

    def calculer_min(self,poids, valeurs, poids_sac1, poids_sac2, elements_sac1, elements_sac2):
        pi = poids[:]
        wi = valeurs[:]

        poids_sac1 = poids_sac1
        poids_sac2 = poids_sac2

        sac1 = []
        sac2 = []
        rejetes = []

        p_sac1, p_sac2 = 0, 0
        utilite_sacs = 0

        if elements_sac1:
            for element in elements_sac1:
                poids_element = pi[element - 1]
                valeur_element = wi[element - 1]
                if poids_sac1 - p_sac1 >= poids_element:
                    sac1.append(element)
                    p_sac1 += poids_element
                    utilite_sacs += valeur_element
                    pi[element - 1] = 0
                    wi[element - 1] = 0

        if elements_sac2:
            for element in elements_sac2:
                poids_element = poids[element - 1]
                valeur_element = valeurs[element - 1]
                if poids_sac2 - p_sac2 >= poids_element:
                    sac2.append(element)
                    p_sac2 += poids_element
                    utilite_sacs += valeur_element
                    pi[element - 1] = 0
                    wi[element - 1] = 0

        if not elements_sac1 and not elements_sac2:
            pi = poids
            wi = valeurs

        for i in range(len(pi)):
            if pi[i] == 0:
                continue

            if poids_sac1 - p_sac1 >= pi[i]:
                sac1.append(i + 1)
                p_sac1 += pi[i]
                utilite_sacs += wi[i]
            elif poids_sac2 - p_sac2 >= pi[i]:
                sac2.append(i + 1)
                p_sac2 += pi[i]
                utilite_sacs += wi[i]
            else:
                rejetes.append(i + 1)

        return utilite_sacs, sac1, sac2

    def calculer_maj(self,poids, valeurs, poids_sac1, poids_sac2, elements_a_ajouter):
        pi = poids[:]
        wi = valeurs[:]
        poids_total = poids_sac1 + poids_sac2
        p_sac = 0
        utilite = 0

        sacmaj = []

        if elements_a_ajouter:
            for element in elements_a_ajouter:
                poids_element = poids[element - 1]
                valeur_element = valeurs[element - 1]
                if poids_total - p_sac >= poids_element:
                    sacmaj.append(element)
                    p_sac += poids_element
                    utilite += valeur_element
                    pi[element - 1] = 0


        for i in range(len(pi)):
            if pi[i] == 0:
                continue

            if poids_total - p_sac >= pi[i]:
                sacmaj.append(i + 1)
                p_sac += pi[i]
                utilite += wi[i]
            elif poids_total - p_sac != 0:
                sacmaj.append(i + 1)
                utilite += ((poids_total - p_sac)* wi[i]) / pi[i]
                break
            else:
                break

        return utilite, sacmaj

def ecrire_csv(arbre, nom_fichier):
    with open(nom_fichier, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["  Min",   "   Maj",   "   Sacs Sac1", "    Sacs Sac2", "    Sacs Résultants (Majaurant)"])

        # Fonction auxiliaire pour parcourir récursivement l'arbre et écrire chaque nœud
        def ecrire_noeud_csv(noeud):
            writer.writerow([noeud.minaurant[0],
                             noeud.majaurant[0],
                             ',       '.join(map(str, noeud.elements_sac1)),
                             ',       '.join(map(str, noeud.elements_sac2)),
                             ',       '.join(map(str, noeud.elements_sac_maj))])

            for enfant in noeud.enfants:
                ecrire_noeud_csv(enfant)

        # Commencez par la racine de l'arbre
        ecrire_noeud_csv(arbre.racine)


def trier_par_ratio_decroissant(poids, utilite):
    ratios = [(utilite[i] / poids[i], poids[i], utilite[i]) for i in range(len(poids))]

    # Trier la liste de tuples par rapport décroissant
    ratios_tries = sorted(ratios, reverse=True)

    # Extraire les poids triés et les utilités triées
    poids_tries = [ratio[1] for ratio in ratios_tries]
    utilite_triee = [ratio[2] for ratio in ratios_tries]

    return poids_tries, utilite_triee

def generer_tableaux_aleatoires(taille):
    poids = [random.randint(1, 20) for _ in range(taille)]  # Valeurs aléatoires entre 1 et 20
    utilite = [random.randint(1, 50) for _ in range(taille)]  # Valeurs aléatoires entre 1 et 50

    poids_sac1 = random.randint(5, 15)  # Valeur aléatoire entre 5 et 15 pour le sac 1
    poids_sac2 = random.randint(5, 15)  # Valeur aléatoire entre 5 et 15 pour le sac 2

    return poids, utilite, poids_sac1, poids_sac2



if __name__ == "__main__":
    poids_racine = [4,6,3,5 ]
    utilite_racine = [45,36,16,30]
    poids_sac1_racine = 10
    poids_sac2_racine = 7



    #trie les donner des 2 tableaux
    poids_tries, utilite_triee = trier_par_ratio_decroissant(poids_racine, utilite_racine)
    print("Poids aléatoires trie :", poids_tries)
    print("Utilité aléatoire trie :", utilite_triee)
    print("Poids du sac 1:", poids_sac1_racine)
    print("Poids du sac 2:", poids_sac2_racine)

    arbre = Arbre(poids_tries,utilite_triee,poids_sac1_racine, poids_sac2_racine)
    racine = Noeud(poids_racine, utilite_racine, poids_sac1_racine, poids_sac2_racine, [], [])
    racine.parent = None
    arbre.racine = racine

    arbre.meilleure_solution = racine.minaurant[0]

    file_attente = deque([racine])
    # itteration sur les element de l'arbre
    while file_attente:
        noeud = file_attente.popleft()

        if noeud.est_ouvert and not noeud.explore:
            noeud.explore = True
            arbre.etendre_arbre(noeud)
            for enfant in noeud.enfants:
                if enfant.est_ouvert and not enfant.explore:
                    file_attente.append(enfant)
    print("Meilleure solution trouvée :", arbre.meilleure_solution)
    ecrire_csv(arbre, "arbre_information2.csv")

    print("Affichage de l'arbre :")
    arbre.afficher_arbre(arbre.racine)
    graph, pos = dessiner_arbre(arbre)
    nx.draw(graph, pos, labels=nx.get_node_attributes(graph, 'label'), with_labels=True)
    plt.show()  #