# WorkflowNo_231
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_231
doc: A workflow including the tool(s) MSGraph, CrosstalkDB, MSiReader, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_2:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_3:
    type: File
    format: "http://edamontology.org/format_3702" # MSF
steps:
  MSGraph_01:
    run: add-path-to-the-implementation/MSGraph.cwl 
    in:
      MSGraph_in_1: input_3
    out: [MSGraph_out_1, MSGraph_out_2]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  MSiReader_03:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_2
      MSiReader_in_2: CrosstalkDB_02/CrosstalkDB_out_3
    out: [MSiReader_out_1, MSiReader_out_2]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_2
      OpenSWATH_in_2: MSGraph_01/MSGraph_out_1
    out: [OpenSWATH_out_1]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_04/OpenSWATH_out_1
      Mascot Server_in_2: MSiReader_03/MSiReader_out_2
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
    outputSource: Mascot Server_05/Mascot Server_out_1
