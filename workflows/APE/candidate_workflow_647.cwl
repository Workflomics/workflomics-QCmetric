# WorkflowNo_646
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_646
doc: A workflow including the tool(s) ProMEX protein mass spectral library, OpenSWATH, Mascot Server, MassChroQ, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3773" # BioYAML
  input_2:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
  input_3:
    type: File
    format: "http://edamontology.org/format_3246" # TraML
steps:
  ProMEX protein mass spectral library_01:
    run: add-path-to-the-implementation/ProMEX protein mass spectral library.cwl 
    in:
      ProMEX protein mass spectral library_in_1: input_1
    out: [ProMEX protein mass spectral library_out_1]
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
      Mascot Server_in_2: ProMEX protein mass spectral library_01/ProMEX protein mass spectral library_out_1
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
