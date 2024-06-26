# WorkflowNo_111
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_111
doc: A workflow including the tool(s) OpenSWATH, Mascot Server, XTandemPipeline, MaxQuant, MSiReader.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3246" # TraML
steps:
  OpenSWATH_01:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_1
      OpenSWATH_in_2: input_3
    out: [OpenSWATH_out_1]
  Mascot Server_02:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_01/OpenSWATH_out_1
      Mascot Server_in_2: input_1
    out: [Mascot Server_out_1]
  XTandemPipeline_03:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: Mascot Server_02/Mascot Server_out_1
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  MaxQuant_04:
    run: add-path-to-the-implementation/MaxQuant.cwl 
    in:
      MaxQuant_in_1: XTandemPipeline_03/XTandemPipeline_out_1
    out: [MaxQuant_out_1, MaxQuant_out_2]
  MSiReader_05:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_2
      MSiReader_in_2: MaxQuant_04/MaxQuant_out_1
    out: [MSiReader_out_1, MSiReader_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3620" # xlsx
    outputSource: MSiReader_05/MSiReader_out_1
