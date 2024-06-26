# WorkflowNo_1554
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1554
doc: A workflow including the tool(s) PChopper, ProFound, OpenMS, OpenMS, PeptideShaker.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3155" # SBRML
steps:
  PChopper_01:
    run: add-path-to-the-implementation/PChopper.cwl 
    in:
      PChopper_in_1: input_2
    out: [PChopper_out_1]
  ProFound_02:
    run: add-path-to-the-implementation/ProFound.cwl 
    in:
      ProFound_in_1: input_2
    out: [ProFound_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_2
      OpenMS_in_2: input_3
      OpenMS_in_3: ProFound_02/ProFound_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_3
      OpenMS_in_3: OpenMS_03/OpenMS_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  PeptideShaker_05:
    run: add-path-to-the-implementation/PeptideShaker.cwl 
    in:
      PeptideShaker_in_1: PChopper_01/PChopper_out_1
      PeptideShaker_in_2: OpenMS_04/OpenMS_out_1
      PeptideShaker_in_3: input_1
    out: [PeptideShaker_out_1, PeptideShaker_out_2, PeptideShaker_out_3, PeptideShaker_out_4]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3579" # JPG
    outputSource: PeptideShaker_05/PeptideShaker_out_1
