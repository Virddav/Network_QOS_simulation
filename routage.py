import networkx as nx
import matplotlib.pyplot as plt
import random
import sys
import copy

class Noeud:
    def __init__(self, numero: int):
        self.nombre_voisins = 0
        self.list_voisins = []  
        self.numero = numero     

    def liaison_directe(self, liste_voisins: list):
        for voisin, poids in liste_voisins:
            if voisin not in [v[0] for v in self.list_voisins]:  
                self.list_voisins.append((voisin, poids))  
                voisin.list_voisins.append((self, poids)) 
                self.nombre_voisins += 1
                voisin.nombre_voisins += 1

    def show_voisins(self):
        print(f"Voisins du noeud {self.numero}:")
        for voisin, poids in self.list_voisins:
            print(f"Noeud {voisin.numero}, Poids: {poids}")
        print("-----------------\n")

    def get_numero(self):
        return self.numero

class Djikstra:
    def __init__(self, file_name=None, nombre_noeuds=None, randomize=False):
        self.list_noeud = []
        self.graph = nx.Graph()
        self.file_name = file_name
        self.nombre_noeuds = nombre_noeuds
        self.randomize = randomize  # Option pour le mode aléatoire

    def set_noeud(self):
        if self.file_name:  # Si un fichier est fourni
            with open(self.file_name, 'r') as fichier:
                size = int(fichier.readline().strip())

            for i in range(size):
                self.list_noeud.append(Noeud(i))

            with open(self.file_name, 'r') as fichier:
                for ligne in fichier:
                    ligne = ligne.strip()
                    text = ligne.split(" ")
                    numero_noeud = int(text[0])
                    if len(text) > 1:
                        for i in range(1, len(text)):
                            voisin_info = text[i].replace('(', '').replace(')', '').split(',')
                            voisin_num = int(voisin_info[0])
                            poids = random.randint(500, 10000)

                            self.list_noeud[numero_noeud].liaison_directe([(self.list_noeud[voisin_num], poids)])
        elif self.randomize:  # Si on génère aléatoirement les voisins
            for i in range(self.nombre_noeuds):
                self.list_noeud.append(Noeud(i))

            for noeud in self.list_noeud:
                nombre_voisins = random.randint(1, self.nombre_noeuds - 1)
                voisins = random.sample([n for n in self.list_noeud if n != noeud], nombre_voisins)
                for voisin in voisins:
                    poids = random.randint(1, 1000)
                    noeud.liaison_directe([(voisin, poids)])

        for noeud in self.list_noeud:
            self.graph.add_node(noeud.numero)
            for voisin, bande_passante in noeud.list_voisins:
                self.graph.add_edge(noeud.numero, voisin.numero, weight=bande_passante)

    def show_state(self):
        for elem in self.list_noeud:
            elem.show_voisins()

    def search_path(self, source: int, destination: int, bande_passante_minimale: int):
        bandes_passantes = {noeud.numero: float('-inf') for noeud in self.list_noeud}
        predecessors = {noeud.numero: None for noeud in self.list_noeud}
        bandes_passantes[source] = float('inf')  

        non_visites = set(noeud.numero for noeud in self.list_noeud)

        while non_visites:
            u = max(non_visites, key=lambda noeud: bandes_passantes[noeud])
            non_visites.remove(u)

            if u == destination:
                break

            for voisin, bande_passante in self.list_noeud[u].list_voisins:
                if voisin.numero in non_visites:
                    nouvelle_bande_passante = min(bandes_passantes[u], bande_passante)
                    if nouvelle_bande_passante > bandes_passantes[voisin.numero]:
                        bandes_passantes[voisin.numero] = nouvelle_bande_passante
                        predecessors[voisin.numero] = u
                    print(f"Exploration de l'arête ({u}, {voisin.numero}) : bande passante actuelle = {bande_passante}, bande passante minimale = {nouvelle_bande_passante}")
   

        chemin = []
        noeud_actuel = destination
        while noeud_actuel is not None:
            chemin.insert(0, noeud_actuel)
            noeud_actuel = predecessors[noeud_actuel]

        if bandes_passantes[destination] == float('-inf'):
            print(f"Aucun chemin trouvé de {source} à {destination}")
        else:
            print(f"Le chemin avec la bande passante maximale de {source} à {destination} est: {chemin}")
            print(f"Bande passante minimale sur ce chemin: {bandes_passantes[destination]}")

            if bandes_passantes[destination] >= bande_passante_minimale:
                print(f"Admission acceptée : bande passante suffisante ({bandes_passantes[destination]} >= {bande_passante_minimale})")
                
                # Mise à jour des poids dans la liste des voisins
                for i in range(len(chemin) - 1):
                    u = chemin[i]
                    v = chemin[i + 1]
                    for voisin, poids in self.list_noeud[u].list_voisins:
                        if voisin.numero == v:
                            nouvelle_bande_passante = poids - bande_passante_minimale
                            nouvelle_bande_passante = max(nouvelle_bande_passante, 0)
                            self.update_bande_passante(u, v, nouvelle_bande_passante)
                            print(f"Nouvelle bande passante pour l'edge ({u}, {v}): {nouvelle_bande_passante}")
                            break

                return chemin
            else:
                print(f"Admission refusée : bande passante insuffisante ({bandes_passantes[destination]} < {bande_passante_minimale})")
                self.visualiser_graphe_static()
                return None

    def update_bande_passante(self, u, v, nouvelle_bande_passante):
        """Mise à jour des bandes passantes après une demande"""
        for index, (voisin, poids) in enumerate(self.list_noeud[u].list_voisins):
            if voisin.numero == v:
                self.list_noeud[u].list_voisins[index] = (voisin, nouvelle_bande_passante)
            break
            
        for index, (voisin, poids) in enumerate(self.list_noeud[v].list_voisins):
            if voisin.numero == u:
                self.list_noeud[v].list_voisins[index] = (self.list_noeud[u], nouvelle_bande_passante)
            break

        self.update_graph_networkx(u, v, nouvelle_bande_passante)

    def update_graph_networkx(self, u, v, nouvelle_bande_passante):
        if self.graph.has_edge(u, v):

            self.graph[u][v]['weight'] = nouvelle_bande_passante


    def visualiser_graphe(self, chemin):
        plt.figure()
        pos = nx.spring_layout(self.graph)  
        edges = self.graph.edges(data=True)
        node_colors = ["red" if node in chemin else "gray" for node in self.graph.nodes()]
        chemin_edges = [(chemin[i], chemin[i+1]) for i in range(len(chemin)-1)]
        edge_colors = ["blue" if (u, v) in chemin_edges or (v, u) in chemin_edges else "gray" for u, v in self.graph.edges()]
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color=node_colors, edge_color=edge_colors)
        
        edge_labels = {(u, v): d['weight'] for u, v, d in edges}  
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        plt.show(block=False)

    def visualiser_graphe_static(self):
        plt.figure()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color="gray")

        edge_labels = {(u, v): d['weight'] for u, v, d in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        plt.show(block=False)


    def save_to_file(self, file_name):
        with open(file_name, 'w') as fichier:
            fichier.write(f"{len(self.list_noeud)}\n")  
            for noeud in self.list_noeud:
                fichier.write(f"{noeud.numero} ")
                for voisin, poids in noeud.list_voisins:
                    fichier.write(f"({voisin.numero},{poids}) ")
                fichier.write("\n")

    

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == 'static':
        file = sys.argv[2]
        d = Djikstra(file_name=file)
    elif mode == 'random':
        nombre_noeuds = int(sys.argv[2])
        d = Djikstra(nombre_noeuds=nombre_noeuds, randomize=True)

    d.set_noeud()
    d.show_state()
    d.visualiser_graphe_static()

    while True:
        user_input = input("Voulez-vous rechercher un chemin? (O/N ou 'exit' pour quitter): ").strip().lower()
        if user_input == 'exit':
            print("Fin du programme.")
            break

        source = int(input("Entrez le noeud source: "))
        destination = int(input("Entrez le noeud destination: "))
        bande_passante_minimale = int(input("Entrez la bande passante minimale requise: "))
        chemin = d.search_path(source, destination, bande_passante_minimale)
        if chemin:
            visualisation = input("Voulez-vous visualiser le chemin sur le graphe? (O/N): ").strip().lower()
            if visualisation == 'o':
                d.visualiser_graphe(chemin)
