from wfqc import data
import pytest
import os 
import asyncio
import aiohttp
import nest_asyncio 



@pytest.mark.asyncio
async def test_get_tool_metadata(shared_datadir):
    tmp_dir='tmp_out'
    os.system(f'mkdir {tmp_dir}')
    df = await data.get_tool_metadata(outpath=tmp_dir)
    os.system(f'rm -rf {tmp_dir}') # maybe not the best method?
    assert df.loc[df['name'] == 'PEPMatch', 'pmid'].values[0] == str(38110863)


@pytest.mark.asyncio
async def test_europepmc_request(shared_datadir):
    ProteinProphet_pmid = 14632076 #ProteinProphet has 2949 citations on Jul 12th 2024
    async with aiohttp.ClientSession() as session:
            citations = await data.europepmc_request(session, 14632076)
            print(citations)
    assert len(citations)> 1000


def get_pmids_from_file(shared_datadir):
    
    print('')

def test_get_pmid_from_doi(shared_datadir):
    filename = os.path.join(shared_datadir, "doi_pmid_library_empty.json")
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}, {"name": "DIAgui", "doi": "10.1093/bioadv/vbae001"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, filename))
    assert str(pmid_list[0]["pmid"]) == '33538780'
    assert str(pmid_list[1]["pmid"]) == '38249340'

def test_get_pmid_from_doi_library(shared_datadir):
    filename = os.path.join(shared_datadir, "doi_pmid_library.json")
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, doi_library_filename = filename))
    print(pmid_list)
    assert str(pmid_list[0]["pmid"]) == '33538780'


# get_tool_metadata
def test_get_tool_metadata():
    print('')

def test_old_get_tool_metadata():
    print('')

def test_existing_file_get_tool_metadata():
    print('')
    