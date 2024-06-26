# WorkflowNo_1072
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1072
doc: A workflow including the tool(s) MSGraph, esimsa2D, esimsa2D, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1984" # FASTA-aln
  input_2:
    type: File
    format: "http://edamontology.org/format_3681" # mzTab
  input_3:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
steps:
  MSGraph_01:
    run: add-path-to-the-implementation/MSGraph.cwl 
    in:
      MSGraph_in_1: input_2
    out: [MSGraph_out_1, MSGraph_out_2]
  esimsa2D_02:
    run: add-path-to-the-implementation/esimsa2D.cwl 
    in:
      esimsa2D_in_1: input_1
      esimsa2D_in_2: input_2
      esimsa2D_in_3: input_2
    out: [esimsa2D_out_1, esimsa2D_out_2, esimsa2D_out_3]
  esimsa2D_03:
    run: add-path-to-the-implementation/esimsa2D.cwl 
    in:
      esimsa2D_in_1: esimsa2D_02/esimsa2D_out_3
      esimsa2D_in_2: input_2
      esimsa2D_in_3: MSGraph_01/MSGraph_out_1
    out: [esimsa2D_out_1, esimsa2D_out_2, esimsa2D_out_3]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_3
      OpenSWATH_in_2: MSGraph_01/MSGraph_out_1
    out: [OpenSWATH_out_1]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_04/OpenSWATH_out_1
      Mascot Server_in_2: esimsa2D_03/esimsa2D_out_2
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
    outputSource: Mascot Server_05/Mascot Server_out_1
