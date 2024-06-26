# WorkflowNo_1215
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1215
doc: A workflow including the tool(s) msmsEDA, MSiReader, Xtractor, ComPIL, isobar.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3650" # netCDF
  input_2:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_3:
    type: File
    format: "http://edamontology.org/format_3609" # qualillumina
steps:
  msmsEDA_01:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_1
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  MSiReader_02:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_3
      MSiReader_in_2: msmsEDA_01/msmsEDA_out_3
    out: [MSiReader_out_1, MSiReader_out_2]
  Xtractor_03:
    run: add-path-to-the-implementation/Xtractor.cwl 
    in:
      Xtractor_in_1: MSiReader_02/MSiReader_out_2
      Xtractor_in_2: input_3
      Xtractor_in_3: MSiReader_02/MSiReader_out_2
    out: [Xtractor_out_1, Xtractor_out_2, Xtractor_out_3]
  ComPIL_04:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: Xtractor_03/Xtractor_out_1
    out: [ComPIL_out_1]
  isobar_05:
    run: add-path-to-the-implementation/isobar.cwl 
    in:
      isobar_in_1: input_2
      isobar_in_2: ComPIL_04/ComPIL_out_1
    out: [isobar_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: isobar_05/isobar_out_1
