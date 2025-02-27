import pytest
from utils.spotify_objects import Playlist, TracksGraph
from business.spotify_setup import sp
from utils.processing_functions import get_playlist_id_from_url, get_all_tracks

playlist_proper_id = '3KfCzf29xRbqCiadoqEcDr'
test_playlist_dict: dict = sp.playlist(playlist_proper_id)
test_playlist_obj: Playlist = Playlist(test_playlist_dict)

sample_values_relevancy: dict = {
        "loudness": True,
        "energy": True,
        "instrumentalness": True,
        "tempo": True,
        "valence": True,
        "danceability": True
    }


def test_connectivity():
    graph = TracksGraph(test_playlist_obj, sample_values_relevancy)

    visited = set()
    to_visit = [graph.nodes[0]] if graph.nodes else []

    while to_visit:
        current = to_visit.pop()
        if current not in visited:
            visited.add(current)
            to_visit.extend(neighbour for neighbour in current.neighbours if neighbour not in visited)

    assert len(visited) == len(graph.nodes)


def test_getting_all_tracks():
    assert len(get_all_tracks(playlist_proper_id)) == len(test_playlist_dict['tracks']['items'])

def test_getting_tracks_empty_playlist():
    empty_playlist_id = '3qHb5M7BaQMdwIoHwXJz2p'
    assert get_all_tracks(empty_playlist_id) == []

def test_making_empty_playlist_object():
    empty_playlist_id = '3qHb5M7BaQMdwIoHwXJz2p'
    with pytest.raises(ValueError, match="Playlist not found or empty"):
        playlist = Playlist(sp.playlist(empty_playlist_id))

def test_getting_playlist_id():
    assert get_playlist_id_from_url('https://open.spotify.com/playlist/3KfCzf29xRbqCiadoqEcDr?si=ade9a9a702c541ce') == playlist_proper_id
    assert get_playlist_id_from_url('alamakotakotmaale') == None

test_getting_tracks_empty_playlist()

def test_normalization():
    values = []
    graph = TracksGraph(test_playlist_obj, sample_values_relevancy)
    for node in graph.nodes:
       values.append(node.loudness_dimention)
       values.append(node.energy_dimention)
       values.append(node.instrumentalness_dimention)
       values.append(node.tempo_dimention)
       values.append(node.valence_dimention)
       values.append(node.danceability_dimention)

    correct = not any(value > 1 or value < 0 for value in values)
    assert correct


def test_dijkstra_pathfinding():
    graph = TracksGraph(test_playlist_obj, sample_values_relevancy)
    start_node = graph.nodes[0]
    end_node = graph.nodes[-1]
    path = graph._dijkstra(start_node, end_node)
    assert path[0] == start_node
    assert path[-1] == end_node

def test_find_path():
    graph = TracksGraph(test_playlist_obj, sample_values_relevancy)

    start_values = {
        "loudness": 1,
        "energy": 0.8,
        "instrumentalness": 0.0,
        "tempo": 1,
        "valence": 0.5,
        "danceability": 0.7
    }

    end_values = {
        "loudness": 0.5,
        "energy": 0.9,
        "instrumentalness": 0.3,
        "tempo": 0,
        "valence": 0.9,
        "danceability": 0.9
    }

    start_song = graph.get_one_point_queue(start_values, 0.01)[0]
    end_song = graph.get_one_point_queue(end_values, 0.01)[0]

    path_uris = graph.find_route_between_points(start_values, end_values)
    assert len(path_uris) > 0
    assert path_uris[0] == start_song
    assert path_uris[-1] == end_song