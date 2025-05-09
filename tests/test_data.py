import json
import os
import pytest
import asyncio
import aiohttp
import pubmetric.data as data
from schemas import metafile_schema_validation
from pubmetric.data import download_domain_annotations, get_tool_metadata
from pubmetric.network import create_network

def test_get_tool_metadata_from_file(shared_datadir):
    """ Testing that loading a metadata file works"""
    metadata_file = asyncio.run(data.get_tool_metadata(outpath='',
                                                       topic_id="topic_0121",
                                                       test_size=20,
                                                       inpath=shared_datadir))
    pepmatch_pmid = next((tool['pmid'] for tool in metadata_file["tools"]
                                    if tool['name'] == 'PEPMatch'), None)
    assert pepmatch_pmid == str(38110863)

def test_get_tool_metadata_schema():
    """Testing that the generated medatata file has the right format"""
    metadata_file = asyncio.run(data.get_tool_metadata(outpath='',
                                                       topic_id="topic_0121",
                                                       test_size=100))
    assert metafile_schema_validation(metadata_file)

@pytest.mark.asyncio
async def test_fetch_citations():
    """ Tests if citations are correctly downloaded for europepmc """
    protein_prophet_pmid = 14632076 #ProteinProphet has 2949 citations on Jul 12th 2024
    async with aiohttp.ClientSession() as session:
        citations = await data.fetch_citations(session=session, article_id=protein_prophet_pmid)
    assert len(citations)> 1000


def test_get_pmid_from_doi_create_file():
    """Tests the creation of a new doi to pmid library"""
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(outpath='',doi_tools= doi_list))
    if os.path.exists('doi_pmid_library.json'): # rm file after completion
        os.remove('doi_pmid_library.json')
    assert str(pmid_list[0]["pmid"]) == '23051804'

def test_get_pmid_from_doi_file_not_found():
    """Tests the handling of a given but non existing doi to pmid library"""
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    filepath="./remove_me.json"
    pmid_list = asyncio.run(data.get_pmid_from_doi(outpath='.',doi_tools= doi_list, inpath='.', doi_library_filename="remove_me.json"))
    if os.path.exists(filepath): # rm file after completion
        os.remove(filepath)
    assert str(pmid_list[0]["pmid"]) == '23051804'

def test_get_pmid_from_doi_from_file(shared_datadir):
    """Tests loading a doi to pmid library"""
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(outpath='',doi_tools= doi_list, inpath= shared_datadir, doi_library_filename='doi_pmid_library.json'))
    assert str(pmid_list[0]["pmid"]) == '23051804' # Proteowizard PMID

def test_get_pmid_from_doi_from_file_with_updates(shared_datadir):
    """Tests updating an existing doi to pmid library"""
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(outpath='',doi_tools= doi_list, inpath= shared_datadir, doi_library_filename= 'doi_pmid_library_empty.json'))
    assert str(pmid_list[0]["pmid"]) == '23051804'

def test_get_pmids():
    test_size = 100
    pmid_tools, doi_tools, total_nr_tools  = asyncio.run(data.get_pmids(topic_id="topic_0121", test_size=test_size))
    print(pmid_tools, doi_tools, total_nr_tools)
    # TODO: just checking some format things right now, could improve
    assert len(pmid_tools) + len(doi_tools) >= test_size
    assert total_nr_tools >= 1800 # As of August 2024 there are 1874 tools in the topic proteomics in bio.tools  
    assert type(pmid_tools[0]['name']) == str
    assert type(pmid_tools[0]['all_publications']) == list


def test_process_citation_data():
    """Tests downloading the citations for one tool"""
    citation_test_tools = {'tools':[{'pmid':'14632076'}]} # Protein prophet, in mock metadata file structure 
    _ = asyncio.run(data.process_citation_data(metadata_file=citation_test_tools))
    assert citation_test_tools['tools'][0]['nr_citations'] >= 2900 # it has 2965 citations currently (August 2024)

def test_get_ages():
     tool_metadata = [
            {"name": "PeptideProphet",
            "doi": None,
            "topic": "Proteomics",
            "nr_publications": 1,
            "all_publications": [
                "12403597"
            ],
            "pmid": "12403597"
        },
     ]
     tool_metadata_inc_ages = asyncio.run(data.process_publication_dates(tool_metadata))
     assert tool_metadata_inc_ages[0]['publication_date'] == 2002


def test_download_domain_annotations():
    """Tests downloading the domain annotations for one tool"""
    tools = download_domain_annotations(annotations="workflomics")
    assert len(tools) > 10
    assert len(tools) < 30


def test_create_network():
    asyncio.run(create_network(tool_selection="workflomics", outpath="out/out_default", inpath="out/out_default"))

def test_create_network_2():
    asyncio.run(create_network(tool_selection=["Comet",
    "PeptideProphet",
    "ProteinProphet",
    "StPeter",
    "mzRecal",
    "idconvert",
    "msconvert",
    "GOEnrichment",
    "gProfiler",
    "XTandem",
    "MS Amanda",
    "MSFragger",
    "protXml2IdList","wcloud"], outpath="out/out_default", inpath="out/out_default"))


def test_get_tool_metadata():
    file :dict = asyncio.run(get_tool_metadata(outpath="out/out_default", topic_id=""))

    # now write to the file system the dict as a json file
    with open("out/out_default/tool_metadata.json", "w") as f:
        f.write(json.dumps(file,indent=4,
    separators=(',', ': ')))

def test_get_pmids_workflomics():
    _, _, no_tools = data.get_pmids_workflomics()
    assert no_tools > 10
    assert no_tools < 30
    