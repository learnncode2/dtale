import mock
import pytest
from six import PY3

from dtale.app import build_app

if PY3:
    from contextlib import ExitStack
else:
    from contextlib2 import ExitStack

URL = "http://localhost:40000"
app = build_app(url=URL)


@pytest.mark.unit
def test_network_data(network_data):
    import dtale.views as views

    df, _ = views.format_data(network_data)
    with build_app(url=URL).test_client() as c:
        with ExitStack() as stack:
            stack.enter_context(mock.patch("dtale.global_state.DATA", {c.port: df}))

            resp = c.get(
                "/dtale/network-data/{}".format(c.port),
                query_string={
                    "to": "to",
                    "from": "from",
                    "group": "weight",
                    "weight": "weight",
                },
            )
            data = resp.json
            assert len(data["edges"]) == 19
            assert len(data["nodes"]) == 14


@pytest.mark.unit
def test_shortest_path(network_data, unittest):
    import dtale.views as views

    df, _ = views.format_data(network_data)
    with build_app(url=URL).test_client() as c:
        with ExitStack() as stack:
            stack.enter_context(mock.patch("dtale.global_state.DATA", {c.port: df}))

            resp = c.get(
                "/dtale/shortest-path/{}".format(c.port),
                query_string={
                    "to": "to",
                    "from": "from",
                    "weight": "weight",
                    "start": "b",
                    "end": "k",
                },
            )
            unittest.assertEqual(resp.json["data"], ["b", "f", "j", "k"])


@pytest.mark.unit
def test_network_analysis(network_data, unittest):
    import dtale.views as views

    df, _ = views.format_data(network_data)
    with build_app(url=URL).test_client() as c:
        with ExitStack() as stack:
            stack.enter_context(mock.patch("dtale.global_state.DATA", {c.port: df}))

            resp = c.get(
                "/dtale/network-analysis/{}".format(c.port),
                query_string={"to": "to", "from": "from", "weight": "weight"},
            )
            unittest.assertEqual(
                resp.json["data"],
                {
                    "avg_weight": 2.68,
                    "edge_ct": 36,
                    "leaf_ct": 3,
                    "max_edge": "10 (source: h, target: j)",
                    "min_edge": "1 (source: j, target: k)",
                    "most_connected_node": "g (Connections: 5)",
                    "node_ct": 14,
                    "triangle_ct": 2,
                },
            )
