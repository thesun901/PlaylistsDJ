import processing_functions
from spotify_setup import sp
import math
from collections import deque
import heapq

class Track:
    def __init__(self, song: dict, features: dict):
        self.id: str = song['id']
        self.uri = song['uri']
        self.name = song['name']
        self.loudness = features['loudness']
        self.energy = features['energy']
        self.instrumentalness = features['instrumentalness']
        self.tempo = features['tempo']
        self.valence = features['valence']
        self.danceability = features['danceability']


class Playlist:
    def __init__(self, playlist_dict: dict):
        self.id: str = playlist_dict['id']
        self.name: str = playlist_dict['name']
        self.image: str = playlist_dict['images'][0]['url']
        self.tracklist = []
        playlist_tracks = processing_functions.get_all_tracks(self.id)
        songs_features = processing_functions.get_audio_features(playlist_tracks)

        for item, features in zip(playlist_tracks, songs_features):
            self.tracklist.append(Track(item['track'], features))


class TrackNode:
    def __init__(self, track: Track):
        self.track = track
        self.loudness_dimention = 0
        self.energy_dimention = 0
        self.instrumentalness_dimention = 0
        self.tempo_dimention = 0
        self.valence_dimention = 0
        self.danceability_dimention = 0

        self.neighbours: set[TrackNode] = set()

    def __lt__(self, other):
        return True


class TracksGraph:
    def __init__(self, playlist: Playlist, values_relevancy: dict):
        self.nodes = []
        self._normalize_features(playlist.tracklist)

        self.loudness_relevant = values_relevancy['loudness']
        self.energy_relevant = values_relevancy['energy']
        self.instrumentalness_relevant = values_relevancy['instrumentalness']
        self.tempo_relevant = values_relevancy['tempo']
        self.valence_relevant = values_relevancy['valence']
        self.danceability_relevant = values_relevancy['danceability']

        self.build_graph()

    def _normalize_features(self, tracks):
        # loudnes feature has only negative values
        max_loudness = float('-inf')
        max_energy = 0
        max_instrumentalness = 0
        max_tempo = 0
        max_valence = 0
        max_danceability = 0

        for track in tracks:
            if track.loudness > max_loudness:
                max_loudness = track.loudness
            if track.energy > max_energy:
                max_energy = track.energy
            if track.instrumentalness > max_instrumentalness:
                max_instrumentalness = track.instrumentalness
            if track.tempo > max_tempo:
                max_tempo = track.tempo
            if track.valence > max_valence:
                max_valence = track.valence
            if track.danceability > max_danceability:
                max_danceability = track.danceability

        for track in tracks:
            node = TrackNode(track)
            node.loudness_dimention = max_loudness / track.loudness
            node.energy_dimention = track.energy / max_energy if max_energy else 0
            node.instrumentalness_dimention = track.instrumentalness / max_instrumentalness if max_instrumentalness else 0
            node.tempo_dimention = track.tempo / max_tempo if max_tempo else 0
            node.valence_dimention = track.valence / max_valence if max_valence else 0
            node.danceability_dimention = track.danceability / max_danceability if max_danceability else 0
            self.nodes.append(node)

    def _distance(self, node1: TrackNode, node2: TrackNode) -> float:
        # Calculate distance considering only relevant dimensions
        distance = 0
        if self.loudness_relevant:
            distance += (node1.loudness_dimention - node2.loudness_dimention) ** 2
        if self.energy_relevant:
            distance += (node1.energy_dimention - node2.energy_dimention) ** 2
        if self.instrumentalness_relevant:
            distance += (node1.instrumentalness_dimention - node2.instrumentalness_dimention) ** 2
        if self.tempo_relevant:
            distance += (node1.tempo_dimention - node2.tempo_dimention) ** 2
        if self.valence_relevant:
            distance += (node1.valence_dimention - node2.valence_dimention) ** 2
        if self.danceability_relevant:
            distance += (node1.danceability_dimention - node2.danceability_dimention) ** 2
        return math.sqrt(distance)

    def _distance_point(self, node: TrackNode, loudness: float, energy: float,
                        instrumentalness: float, tempo: float, valence: float, danceability: float) -> float:
        # Calculate distance considering only relevant dimensions
        distance = 0
        if self.loudness_relevant:
            distance += (node.loudness_dimention - loudness) ** 2
        if self.energy_relevant:
            distance += (node.energy_dimention - energy) ** 2
        if self.instrumentalness_relevant:
            distance += (node.instrumentalness_dimention - instrumentalness) ** 2
        if self.tempo_relevant:
            distance += (node.tempo_dimention - tempo) ** 2
        if self.valence_relevant:
            distance += (node.valence_dimention - valence) ** 2
        if self.danceability_relevant:
            distance += (node.danceability_dimention - danceability) ** 2
        return math.sqrt(distance)

    def build_graph(self):
        for node in self.nodes:
            distances = []
            for other_node in self.nodes:
                if other_node is not node:
                    distance = self._distance(node, other_node)
                    distances.append((distance, other_node))
            distances.sort(key=lambda x: x[0])
            for _, closest_node in distances[:2]:
                if closest_node not in node.neighbours:
                    node.neighbours.add(closest_node)
                    if node not in closest_node.neighbours:
                        closest_node.neighbours.add(node)

        self._ensure_connectivity()

    def _ensure_connectivity(self):
        # Perform DFS to check connectivity
        visited = set()
        to_visit = [self.nodes[0]] if self.nodes else []

        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                to_visit.extend(neighbour for neighbour in current.neighbours if neighbour not in visited)

        # Add extra neighbours if the graph is not fully connected
        # and connect the unvisited node to the closest visited node
        if len(visited) != len(self.nodes):
            unvisited = [node for node in self.nodes if node not in visited]
            for unvisited_node in unvisited:
                distances = []
                for visited_node in visited:
                    distance = self._distance(unvisited_node, visited_node)
                    distances.append((distance, visited_node))
                distances.sort(key=lambda x: x[0])

                if distances:
                    _, closest_visited_node = distances[0]
                    unvisited_node.neighbours.add(closest_visited_node)
                    closest_visited_node.neighbours.add(unvisited_node)
                    visited.add(unvisited_node)

    def get_one_point_queue(self, values: dict, percentage: float):
        amount: int = int(len(self.nodes) * percentage)
        loudness: float = values['loudness']
        energy: float = values['energy']
        instrumentalness: float = values['instrumentalness']
        tempo: float = values['tempo']
        valence: float = values['valence']
        danceability: float = values['danceability']

        distances: list[tuple] = []
        for node in self.nodes:
            distances.append((node, self._distance_point(node, loudness, energy,
                             instrumentalness, tempo, valence, danceability)))

        distances.sort(key=lambda x: x[1])

        queue: list = []
        for i in range(amount):
            queue.append(distances[i][0].track.uri)

        return queue

    def find_route_between_points(self, start_vals: dict, end_vals: dict) -> list[str]:
        """
        Finds the route between the closest node to start_vals and the closest node to end_vals.

        :param start_vals: Dictionary of attribute values for the starting point.
        :param end_vals: Dictionary of attribute values for the ending point.
        :return: List of track URIs representing the route.
        """
        start_loudness = start_vals['loudness']
        start_energy = start_vals['energy']
        start_instrumentalness = start_vals['instrumentalness']
        start_tempo = start_vals['tempo']
        start_valence = start_vals['valence']
        start_danceability = start_vals['danceability']

        end_loudness = end_vals['loudness']
        end_energy = end_vals['energy']
        end_instrumentalness = end_vals['instrumentalness']
        end_tempo = end_vals['tempo']
        end_valence = end_vals['valence']
        end_danceability = end_vals['danceability']

        # Find closest start node
        start_node = min(self.nodes, key=lambda node: self._distance_point(node, start_loudness, start_energy,
                                                                           start_instrumentalness, start_tempo,
                                                                           start_valence, start_danceability))

        # Find closest end node
        end_node = min(self.nodes,key=lambda node: self._distance_point(node, end_loudness, end_energy, end_instrumentalness,
                                                             end_tempo, end_valence, end_danceability))

        # Find the route using Dijkstra's algorithm
        route_nodes = self._dijkstra(start_node, end_node)

        queue: list = []
        for node in route_nodes:
            queue.append(node.track.uri)
            print(node.track.name)

        return queue

    def _dijkstra(self, start_node: TrackNode, end_node: TrackNode) -> list[TrackNode]:
        """
        Finds the shortest path between start_node and end_node using Dijkstra's algorithm.

        :param start_node: Starting track node.
        :param end_node: Ending track node.
        :return: List of TrackNodes representing the path from start to end.
        """
        # Priority queue to store (distance, node, path)
        priority_queue = [(0, start_node, [start_node])]
        # Dictionary to store the shortest distance to each node
        distances = {start_node: 0}
        # Set to store visited nodes
        visited = set()

        while priority_queue:
            current_distance, current_node, path = heapq.heappop(priority_queue)
            if current_node in visited:
                continue

            visited.add(current_node)

            if current_node == end_node:
                return path

            for neighbour in current_node.neighbours:
                distance = self._distance(current_node, neighbour)
                new_distance = current_distance + distance

                if neighbour not in distances or new_distance < distances[neighbour]:
                    distances[neighbour] = new_distance
                    heapq.heappush(priority_queue, (new_distance, neighbour, path + [neighbour]))

        return []


    # Check the graph structure
def print_graph(graph):
    print("Track Graph")
    print("===========")
    for node in graph.nodes:
        print(f"Track ID: {node.track.name}")
        print(f"neighbours: {[neighbour.track.name for neighbour in node.neighbours]}")
        print("")


# Function to check connectivity
def is_connected(graph):
    visited = set()
    to_visit = [graph.nodes[0]] if graph.nodes else []

    while to_visit:
        current = to_visit.pop()
        if current not in visited:
            visited.add(current)
            to_visit.extend(neighbour for neighbour in current.neighbours if neighbour not in visited)

    return len(visited) == len(graph.nodes)

if __name__ == '__main__':

    relevancy: dict = {
        "loudness": True,
        "energy": True,
        "instrumentalness": False,
        "tempo": True,
        "valence": False,
        "danceability": False
    }
    vals1: dict = {
        "loudness": 0,
        "energy":0,
        "instrumentalness": 1,
        "tempo": 0,
        "valence": 0,
        "danceability": 0
    }
    vals2: dict = {
        "loudness": 1,
        "energy": 1,
        "instrumentalness": 1,
        "tempo": 1,
        "valence": 1,
        "danceability": 1
    }

    playlist_id = processing_functions.get_playlist_id_from_url('https://open.spotify.com/playlist/2qFlUcj6WcXDzvzO0XlTo6?si=d491a85bd3114701')
    pl = Playlist(sp.playlist(playlist_id))
    graph = TracksGraph(pl, relevancy)
    route = graph.find_route_between_points(vals1, vals2)
    print("Route between points:", route)






