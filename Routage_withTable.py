import networkx as nx
import matplotlib.pyplot as plt
import argparse
import random
import time


class Noeud:
    def __init__(self, numero: int):
        self.nombre_voisins = 0
        self.list_voisins = []  
        self.numero = numero
        self.bordure = False
        self.table = {}

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
    

    def show_table(self):
        if self.bordure==True:
            print(f"Table de routage du noeud {self.numero}:")
            for destination, info in self.table.items():
                print(f"Destination: {destination}, Bande passante: {info['bande_passante']}")
            print("-----------------\n")

    



class Djikstra:
    def __init__(self, file_name: str = None):
        self.list_noeud = []
        self.graph = nx.Graph()
        self.file_name = file_name
        self.nombre_noeud_max = None

    def set_noeud(self, aleatoire: None = None, file: None = None):
        if file is not None and aleatoire is not None:
            print("Erreur : Vous ne pouvez pas utiliser les options random et file en même temps.")
            return

        if file is not None:
            with open(self.file_name, 'r') as fichier:
                lignes = fichier.readlines()
                size = int(lignes[0].strip())

                for i in range(size):
                    self.list_noeud.append(Noeud(i))

                for ligne in lignes[1:-1]:
                    text = ligne.split(" ")
                    numero_noeud = int(text[0])  
                    if len(text) > 1:  
                        for i in range(1, len(text)):
                            voisin_info = text[i].replace('(', '').replace(')', '').split(',')
                            voisin_num = int(voisin_info[0]) 
                            poids = int(voisin_info[1])  
                            self.list_noeud[numero_noeud].liaison_directe([(self.list_noeud[voisin_num], poids)])
                
                last_line = lignes[-1].strip()
                for elem in last_line.split(" "):
                    self.list_noeud[int(elem)].bordure = True

        if aleatoire is not None:
            for i in range(self.nombre_noeud_max):
                self.list_noeud.append(Noeud(i))

            for noeud in self.list_noeud:
                nombre_voisins = random.randint(1, self.nombre_noeud_max - 1)
                voisins = random.sample([n for n in self.list_noeud if n != noeud], nombre_voisins)
                for voisin in voisins:
                    poids = random.randint(1, 1000)
                    noeud.liaison_directe([(voisin, poids)])

        for noeud in self.list_noeud:
            self.graph.add_node(noeud.numero)
            for voisin, bande_passante in noeud.list_voisins:
                self.graph.add_edge(noeud.numero, voisin.numero, weight=bande_passante)

        for source_node in self.list_noeud:
            self.remplir_table(source_node)

    
    def remplir_table(self, source: Noeud):
        for destination in self.list_noeud:
            if source.numero != destination.numero and source.bordure==True: 
                self.search_path(source.numero, destination.numero)

    
    
    def search_path(self, source: int, destination: int):
        if source not in range(len(self.list_noeud)) or destination not in range(len(self.list_noeud)):
            print(f"Erreur : le nœud source {source} ou destination {destination} n'existe pas.")
            return None, []

        bandes_passantes = {noeud.numero: float('-inf') for noeud in self.list_noeud}
        predecessors = {noeud.numero: None for noeud in self.list_noeud}
        bandes_passantes[source] = float('inf')

        non_visités = set(noeud.numero for noeud in self.list_noeud)

        while non_visités:
            u = max(non_visités, key=lambda noeud: bandes_passantes[noeud])
            non_visités.remove(u)

            if u == destination:
                break

            for voisin, bande_passante in self.list_noeud[u].list_voisins:
                if voisin.numero in non_visités:
                    nouvelle_bande_passante = min(bandes_passantes[u], bande_passante)
                    if nouvelle_bande_passante > bandes_passantes[voisin.numero]:
                        bandes_passantes[voisin.numero] = nouvelle_bande_passante
                        predecessors[voisin.numero] = u

        chemin = []
        noeud_actuel = destination
        while noeud_actuel is not None:
            chemin.insert(0, noeud_actuel)
            noeud_actuel = predecessors[noeud_actuel]

        if bandes_passantes[destination] == float('-inf'):
            print(f"Aucun chemin trouvé de {source} à {destination}")
            return None, []

        
        self.list_noeud[source].table[destination] = {
            'chemin' : chemin,
            'bande_passante': bandes_passantes[destination]
        }

        return bandes_passantes[destination], chemin

    def get_table_data(self, number: int):
        for destination, data in self.list_noeud[number].table.items():
            print(f"Destination: {destination}")
            print(f"Bande passante: {data['bande_passante']}")
            print(f"Chemin: {data['chemin']}")
            print("-----------------")


    def controle_admission(self):
        routeur_source = None
        routeur_destination = None
        choix = None
        affichage = False
        bande_demande = None
        print("Voulez vous un affichage graphique des résultats n/y?")
        choix = input("n/y")
        if choix=='y':
            affichage=True
        else:
            affichage = False
        while True:
            routeur_source = int(input("Entrez le routeur source de l'emission "))
            if not self.list_noeud[routeur_source].bordure:
                break
            routeur_destination = int(input("Entrez le routeur destination "))
            bande_demande = int(input("Entrez la bande passante demande"))
            bande_path , chemin = self.search_path(routeur_source , routeur_destination)
            print(f"La bande passante maximale du chemin est de {bande_path} avec le chemin {chemin}")
            self.get_table_data(routeur_source)
            if bande_demande > bande_path:
                print(f"Aucun chemin trouve , la bande passante maximale sur ce chemin est de {bande_path}")
            if bande_demande <= bande_path:
                print("Chemin accepte")
                for i in range(len(chemin)-1) :
                    for voisin, poids in self.list_noeud[chemin[i]].list_voisins:
                        if voisin.numero == chemin[i + 1]:
                            if poids >= bande_demande:
                                for idx, (voisin2, poids2) in enumerate(self.list_noeud[chemin[i]].list_voisins):
                                    if voisin2.numero == chemin[i + 1]:
                                        self.list_noeud[chemin[i]].list_voisins[idx] = (voisin2, poids2 - bande_demande)
                                        break

                                self.graph[chemin[i]][chemin[i + 1]]['weight'] -= bande_demande
                                print(f"La bande passante a été réduite à {poids - bande_demande} pour le lien entre {chemin[i]} et {chemin[i+1]}")
                            else:
                                print(f"La bande passante demandée est supérieure à celle du lien. La bande passante du lien est de {poids}.")

                            break  
                    else:
                        print(f"Aucun voisin ne mène de {chemin[i]} à {chemin[i+1]}")

            if chemin and affichage:
                self.visualiser_graphe(chemin)
                time.sleep(2)
            else:
                continue





    def show_state(self):
        for elem in self.list_noeud:
            elem.show_voisins()

    def visualiser_graphe(self, chemin):
        pos = nx.spring_layout(self.graph)
        edges = self.graph.edges(data=True)
        node_colors = ["red" if node in chemin else "gray" for node in self.graph.nodes()]
        chemin_edges = [(chemin[i], chemin[i+1]) for i in range(len(chemin)-1)]
        edge_colors = ["blue" if (u, v) in chemin_edges or (v, u) in chemin_edges else "gray" for u, v in self.graph.edges()]
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color=node_colors, edge_color=edge_colors)
        
        edge_labels = {(u, v): d['weight'] for u, v, d in edges}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        plt.show()
        



def main():
    parser = argparse.ArgumentParser(description="Programme qui lit un fichier ou génère un graphe aléatoire.")
    parser.add_argument('-f', '--file', type=str, help="Chemin vers le fichier à utiliser.")
    parser.add_argument('-r', '--random', type=int, help="Nombre de nœuds pour un graphe aléatoire.")
    parser.add_argument('--source', type=int, help="Nœud source pour l'algorithme (uniquement avec --file).")
    parser.add_argument('--destination', type=int, help="Nœud destination pour l'algorithme (uniquement avec --file).")
    args = parser.parse_args()

    if args.file and args.random:
        print("Erreur : vous ne pouvez pas utiliser les options random et file en même temps.")
        return

    if args.file:
        if args.source is None or args.destination is None:
            print("Erreur : vous devez spécifier un nœud de départ (--source) et un nœud de destination (--destination) lorsque vous utilisez l'option --file.")
            return
        
        d = Djikstra(args.file)
        d.set_noeud(aleatoire=None, file=args.file)
        """d.show_state()
        bande, chemin = d.search_path(args.source, args.destination)
        for elem in range(len(d.list_noeud)):
            d.list_noeud[elem].show_table()

        if chemin:
            d.visualiser_graphe(chemin)
        else:
            print("Aucun chemin valide trouvé. Le graphe ne sera pas affiché.")
        """
        d.controle_admission()

    elif args.random:
        d = Djikstra(file_name=None)
        d.nombre_noeud_max = args.random
        d.set_noeud(aleatoire=args.random, file=None)
        d.show_state()

        source = 0
        destination = random.randint(1, args.random - 1)
        print(f"Source: {source}, Destination: {destination}")

        bande, chemin = d.search_path(source, destination)
        if chemin:
            d.visualiser_graphe(chemin)
        else:
            print("Aucun chemin valide trouvé. Le graphe ne sera pas affiché.")

if __name__ == "__main__":
    main()
