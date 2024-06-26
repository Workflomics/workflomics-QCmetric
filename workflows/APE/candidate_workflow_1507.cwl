# WorkflowNo_1506
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1506
doc: A workflow including the tool(s) PGA, PeptideProphet, OpenMS, RelEx, SCENERY.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3016" # VCF
  input_2:
    type: File
    format: "http://edamontology.org/format_2311" # EMBL-HTML
  input_3:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
steps:
  PGA_01:
    run: add-path-to-the-implementation/PGA.cwl 
    in:
      PGA_in_1: input_1
    out: [PGA_out_1]
  PeptideProphet_02:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: input_2
    out: [PeptideProphet_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: PGA_01/PGA_out_1
      OpenMS_in_3: PeptideProphet_02/PeptideProphet_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  RelEx_04:
    run: add-path-to-the-implementation/RelEx.cwl 
    in:
      RelEx_in_1: OpenMS_03/OpenMS_out_1
    out: [RelEx_out_1]
  SCENERY_05:
    run: add-path-to-the-implementation/SCENERY.cwl 
    in:
      SCENERY_in_1: RelEx_04/RelEx_out_1
    out: [SCENERY_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_2532" # GenBank-HTML
    outputSource: SCENERY_05/SCENERY_out_1
