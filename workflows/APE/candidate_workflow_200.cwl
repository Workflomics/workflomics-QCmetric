# WorkflowNo_177
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_177
doc: A workflow including the tool(s) Jtraml, DECIPHER, Graph Extract, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1628" # ABI
  input_2:
    type: File
    format: "http://edamontology.org/format_1930" # FASTQ
  input_3:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
steps:
  Jtraml_01:
    run: add-path-to-the-implementation/Jtraml.cwl 
    in:
      Jtraml_in_1: input_1
    out: [Jtraml_out_1]
  DECIPHER_02:
    run: add-path-to-the-implementation/DECIPHER.cwl 
    in:
      DECIPHER_in_1: input_2
      DECIPHER_in_2: Jtraml_01/Jtraml_out_1
    out: [DECIPHER_out_1, DECIPHER_out_2]
  Graph Extract_03:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: DECIPHER_02/DECIPHER_out_1
    out: [Graph Extract_out_1]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_3
      OpenSWATH_in_2: Graph Extract_03/Graph Extract_out_1
    out: [OpenSWATH_out_1]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_04/OpenSWATH_out_1
      Mascot Server_in_2: input_3
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
    outputSource: Mascot Server_05/Mascot Server_out_1
