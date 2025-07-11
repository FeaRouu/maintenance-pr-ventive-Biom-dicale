import random
import math
from collections import defaultdict
import copy
import matplotlib.pyplot as plt
import pandas as pd


def fonction_cout(assignations, techniciens, tolerance=0.1):
    charge_tech = {tech: sum(duree for duree, _ in taches) for tech, taches in assignations.items()}
    total_heures = sum(charge_tech.values())
    moyenne = total_heures / len(techniciens)
    score = 0

    for charge in charge_tech.values():
        ecart = abs(charge - moyenne)
        if (1 - tolerance) * moyenne <= charge <= (1 + tolerance) * moyenne:
            score += ecart
        else:
            score += ecart ** 2  # pénalité quadratique
    return score

from collections import defaultdict

def initialiser_glouton(taches, techniciens):
    assignations = defaultdict(list)
    charge = {tech: 0.0 for tech in techniciens}

    for duree, dispo in sorted(taches, key=lambda x: -x[0]):  # trie les tâches longues d'abord
        compatibles = [tech for tech in techniciens if dispo in techniciens[tech]]
        if not compatibles:
            print(f"Aucun technicien compétent pour le dispositif : {dispo}")
            continue

        # On choisit celui qui a la charge la plus faible actuellement
        tech_choisi = min(compatibles, key=lambda t: charge[t])
        assignations[tech_choisi].append((duree, dispo))
        charge[tech_choisi] += duree

    return assignations


def generer_voisin(assignations, taches_possibles, techniciens):
    voisin = copy.deepcopy(assignations)

    # Calcul des charges actuelles
    charge_tech = {tech: sum(duree for duree, _ in voisin[tech]) for tech in techniciens}
    moyenne = sum(charge_tech.values()) / len(techniciens)

    # Trier les techniciens par surcharge
    techs_ordonnes = sorted(techniciens, key=lambda t: charge_tech[t] - moyenne, reverse=True)

    for tech_src in techs_ordonnes:
        if not voisin[tech_src]:
            continue

        index = random.randint(0, len(voisin[tech_src]) - 1)
        tache = voisin[tech_src][index]
        duree, dispo = tache

        # Candidats compatibles, moins chargés
        candidats = [t for t in techniciens if dispo in techniciens[t] and t != tech_src]
        candidats = sorted(candidats, key=lambda t: charge_tech[t])  # favorise ceux en dessous de la moyenne

        if not candidats:
            continue

        tech_dest = candidats[0]  # Le moins chargé compatible

        # === Tirage aléatoire : déplacement OU échange ===
        if random.random() < 0.5:
            # Déplacement simple
            voisin[tech_src].pop(index)
            voisin[tech_dest].append(tache)
        else:
            # Échange si possible
            compatibles_dest = [
                (i, t) for i, t in enumerate(voisin[tech_dest])
                if dispo in techniciens[tech_dest] and t[1] in techniciens[tech_src]
            ]
            if compatibles_dest:
                i2, tache2 = random.choice(compatibles_dest)
                voisin[tech_src][index] = tache2
                voisin[tech_dest][i2] = tache
            else:
                # fallback déplacement
                voisin[tech_src].pop(index)
                voisin[tech_dest].append(tache)

        return voisin

    return voisin  # Aucun mouvement possible


def recuit_simule(taches, techniciens, tolerance=0.1, T_init=1000, T_min=1, alpha=0.98, iter_max=300):
    # Solution initiale via glouton
    assignations = initialiser_glouton(taches, techniciens)

    T = T_init
    meilleure_solution = copy.deepcopy(assignations)
    meilleure_cout = fonction_cout(meilleure_solution, techniciens, tolerance)
    while T > T_min:
        for _ in range(iter_max):
            voisin = generer_voisin(assignations, taches, techniciens)
            cout_voisin = fonction_cout(voisin, techniciens, tolerance)
            cout_actuel = fonction_cout(assignations, techniciens, tolerance)
            delta = cout_voisin - cout_actuel
            if delta < 0 or random.random() < math.exp(-delta / T):
                assignations = voisin
                if cout_voisin < meilleure_cout:
                    meilleure_solution = copy.deepcopy(voisin)
                    meilleure_cout = cout_voisin


        T *= alpha  # Refroidissement

    # Vérification des dispositifs non attribués
    dispositifs_taches = set(dispo for _, dispo in taches)
    dispositifs_attribues = set()
    for taches_tech in meilleure_solution.values():
        for _, dispo in taches_tech:
            dispositifs_attribues.add(dispo)
    dispositifs_non_attribues = dispositifs_taches - dispositifs_attribues

    return meilleure_solution, dispositifs_non_attribues

