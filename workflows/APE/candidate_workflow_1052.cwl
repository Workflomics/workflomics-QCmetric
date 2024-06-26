# WorkflowNo_1051
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1051
doc: A workflow including the tool(s) XTandemPipeline, OpenMS, TMHMM, mzStar, MSiReader.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3758" # SEQUEST .out file
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3652" # dta
steps:
  XTandemPipeline_01:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_1
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  OpenMS_02:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: input_2
      OpenMS_in_3: XTandemPipeline_01/XTandemPipeline_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  TMHMM_03:
    run: add-path-to-the-implementation/TMHMM.cwl 
    in:
      TMHMM_in_1: input_2
    out: [TMHMM_out_1, TMHMM_out_2]
  mzStar_04:
    run: add-path-to-the-implementation/mzStar.cwl 
    in:
      mzStar_in_1: TMHMM_03/TMHMM_out_2
    out: [mzStar_out_1]
  MSiReader_05:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: mzStar_04/mzStar_out_1
      MSiReader_in_2: OpenMS_02/OpenMS_out_2
    out: [MSiReader_out_1, MSiReader_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3592" # BMP
    outputSource: MSiReader_05/MSiReader_out_1
