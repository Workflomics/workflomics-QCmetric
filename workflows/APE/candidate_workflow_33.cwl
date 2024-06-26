# WorkflowNo_32
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_32
doc: A workflow including the tool(s) CrosstalkDB, Graph Extract, InDigestion, EncyclopeDIA, Multi-Q.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_3
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  Graph Extract_02:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: CrosstalkDB_01/CrosstalkDB_out_3
    out: [Graph Extract_out_1]
  InDigestion_03:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: Graph Extract_02/Graph Extract_out_1
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  EncyclopeDIA_04:
    run: add-path-to-the-implementation/EncyclopeDIA.cwl 
    in:
      EncyclopeDIA_in_1: input_1
      EncyclopeDIA_in_2: InDigestion_03/InDigestion_out_3
    out: [EncyclopeDIA_out_1]
  Multi-Q_05:
    run: add-path-to-the-implementation/Multi-Q.cwl 
    in:
      Multi-Q_in_1: input_2
      Multi-Q_in_2: EncyclopeDIA_04/EncyclopeDIA_out_1
    out: [Multi-Q_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
    outputSource: Multi-Q_05/Multi-Q_out_1
