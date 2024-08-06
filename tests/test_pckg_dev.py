from pubmetric.pckg_dev import *
from pubmetric import data
import asyncio
import pickle

def get_pmids_from_file(shared_datadir): # TODO why is this here?
    filename = os.path.join(shared_datadir, "doi_pmid_library.json")
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}, {"name": "DIAgui", "doi": "10.1093/bioadv/vbae001"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, filename))
    assert str(pmid_list[0]["pmid"]) == '33538780'
    assert str(pmid_list[1]["pmid"]) == '38249340'

def test_generate_random_workflow(shared_datadir):
    """"
    Comparing two igraph graphs "topologically" to assert that the random workflow generated 
    is of the same strucutre as the workflow it was based on, that is, that they are isomorphs. 

    """
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time?
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 
    workflow = {
        "edges": [
            [
                "XTandem_01",
                "ProteinProphet_02"
            ],
            [
                "ProteinProphet_02",
                "StPeter_04"
            ],
            [
                "XTandem_03",
                "StPeter_04"
            ]
        ],
        "steps": {
            "ProteinProphet_02": "14632076",
            "StPeter_04": "29400476",
            "XTandem_01": "14976030",
            "XTandem_03": "14976030"
        },
        "pmid_edges": [
            [
                "14976030",
                "14632076"
            ],
            [
                "14632076",
                "29400476"
            ],
            [
                "14976030",
                "29400476"
            ]
        ]
    }

    random_workflow = generate_random_workflow(graph=graph, workflow=workflow) # TDO: needs to be updated to support the new structure 

    og_graph = igraph.Graph.TupleList(workflow['edges'])
    random_graph = igraph.Graph.TupleList(random_workflow['edges'])

    assert len(random_graph.vs) == 4
    assert og_graph.isomorphic(random_graph) 