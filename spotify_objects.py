import processing_functions
from spotify_setup import sp
import math

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


class TracksGraph:
    def __init__(self, playlist: Playlist):
        self.nodes = []
        self._normalize_features(playlist.tracklist)

        self.loudness_relevant = False
        self.energy_relevant = False
        self.instrumentalness_relevant = False
        self.tempo_relevant = True
        self.valence_relevant = True
        self.danceability_relevant = True

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
            node.loudness_dimention = (track.loudness - max_loudness) / -max_loudness  # normalize negative value
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
        # Perform BFS to check connectivity
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
        queue: list = []
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

        for i in range(amount):
            queue.append(distances[i][0].track.uri)

        return queue



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
    playlist_id = processing_functions.get_playlist_id_from_url('https://open.spotify.com/playlist/657uAFl5hSMc8f493QEid0?si=64605511a4d243bc')
    pl = Playlist(sp.playlist(playlist_id))
    vals = {
        "loudness": 1,
        "energy": 1,
        "instrumentalness": 1,
        "tempo": 0,
        "valence": 0,
        "danceability": 0
    }
    graph = TracksGraph(pl)
    print(graph.get_one_point_queue(vals, 0.5))

    # Create graph

    # Print the graph


    # print_graph(graph)




    # Check if the graph is connected
   # connected = is_connected(graph)
   # print("Is graph fully connected?", connected)





