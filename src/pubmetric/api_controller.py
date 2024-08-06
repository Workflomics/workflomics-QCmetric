from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict
import tempfile
import os 
import json
from datetime import datetime

from pubmetric.metrics import *
from pubmetric.workflow import parse_cwl_workflows
from pubmetric.network import create_citation_network

app = FastAPI()

class ScoreResponse(BaseModel):
    workflow_scores: Dict

class GraphRequest(BaseModel):
    topic_id: str
    test_size: str

@app.post("/score_workflows/", response_model=ScoreResponse)
async def score_workflows(file: UploadFile = File(None)):
    path_to_data = "out_202407041439" # where does one store things later?  
    metadata_filename = "../tool_metadata_topic_0121_20240703.json"

    graph = await create_citation_network(inpath=path_to_data) # should I maybe change the name so it does not contain the date, so you have to look in the file instead, or perhaps it is regenerated outside of the package entrirely

    workflow_scores = {}
    # Saving the uploaded files temporarily, should this have some type of check so no bad things can be sent? 
    with tempfile.TemporaryDirectory() as temp_dir: 

        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f: # Slightly dumb to open and save and then just open again within the parse workflows function. Shoudl I update parse wf to work with open files?
            f.write(file.file.read())
        
        print(os.getcwd())

        workflow = parse_cwl_workflows(file_path, metadata_filename)
        
        workflow_level_scores = {}
        pmid_workflow = workflow['pmid_edges'] # for the metrics that do not need to take into account the structure
        workflow_level_scores['workflow_level_average_sum'] = workflow_average_sum(graph, pmid_workflow)
        workflow_level_scores['connectivity_sum'] = connectivity(graph, workflow)
        # etc 

        tool_level_scores = {}
        tool_level_scores['tool_level_average_sum'] = tool_average_sum(graph, workflow)
        # etc 

        # Ages
        with open(metadata_filename, 'r') as f:
            metadata_file = json.load(f)

        current_year = datetime.now().year
        tool_ages = {}
        for step, pmid in workflow['steps'].items(): #TODO: maybe store age directly, instead of publication date - i use age often. pub year never. then we can also use this list comp nightmare below
            tool_name = step.split("_")[0]
            tool_ages[tool_name] = next(tool['age'] for tool in graph.vs if tool['pmid'] == pmid)

        # Format returned scores
        scores = {  'workflow_level_scores': workflow_level_scores,
                    'tool_level_scores': tool_level_scores,
                    'ages': tool_ages                    
                    }
        
        workflow_id = file.filename  # filename as the workflow id
        workflow_scores[workflow_id] = scores # do I want to save any other info? # do I need the id there? 
    
    return ScoreResponse(workflow_scores=workflow_scores)

@app.post("/recreate_graph/")
async def recreate_graph(graph_request: GraphRequest):
    
    graph = await create_citation_network(topic_id=graph_request.topic_id, test_size=20) # rm test_size later # TODO: sometimes asyncio crashes - should have some function to try again
    # TODO: right now the graph is saved within the create graph function. should save it to the same place as the tool_metadata and make sure that is reachable
    return {"message": f"Graph and metadata file recreated successfully."}
