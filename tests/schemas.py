from pubmetric.exceptions import SchemaValidationError

required_meta_keys = {
    "creation_date": str,
    "topic": (str, type(None)),
    "total_nr_tools": int,
    "biotools_wo_pmid": int,
    "pmid_from_doi": int,
    "tools": list
}

required_meta_tool_keys = {
    "name": str,
    "doi": (str, type(None)),
    "topics": list,
    "nr_publications": int,
    "all_publications": list,
    "publication_date": (int, type(None)),
    "pmid": (str, type(None))
}

def metafile_schema_validation(metadata_file):
    """
    Checks that the metadatafile follows the correct 

    :param metadata_file: The dictionary of tool matadata. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    
    """
    if not all(key in metadata_file and isinstance(metadata_file[key], required_meta_keys[key]) for key in required_meta_keys):
        raise SchemaValidationError("The schema of the top layer of the metadata file is incorrect.")
    
    tool = metadata_file["tools"][0] # check only first cause otherwise it takes too much time
    print(tool)
    if not all(key in tool and isinstance(tool[key], required_meta_tool_keys[key]) for key in required_meta_tool_keys):
        print([(tool[key], required_meta_tool_keys[key]) for key in required_meta_tool_keys])
        raise SchemaValidationError("The schema of the tool metadata is incorrect.")
    
    return True

