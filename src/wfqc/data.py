"""
Module to download meta data about software in bio.tools

"""
import os
from tqdm import tqdm       
from datetime import datetime, timedelta
import glob
import json
import numpy as np
import asyncio              
import aiohttp              
import nest_asyncio         # For jupyter asyncio compatibility 
nest_asyncio.apply()        # Automatically takes into account how jupyter handles running event loops

# TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 


async def aggregate_requests(session: aiohttp.ClientSession, url: str) -> dict:
    """
    Sync requests so they are all made in a single session

    :param session: aiohttp.ClientSession object
        Session object for package aiohttp
    :param url: str
        URL for request

    :return: dict
        JSON response from the request
    """
    
    async with session.get(url) as response:
        return await response.json()


async def get_pmid_from_doi(doi_tools: dict, doi_library_filename: str = 'doi_pmid_library.json') -> dict:
    """
    Given a list of dictionaries with data about (tool) publications, 
    this function uses their DOIs to retrieve their PMIDs from NCBI eutils API.

    :param doi_tools: list
        List of dictionaries with data about publications, containing the key "doi".
    :param doi_library_filename: str, default 'doi_pmid_library.json'
        The name of the JSON file with DOI to PMID conversions.

    :return: list
        Updated list of dictionaries with PMIDs included.
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
                print(doi_pmid)             
                # if doi_library:
                #     if doi_library.items()[1]:# this is no dumb need tolook into this more # solve why it gets stuck here! 
                #         continue
                print(doi_pmid)
                if doi_pmid and doi_pmid != 'null': 
                    tool["pmid"] = doi_pmid
                    doi_library[doi] = doi_pmid  # Update the library
                    library_updates = True
            except:
                continue 
        
    if library_updates:
        print(f"Writing new doi, pmid pairs to file {doi_library_filename}")
        with open(doi_library_filename, 'w') as f: #TODO a ok? # appending new dict not good, wan tto extend contents
            json.dump(doi_library, f) # but this will still be wierd. change in furture
    
    updated_doi_tools = [tool for tool in doi_tools if tool.get('pmid')]
    print(updated_doi_tools)
    print(doi_tools)
    print(f"Found {len(updated_doi_tools)} more tools with pmid using their doi's")

    return updated_doi_tools


async def get_pmids(topicID: str, testSize: int = None) -> tuple:
    """ 
    Downloads all (or a specified amount) of the bio.tools tools for a specific topic and returns metadata about the tools.

    :param topicID: str
        The ID to which the tools downloaded belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param testSize: int, default None
        Determines the number of tools downloaded

    :return: tuple
        Tuple containing a list of tools (dictionaries) with PMIDs, a list of tools without PMIDs, and the total number of tools.
    """

    pmid_tools = [] # TODO: predefine the length, means one more request 
    doi_tools = [] # collect tools without pmid

    # requests are made during single session

    page = 1 
    print("Downloading tool metadata from bio.tools")
    async with aiohttp.ClientSession() as session: 
        while page:
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

                    if primary_publication.get('metadata'):
                        age = primary_publication['metadata'].get('date') 
                        if age:
                            age = int(age.split('-')[0])
                    else: 
                        age = None

                    if primary_publication.get('pmid'):
                        pmid_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'), # adding doi here too 
                            'topic': topic[0]['term'],
                            'nrPublications':  nr_publications,
                            'allPublications': all_publications,
                            'pubDate': age,
                            'pmid': str(primary_publication['pmid'])

                        })
                    else:
                        
                        doi_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'),
                            'topic': topic[0]['term'],
                            'nrPublications':  nr_publications,
                            'allPublications': all_publications,
                            'pubDate': age
                        })

                if len(pmid_tools) + len(doi_tools) >= testSize: # TODO: this does not guar. that tot nr tools with pmid is at least testsize. only include pmid_tools in calc?
                    break

                page = biotool_data.get('next')
                if page: # else page will be None and loop will stop 
                    page = page.split('=')[-1] # only want the page number 
            else: 
                print(f'Error while fetching tool names from page {page}')
                break

    # Record the total nr of tools
    total_nr_tools = int(biotool_data['count']) if biotool_data and 'count' in biotool_data else 0

    return pmid_tools, doi_tools, total_nr_tools 

def check_datafile(filename: str, topicID: str, update: bool = False, testSize: int = None) -> tuple: #TODO: filename default None? 
    """
    Checks if the metadata JSON file needs to be updated or not.

    :param filename: str or None
        User-provided filename used to load a specific file. If None, the standard filename will be created using 
        the topic ID and current date and time.
    :param topicID: str
        The ID to which the tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param update: bool, default False
        Determines whether or not to force the creation of a new data file.
    :param testSize: int, default None
        Determines the size of the test file to be generated.

    :return: tuple
        Tuple containing the filename (str) and a boolean indicating whether to load the file or create a new one.
    """

    if not filename: # if no given filename 
        if testSize:
            prefix = f'tool_metadata_test{testSize}_{topicID}'
        else: 
            prefix = f'tool_metadata_{topicID}'

        date_format = "%Y%m%d"

        pattern = f'{prefix}*' #TODO. this means every size of a testfile needs to be regenerated 
        matching_files = glob.glob(pattern)


        if matching_files:
            matching_files.sort(key=os.path.getmtime)
            filename = matching_files[-1]          
            file_date = datetime.strptime(filename.split('_')[-1].split('.')[0], date_format)
            
            if file_date < datetime.now() - timedelta(days=7) or update == True:
                print("Old datafile. Updating...") #TODO: incorrect for update option, say sth better
            else:
                print("Bio.tools data loaded from existing file.")
                return (filename, True) # True, as in load the file 
        else:
            print("No existing bio.tools file. Downloading data.") 

        filename = f'{prefix}_{datetime.now().strftime(date_format)}.json' 
    else:
        print("Proceeding with custom file, please note that the contents may be dated.")
        return (filename, True)
    
    return (filename, False) # False, as in create the file 


async def get_publication_dates(tool_metadata: list) -> list: #TODO: do I really need to send the entire list of dictionaries here or should I just send a list of pmids, what is computationally better? 
    """
    Downloads the publication date from NCBI using the PMID of the file.

    :param tool_metadata: list
        List of dictionaries containing tool metadata.

    :return: list
        Updated list of tool metadata with publication dates included.
    """

    tools_without_pubdate = 0
    async with aiohttp.ClientSession() as session: 
        for tool in tqdm(tool_metadata, desc= 'Downloading publication dates'):

            if tool['pubDate'] and tool['pubDate']!='null': # only fetch info for the ones that did not already have it 
                continue

            tools_without_pubdate += 1
            pmid = tool['pmid']
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"

            data = await aggregate_requests(session, url)
            
            if 'result' in data and pmid in data['result']:
                try:
                    pub_date = data['result'][pmid]['pubdate']

                    tool['pubDate'] = int(str(pub_date).split()[0]) # only include year
                except:
                    tool['pubDate'] = None
            else:
                tool['pubDate'] = None
    print(f"Nr of tools in bio.tools without a publication date: {tools_without_pubdate}")
    return tool_metadata # TODO: do I have to return it or can I just update it using the function, i think i can just update it? 


# TODO: Currently no timing - add tracker
# TODO: outpath not used
def get_tool_metadata(outpath: str, topicID: str = "topic_0121", filename: str = None, update: bool = False, testSize: int = None) -> dict:
    """
    Fetches metadata about tools from bio.tools, belonging to a given topicID and returns as a dictionary, as well as saving the metadata as a JSON file. 
    If a recent enough (less than one week old) JSON file already exists, it loads the metadata from it.

    :param outpath: str
        Path to directory where a newly created file should be placed.
    :param topicID: str
        The ID to which the tools downloaded belong, e.g., the default "Proteomics" (topic_0121) as defined by EDAM ontology 
    :param filename: str or None
        User-provided filename used to load a specific file. If None, the standard filename will be created using 
        topic ID and current date and time.
    :param update: bool, default False
        Determines whether or not to force the retrieval of a new data file.
    :param testSize: int, default None
        Determines the size of the test sample - the number of tools included in the final dictionary.

    :return: dict
        Dictionary containing metadata about the tools.
    """


    np.random.seed(42) #TODO: should it be configurable?

    # File name checking and creation 
    filename, load = check_datafile(filename, topicID, update, testSize)

    if load:
        with open(filename, "r") as f:
            metadata_file = json.load(f)
        if testSize:
            test_tools = np.random.choice(metadata_file['tools'], size = testSize) 
            metadata_file['tools'] = test_tools
            return metadata_file
        else:
            return metadata_file
    
    # Creating json file 

    metadata_file = {"creationDate": str(datetime.now())}

    # Download bio.tools metadata

    pmid_tools, doi_tools, tot_nr_tools = asyncio.run(get_pmids(topicID, testSize))

    metadata_file['totalNrTools'] = tot_nr_tools  
    metadata_file['biotoolsWOpmid'] = len(doi_tools)

    # Update list of doi_tools to include pmid
    doi_tools = asyncio.run(get_pmid_from_doi(doi_tools))

    metadata_file["nrpmidfromdoi"] = len(doi_tools)

    all_tools = pmid_tools + doi_tools

    all_tools_with_age = asyncio.run(get_publication_dates(all_tools))

    metadata_file["tools"] = all_tools_with_age

    with open(filename, 'w') as f:
            json.dump(metadata_file, f)

    # If there were any pages, pmid not empty, check how many tools were retrieved and how many tools had pmids

    print(f'Found {len(all_tools_with_age)} out of a total of {tot_nr_tools} tools with PMIDS.')

    return metadata_file


def get_pmids_from_file(filename: str) -> list:
    """
    Retrieves a list of all PMIDs for the primary publications in the specified meta data JSON file.

    :param filename: str
        The name of the JSON file from which to retrieve the PMIDs.

    :return: list
        List of PMIDs extracted from the JSON file.
    """

    with open(filename, "r") as f:
        metadata_file = json.load(f)
    tools = metadata_file['tools']

    return [tool['pmid'] for tool in tools]


async def europepmc_request(session: aiohttp.ClientSession, article_id: str, page: int = 1, source: str = 'MED') -> list: 
    """ 
    Downloads PMIDs for the articles citing the given article_id, returns a list of citation PMIDs (PubMed IDs).
        
    :param session: aiohttp.ClientSession
        Session object for making asynchronous HTTP requests.
    :param article_id: str  
        PubMed ID for a given article. Can be given as int, but PubMed IDs sometimes contain letters. 
    :param page: int, default 1
        Page number for query.
    :param source: str
        Source ID as given by the EuropePMC API documentation (https://europepmc.org/Help#contentsources).

    :return: list
        List of citation PMIDs.
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
