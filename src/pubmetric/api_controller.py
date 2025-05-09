import os
import tempfile
from contextlib import asynccontextmanager
from typing import List, Optional

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

import pubmetric.metrics
import pubmetric.network
import pubmetric.workflow


jobstores = {"default": MemoryJobStore()}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Europe/Berlin")

latest_output_path = "data/out_default"


@asynccontextmanager
async def lifespan(application: FastAPI):
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_main():
    return {"msg": "Welcome to Pubmetric!"}


class ScoreResponse(BaseModel):
    benchmarks: List


class GraphRequest(BaseModel):
    topic_id: str
    test_size: str
    tool_list: Optional[list]


@scheduler.scheduled_job("interval", days=30)
async def periodic_graph_generation():
    """Periodically generates a new citation network graph every 30 days and updates
        the global path if the graph is successfully created.
        If the graph file is not found, it logs an error message.

    :return: Dict
        A dictionary containing a message with the new graph path if successful
        or an error message if the graph file is not found.

    """
    global latest_output_path
    try:
        new_output_path = await pubmetric.network.create_network(
            topic_id="default", test_size=50
        )  # TODO: rm test size
        if os.path.exists(new_output_path + "/graph.pkl"):
            latest_output_path = new_output_path
            return {
                "message": f"Graph and metadata file recreated "
                f"successfully New graph path: {latest_output_path}."
            }
        else:
            return {
                "error": "Error: Generated graph file not found."
            }  # TODO error type
    except Exception as e:
        return {
            "error": f"An error occurred while recreating the graph: {e}."
            "The previous graph will continue to be used."
        }


scheduler.add_job(periodic_graph_generation, "interval", days=30)


@app.post("/score_workflow/", response_model=ScoreResponse)
async def score_workflow(cwl_file: UploadFile = File(None)):
    """
    Processes an uploaded CWL file to score workflows based on the current citation
    network graph. Returns scores for the tool- and workflow-level metrics, and ages.
    :param cwl_file: UploadFile
        The uploaded CWL file to be processed.

    :return: ScoreResponse
        A response model containing the computed scores for the workflow;
        metric and age benchmarks accoring to the Workflomics JSON Schema for Benchmarks.
    """

    graph = await pubmetric.network.create_network(
        inpath=latest_output_path, load_graph=True
    )
    with tempfile.TemporaryDirectory() as temp_dir:

        cwl_file_path = os.path.join(temp_dir, cwl_file.filename)
        with open(
            cwl_file_path, "wb"
        ) as f:  # Slightly dumb to open and save and then just
            # open again within the parse workflows function.
            # Shoudl I update parse wf to work with open files?
            f.write(cwl_file.file.read())

        workflow = pubmetric.workflow.parse_cwl(cwl_filename=cwl_file_path, graph=graph)
        pmid_workflow = workflow["pmid_edges"]

        # Metrics
        workflow_level_score = pubmetric.metrics.workflow_average(
            graph=graph, workflow=pmid_workflow
        )
        workflow_desirability = pubmetric.metrics.calculate_desirability(
            score=workflow_level_score, thresholds=[0, 400]
        )
        tool_level_scores = pubmetric.metrics.tool_average_sum(graph, workflow)

        tool_level_output = []
        for tool_name, score in tool_level_scores.items():
            # lower since they are multiplied by the desirability of workflows
            desirability = pubmetric.metrics.calculate_desirability(
                score=score, thresholds=[0, 200]
            )

            if not score or score == 0:
                score = "Unknown"
            tool_level_output.append(
                {
                    "desirability": desirability,
                    "label": f'{tool_name.split("_")[0]}: {score}',
                    "value": str(score),
                }
            )

        ages_output = []
        ages = []
        for tool_name, pmid in workflow['steps'].items():
            age = next((tool['age'] for tool in graph.vs if tool['pmid'] == pmid), None)
            if not age or age > 40: # igraph requires all values of same type, hence >40 is None
                age = "Unknown"
                desirability = 0
            else:
                # capped by putting the upper threshold above maximum
                desirability = pubmetric.metrics.calculate_desirability(
                    score=age, thresholds=[0, 45], inverted=True, transform=False
                )
            ages.append(age)
            ages_output.append(
                {
                    "desirability": desirability,  # Because green == new?
                    "label": f'{tool_name.split("_")[0]}: {age}',
                    "value": str(age),
                }
            )

        metric_benchmark = {
            "unit": "metric",
            "category": "Bibliometrics",
            "description": "The tool- and workflow-level co-citation metric",
            "title": "Co-citation score",
            "steps": tool_level_output,
            "aggregate_value": {
                "desirability": workflow_desirability,
                "value": str(workflow_level_score),
            },
        }
        age_benchmark = {
            "unit": "age",
            "category": "Bibliometrics",
            "description": "Time since release of primary publication",
            "title": "Tool age",
            "steps": ages_output,
            "aggregate_value": {
                "desirability": 1.0,  # unclear what to put here
                "value": f'{len([age for age in ages_output if age["value"] != "Unknown"])}/{len(ages_output)}',
            },
        }

    benchmarks = [metric_benchmark, age_benchmark]

    return ScoreResponse(benchmarks=benchmarks)


@app.post("/recreate_graph/")
async def recreate_graph(
    graph_request: GraphRequest,
):  # if you want to recreate it with a request
    """
    Recreates the citation network graph based on the provided topic ID and test size.
    Updates the global graph path if the graph is successfully generated.

    :param graph_request: GraphRequest
        The request model containing the topic ID and test size for graph recreation.

    :return: Dict
        A dictionary containing a message with the new graph path if successful or an error
        message if the graph file is not found.


    """
    global latest_output_path
    try:
        new_output_path = await pubmetric.network.create_network(
            topic_id=graph_request.topic_id, test_size=50
        )
        if os.path.exists(os.path.join(new_output_path, "graph.pkl")):
            latest_output_path = new_output_path
            return {
                "message": f"Graph and metadata file recreated successfully New graph path: {latest_output_path}."
            }
        else:
            return {"error": "Error: Generated graph file not found."}
    except Exception as e:
        return {
            "error": f"An error occurred while recreating the graph: {e}."
            "The previous graph will continue to be used."
        }
