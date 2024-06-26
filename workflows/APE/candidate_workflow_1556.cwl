# WorkflowNo_1555
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1555
doc: A workflow including the tool(s) MSD File Reader, InDigestion, MS-GF+, OpenMS, PeptideShaker.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_3653" # pkl
  input_3:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
steps:
  MSD File Reader_01:
    run: add-path-to-the-implementation/MSD File Reader.cwl 
    in: []
    out: [MSD File Reader_out_1]
  InDigestion_02:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: MSD File Reader_01/MSD File Reader_out_1
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  MS-GF+_03:
    run: add-path-to-the-implementation/MS-GF+.cwl 
    in:
      MS-GF+_in_1: input_2
      MS-GF+_in_2: InDigestion_02/InDigestion_out_3
    out: [MS-GF+_out_1, MS-GF+_out_2]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_3
      OpenMS_in_3: MS-GF+_03/MS-GF+_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  PeptideShaker_05:
    run: add-path-to-the-implementation/PeptideShaker.cwl 
    in:
      PeptideShaker_in_1: input_3
      PeptideShaker_in_2: OpenMS_04/OpenMS_out_1
      PeptideShaker_in_3: input_1
    out: [PeptideShaker_out_1, PeptideShaker_out_2, PeptideShaker_out_3, PeptideShaker_out_4]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3579" # JPG
    outputSource: PeptideShaker_05/PeptideShaker_out_1
