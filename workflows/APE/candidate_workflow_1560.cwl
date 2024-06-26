# WorkflowNo_1557
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1557
doc: A workflow including the tool(s) InfernoRDN, CrosstalkDB, Graph Extract, PECAN (PEptide-Centric Analysis), Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3620" # xlsx
  input_2:
    type: File
    format: "http://edamontology.org/format_1996" # pair
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  InfernoRDN_01:
    run: add-path-to-the-implementation/InfernoRDN.cwl 
    in:
      InfernoRDN_in_1: input_1
    out: [InfernoRDN_out_1, InfernoRDN_out_2]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: InfernoRDN_01/InfernoRDN_out_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  Graph Extract_03:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: CrosstalkDB_02/CrosstalkDB_out_2
    out: [Graph Extract_out_1]
  PECAN (PEptide-Centric Analysis)_04:
    run: add-path-to-the-implementation/PECAN (PEptide-Centric Analysis).cwl 
    in:
      PECAN (PEptide-Centric Analysis)_in_1: input_3
      PECAN (PEptide-Centric Analysis)_in_2: Graph Extract_03/Graph Extract_out_1
    out: [PECAN (PEptide-Centric Analysis)_out_1, PECAN (PEptide-Centric Analysis)_out_2]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: input_2
      Mascot Server_in_2: PECAN (PEptide-Centric Analysis)_04/PECAN (PEptide-Centric Analysis)_out_2
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
    outputSource: Mascot Server_05/Mascot Server_out_1
