# WorkflowNo_725
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_725
doc: A workflow including the tool(s) PChopper, EncyclopeDIA, OpenSWATH, OpenMS, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
  input_3:
    type: File
    format: "http://edamontology.org/format_3246" # TraML
steps:
  PChopper_01:
    run: add-path-to-the-implementation/PChopper.cwl 
    in:
      PChopper_in_1: input_1
    out: [PChopper_out_1]
  EncyclopeDIA_02:
    run: add-path-to-the-implementation/EncyclopeDIA.cwl 
    in:
      EncyclopeDIA_in_1: input_2
      EncyclopeDIA_in_2: input_1
    out: [EncyclopeDIA_out_1]
  OpenSWATH_03:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_2
      OpenSWATH_in_2: input_3
    out: [OpenSWATH_out_1]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: OpenSWATH_03/OpenSWATH_out_1
      OpenMS_in_2: PChopper_01/PChopper_out_1
      OpenMS_in_3: EncyclopeDIA_02/EncyclopeDIA_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: OpenMS_04/OpenMS_out_2
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenSWATH_05/OpenSWATH_out_1
