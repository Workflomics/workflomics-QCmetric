import json
import requests

def get_tool_by_id(biotools_id):
    base_url = f"https://bio.tools/api/tool/{biotools_id}"
    params = {
        "format": "json"
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Check for request errors
    return response.json()

def get_specific_tools_by_id(biotools_ids):
    tools = []
    for biotools_id in biotools_ids:
        try:
            tool = get_tool_by_id(biotools_id)
            tools.append(tool)
            print(f"Found tool: {tool['name']} with biotoolsID: {biotools_id}")
        except requests.HTTPError:
            print(f"Tool with biotoolsID '{biotools_id}' not found.")
    return tools

# List of biotoolsIDs for the specific tools you want to get
biotools_ids = [
    "comet", "peptideprophet", "proteinprophet", "stpeter",
    "mzrecal", "idconvert", "msconvert", "GOEnrichment",
    "gprofiler", "xtandem", "MS_Amanda", "msfragger", 
    "protXml2IdList"
]

# Fetch details for the specified tools using biotoolsID
specific_tools = get_specific_tools_by_id(biotools_ids)