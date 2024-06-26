# WorkflowNo_246
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_246
doc: A workflow including the tool(s) MaxQuant, CrosstalkDB, Graph Extract, MS-Fit, Multi-Q.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_2:
    type: File
    format: "http://edamontology.org/format_1996" # pair
  input_3:
    type: File
    format: "http://edamontology.org/format_3620" # xlsx
steps:
  MaxQuant_01:
    run: add-path-to-the-implementation/MaxQuant.cwl 
    in:
      MaxQuant_in_1: input_3
    out: [MaxQuant_out_1, MaxQuant_out_2]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: MaxQuant_01/MaxQuant_out_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  Graph Extract_03:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: CrosstalkDB_02/CrosstalkDB_out_2
    out: [Graph Extract_out_1]
  MS-Fit_04:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: Graph Extract_03/Graph Extract_out_1
    out: [MS-Fit_out_1]
  Multi-Q_05:
    run: add-path-to-the-implementation/Multi-Q.cwl 
    in:
      Multi-Q_in_1: input_1
      Multi-Q_in_2: MS-Fit_04/MS-Fit_out_1
    out: [Multi-Q_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
    outputSource: Multi-Q_05/Multi-Q_out_1
