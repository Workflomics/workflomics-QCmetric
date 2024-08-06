from pubmetric.exceptions import SchemaValidationError

required_meta_keys = {
    "creationDate": str,
    "topic": str,
    "totalNrTools": int,
    "biotoolsWOpmid": int,
    "nrpmidfromdoi": int,
    "tools": list
}

required_meta_tool_keys = {
    "name": str,
    "doi": str,
    "topics": list,
    "nrPublications": int,
    "allPublications": list,
    "pubDate": int,
    "pmid": str
}

def metafile_schema_validation(metadata_file):
    """
    Checks that the metadatafile follows the correct 

    :param metadata_file: The dictionary of tool matadata. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    
    """
    if not all(key in metadata_file and isinstance(metadata_file[key], required_meta_keys[key]) for key in required_meta_keys):
        raise SchemaValidationError("The schema of the top layer of the metadata file is incorrect.")
    
    tool = metadata_file["tools"][0] # check only first cause otherwise it takes too much time 
    if not all(key in tool and isinstance(tool[key], required_meta_tool_keys[key]) for key in required_meta_tool_keys):
        raise SchemaValidationError("The schema of the tool metadata is incorrect.")
    
    return True

