import pytest
import asyncio
import aiohttp
from pubmetric.data import * 
from data.schemas import metafile_schema_validation

def test_get_tool_metadata_from_file(shared_datadir):
    metadata_file = asyncio.run(get_tool_metadata(outpath='',topic_id="topic_0121", test_size=20, inpath=shared_datadir))
    pepmatch_pmid = next((tool['pmid'] for tool in metadata_file["tools"] if tool['name'] == 'PEPMatch'), None)
    assert pepmatch_pmid == str(38110863)

def test_get_tool_metadata_schema():
    metadata_file = asyncio.run(get_tool_metadata(outpath='',topic_id="topic_0121", test_size=20))
    assert metafile_schema_validation(metadata_file)

@pytest.mark.asyncio
async def test_europepmc_request():
    protein_prophet_pmid = 14632076 #ProteinProphet has 2949 citations on Jul 12th 2024
    async with aiohttp.ClientSession() as session:
            citations = await europepmc_request(session, protein_prophet_pmid)
    assert len(citations)> 1000


def test_get_pmid_from_doi_create_file():
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(get_pmid_from_doi(outpath='',doi_tools= doi_list)) # TODO: what outpaths should I be using for these? 
    assert str(pmid_list[0]["pmid"]) == '23051804'

def test_get_pmid_from_doi_file_not_found():
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(get_pmid_from_doi(outpath='',doi_tools= doi_list, doi_lib_directory='fake/dir/')) # TODO: what outpaths should I be using for these? 
    assert str(pmid_list[0]["pmid"]) == '23051804'

def test_get_pmid_from_doi_from_file(shared_datadir):
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(get_pmid_from_doi(outpath='',doi_tools= doi_list, doi_lib_directory=shared_datadir)) # TODO: what outpaths should I be using for these? 
    assert str(pmid_list[0]["pmid"]) == '23051804' # Proteowizard PMID

def test_get_pmid_from_doi_from_file_with_updates(shared_datadir):
    doi_list = [{"name": "ProteoWizard", "doi": "10.1038/nbt.2377"}]
    pmid_list = asyncio.run(get_pmid_from_doi(outpath='',doi_tools= doi_list, doi_lib_directory=shared_datadir, doi_library_filename='doi_pmid_library_empty.json')) # TODO: what outpaths should I be using for these? 
    assert str(pmid_list[0]["pmid"]) == '23051804'

def test_get_pmids():
    test_size = 10
    pmid_tools, doi_tools, total_nr_tools  = asyncio.run(get_pmids(topic_id="topic_0121", test_size=test_size)) # TODO: I dont really know how to test if these random downloaded tools are correct
    print(pmid_tools, doi_tools, total_nr_tools) 
    # TODO: just checking some format things right now, could improve
    assert len(pmid_tools) + len(doi_tools) == test_size 
    assert total_nr_tools >= 1800 # As of August 2024 there are 1874 tools in the topic proteomics in bio.tools  
    assert type(pmid_tools[0]['name']) == str
    assert type(pmid_tools[0]['allPublications']) == list

def test_get_ages():
     tool_metadata = [
            {"name": "PeptideProphet",
            "doi": None,
            "topic": "Proteomics",
            "nrPublications": 1,
            "allPublications": [
                "12403597"
            ],
            "pmid": "12403597"
        },
     ]
     tool_metadata_inc_ages = asyncio.run(get_publication_dates(tool_metadata))
     tool_metadata_inc_ages[0]['pubDate'] == 2002