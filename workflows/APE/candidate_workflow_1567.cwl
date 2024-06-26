# WorkflowNo_1566
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1566
doc: A workflow including the tool(s) InDigestion, MS-GF+, MFPaQ, PeptideProphet, Libra.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1996" # pair
  input_2:
    type: File
    format: "http://edamontology.org/format_1342" # InterPro protein view report format
  input_3:
    type: File
    format: "http://edamontology.org/format_3653" # pkl
steps:
  InDigestion_01:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_2
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  MS-GF+_02:
    run: add-path-to-the-implementation/MS-GF+.cwl 
    in:
      MS-GF+_in_1: input_3
      MS-GF+_in_2: InDigestion_01/InDigestion_out_3
    out: [MS-GF+_out_1, MS-GF+_out_2]
  MFPaQ_03:
    run: add-path-to-the-implementation/MFPaQ.cwl 
    in:
      MFPaQ_in_1: MS-GF+_02/MS-GF+_out_1
    out: [MFPaQ_out_1]
  PeptideProphet_04:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: MFPaQ_03/MFPaQ_out_1
    out: [PeptideProphet_out_1]
  Libra_05:
    run: add-path-to-the-implementation/Libra.cwl 
    in:
      Libra_in_1: PeptideProphet_04/PeptideProphet_out_1
    out: [Libra_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: Libra_05/Libra_out_1
