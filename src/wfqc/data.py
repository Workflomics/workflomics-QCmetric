"""
Functions to download data.
"""

import pandas as pd         
import os
from tqdm import tqdm       
from datetime import datetime, timedelta
import glob
import json

import asyncio              # -"-
import aiohttp              # Used for aggregating requests into single session
import nest_asyncio         # For jupyter asyncio compatibility 
nest_asyncio.apply()        # Automatically takes into account how jupyter handles running event loops
import jsonpath_ng as jp    # TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 

# TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 
import requests             # For single API requests 
import pickle


async def aggregate_requests(session, url):
    """ 
    Sync the bio.tools (page) requests so they are all made in a single session 

    Parameters
    ----------
    session : aiohttp.client.ClientSession object
        session object for package aiohttp
    url : str
        url for request
    """
    
    async with session.get(url) as response:
        return await response.json()


async def get_pmid_from_doi(doi_tools, doi_library_filename = 'doi_pmid_library.json'):
    """
    Given a list of dictionaries with data about (tool) publications, 
    this function uses their doi to retrieve their pmids from NCBI eutils API

    Parameters
    ---
    doi_tools : list
        list of dictionaries with data about publications, containing the key "doi"
    doi_library_filename : str, default 'doi_pmid_library.json' 
        the name of the json file with doi to pmid conversions
    """
    # Download pmids from dois

    try: 
        with open(doi_library_filename, 'r') as f:
            doi_library = json.load(f)
    except FileNotFoundError:
        print(f'Doi library file not found. Creating new file named {doi_library_filename}.')
        doi_library = {} # {doi: pmid}, should I perhaps do {name: [pmid doi ]} instead?
    

    library_updates = False
    async with aiohttp.ClientSession() as session: 
        for tool in tqdm(doi_tools, desc="Downloading pmids from dois."):
            doi = tool.get("doi")

            # Check if tool is already in library 
            if doi in doi_library: 
                tool["pmid"] = doi_library[doi] 
                continue

            url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=PubMed&retmode=json&term={doi}"
            result = await aggregate_requests(session, url)
            
            try:
                doi_pmid = str(result.get('esearchresult').get('idlist')[0])
                if doi_pmid and doi_pmid != 'null' and doi_pmid != "38866554": 
                    tool["pmid"] = doi_pmid
                    doi_library[doi] = doi_pmid  # Update the library
                    library_updates = True
            except:
                continue 
        
    if library_updates:
        print(f"Writing new doi, pmid pairs to file {doi_library_filename}")
        with open(doi_library_filename, 'a') as f: #TODO a ok?
            json.dump(doi_library, f) # but this will still be wierd. change in furture
    
    updated_doi_tools = [tool for tool in doi_tools if tool.get('pmid')]

    print(f"Found {len(updated_doi_tools)} more tools with pmid using their doi's")

    return updated_doi_tools


async def get_pmids(topicID, testSize = None):
    """ 
    Downloads all of the bio.tool tools for a specific topic and returns metadata, including pmids as two lists
    one with dictionaries of metadata fro each tool with pmids, and one for each without a pmid in 
    bio.tools. 

    Parameters
    ---
    topicID : str
        determines what topic/domain tools are downloaded from
    testSize : int, default None
        determines how many pages of tools are downloaded

    """

    pmid_tools = [] # TODO: predefine the length, means one more request 
    doi_tools = [] # collect tools without pmid

    # requests are made during single session

    page = 1 
    print("Downloading tool metadata from bio.tools")
    async with aiohttp.ClientSession() as session: 
        while page:
            if testSize: # not the most optimal for testing, but better than noting? 
                if page >= testSize:
                    break # for debug 
            # send request for tools on the page, await further requests and return resonse in json format
            biotools_url = f'https://bio.tools/api/t?topicID=%22{topicID}%22&format=json&page={page}'
            biotool_data = await aggregate_requests(session, biotools_url)
            

            # TODO: Do I need to check? what happens if no response for page == 1? Maybe try/except instead
            # Checking if there are any tools, if 

            # To record nr of tools with primary

            if 'list' in biotool_data: 
                biotools_lst = biotool_data['list']
                
                for tool in biotools_lst: #add tqdm here 
                    name = tool.get('name') 
                    publications = tool.get('publication') # does this cause a problem if there is no publication? 
                    topic = tool.get('topic')
               
                    if isinstance(publications, list): #TODO: I want them all!
                        nr_publications = len(publications)
                        try:
                            for publication in publications:
                                if publication.get('type')[0] == 'Primary':
                                    primary_publication = publication
                                    break
                        except:
                            primary_publication = publications[0] # pick first then 
                    else:
                        nr_publications = 1
                        primary_publication = publications

                    all_publications = [pub.get('pmid') for pub in publications]

                    if primary_publication.get('pmid'):
                        pmid_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'), # adding doi here too 
                            'topic': topic[0]['term'],
                            'nrPublications':  nr_publications,
                            'allPublications': all_publications,
                            'pmid': str(primary_publication['pmid'])

                        })
                    else:
                        
                        doi_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'),
                            'topic': topic[0]['term'],
                            'nrPublications':  nr_publications,
                            'allPublications': all_publications
                        })

                page = biotool_data.get('next')
                if page: # else page will be None and loop will stop 
                    page = page.split('=')[-1] # only want the page number 
            else: 
                print(f'Error while fetching tool names from page {page}')
                break

    # Record the total nr of tools
    total_nr_tools = int(biotool_data['count']) if biotool_data and 'count' in biotool_data else 0

    return pmid_tools, doi_tools, total_nr_tools

def check_datafile(filename, topicID, update = False):

    """
    Checks if the metadata json file needs to be updatesd or not

    Parameters
    ----------
    filename : str or None
        User provided filename used to load a specific file, if none the standard filename will be created using 
        topic ID and current date and time
    topicID : str
        EDAM topic ID used as tag in the filename to indicate the domain of the file contents 
    update : Boolean, default False
        Determines wether or not to force the creation of a new data file
    """

    if not filename: # if no given filename 
        date_format = "%Y%m%d"
        pattern = f'tool_metadata_{topicID}*'
        matching_files = glob.glob(pattern)

        if matching_files:
            matching_files.sort(key=os.path.getmtime)
            filename = matching_files[-1]          
            file_date = datetime.strptime(filename.split('_')[-1].split('.')[0], date_format)
            
            if file_date < datetime.now() - timedelta(days=7) or update == True:
                print("Old datafile. Updating...")
            else:
                print("Bio.tools data loaded from existing file.")
                return (filename, True) # True, as in load the file 
        else:
            print("No existing bio.tools file. Downloading data.") 
        filename = f'tool_metadata_{topicID}_{datetime.now().strftime(date_format)}.json' 

    else:
        print("Proceeding with custom file, please note that the contents may be dated.")

    return (filename, False) # False, as in create the file 


def get_tool_metadata(outpath, topicID="topic_0121", filename = None, update = False ): 
                                                        # TODO: should add parameter for optional forced retrieval - even if csv file, still recreate it 
                                                        # TODO: Currently no timing - add tracker
    """
    Fetches metadata about tools from bio.tools, belonging to a given topicID and returns as a dataframe.
    If a CSV file already exists load the dataframe from it. 

    Parameters
    ----------
    outpath : str
        Path to directory where a newly created file should be placed
    topicID : str TODO: make this a int instead? why am I writing topic? 
        The ID to which the tools belongs to, ex. "Proteomics" or "DNA" as defined by 
        EDAM ontology (visualisation: https://edamontology.github.io/edam-browser/#topic_0003)
    filename : str or None
        User provided filename used to load a specific file, if none the standard filename will be created using 
        topic ID and current date and time
    update : Boolean, default False
        determines wether or not to force the retrieval  of a new datafile
    """


    # File name checking and creation 
    filename, load = check_datafile(filename, topicID, update)

    if load:
        with open(filename, "r") as f:
            metadata_file = json.load(f)
        return metadata_file
    
    # Creating json file 

    metadata_file = {"creationDate": str(datetime.now())}

    # Download bio.tools metadata
    pmid_tools, doi_tools, tot_nr_tools = asyncio.run(get_pmids(topicID))

    metadata_file['totalNrTools'] = tot_nr_tools  
    metadata_file['biotoolsWOpmid'] = len(doi_tools)

    # Update list of doi_tools to include pmid
    doi_tools = asyncio.run(get_pmid_from_doi(doi_tools))

    metadata_file["nrpmidfromdoi"] = len(doi_tools)

    all_tools = pmid_tools + doi_tools
    metadata_file["tools"] = all_tools

    json_data = json.dumps(metadata_file) # convert to json str
    with open(filename, 'w') as f:
            json.dump(json_data, f)

    # If there were any pages, pmid not empty, check how many tools were retrieved and how many tools had pmids

    print(f'Found {len(all_tools)} out of a total of {tot_nr_tools} tools with PMIDS.')

    return metadata_file

## citations

def get_pmids_from_file(filename): # TODO change to json 
    """ 
    Retrieves a list of all of the pmids for the primary publications in the data file 
    
    Parameters
    ----------
    filename : str
        the name of the json file from which the script retrieves the pmids
    """
    with open(filename, "r") as f:
        metadata_file = json.load(f)
    tools = metadata_file['tools']

    return [tool['pmid'] for tool in tools]


async def europepmc_request(session, article_id, page=1, source='MED'):
    """ 
    Downloads pmids for the articles citing the given article_id, returns list of citation pmids (PubMed IDs)
        
    Parameters
    ----------
    session : asyncio session tag

    article_id : int or str 
        pmid, PubMed ID, for a given article.

    page: int, default == 1
        page number for query

    source: str
        source ID as given by the EuropePMC API documentation: https://europepmc.org/Help#contentsources 
    
    """ 
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/citations?page={page}&pageSize=1000&format=json'
    async with session.get(url) as response:
        if response.ok:
            result = await response.json()
            citations = result['citationList']['citation']
            citation_ids = [citation['id'] for citation in citations]
            if result['hitCount'] <= 1000 * page:
                return citation_ids
            else:
                next_page_citations = await europepmc_request(session, article_id, page + 1, source)
                return citation_ids + next_page_citations
        else:
            print(f'Something went wrong with request {url}')
            return None

async def get_citations(filename):
    pmids = get_pmids_from_file(filename)
    async with aiohttp.ClientSession() as session:
        citation_list = []
        for article_id in tqdm(pmids, desc='Downloading citations from EuropePMC'):
            citation_ids = await europepmc_request(session, article_id)
            citation_list.append(citation_ids)
        return citation_list