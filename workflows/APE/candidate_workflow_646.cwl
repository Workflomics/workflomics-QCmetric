# WorkflowNo_645
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_645
doc: A workflow including the tool(s) PEAKS De Novo, OpenSWATH, Mascot Server, MassChroQ, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3710" # WIFF format
  input_2:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
  input_3:
    type: File
    format: "http://edamontology.org/format_3246" # TraML
steps:
  PEAKS De Novo_01:
    run: add-path-to-the-implementation/PEAKS De Novo.cwl 
    in:
      PEAKS De Novo_in_1: input_1
    out: [PEAKS De Novo_out_1]
  OpenSWATH_02:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_2
      OpenSWATH_in_2: input_3
    out: [OpenSWATH_out_1]
  Mascot Server_03:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_02/OpenSWATH_out_1
      Mascot Server_in_2: PEAKS De Novo_01/PEAKS De Novo_out_1
    out: [Mascot Server_out_1]
  MassChroQ_04:
    run: add-path-to-the-implementation/MassChroQ.cwl 
    in:
      MassChroQ_in_1: Mascot Server_03/Mascot Server_out_1
    out: [MassChroQ_out_1]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: MassChroQ_04/MassChroQ_out_1
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenSWATH_05/OpenSWATH_out_1
