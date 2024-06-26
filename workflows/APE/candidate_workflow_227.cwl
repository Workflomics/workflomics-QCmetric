# WorkflowNo_226
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_226
doc: A workflow including the tool(s) DeconMSn, CrosstalkDB, MSiReader, ComPIL, isobar.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
  input_2:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_3:
    type: File
    format: "http://edamontology.org/format_3813" # SAMPLE file format
steps:
  DeconMSn_01:
    run: add-path-to-the-implementation/DeconMSn.cwl 
    in:
      DeconMSn_in_1: input_1
      DeconMSn_in_2: input_1
    out: [DeconMSn_out_1, DeconMSn_out_2, DeconMSn_out_3]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_2
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  MSiReader_03:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_3
      MSiReader_in_2: CrosstalkDB_02/CrosstalkDB_out_2
    out: [MSiReader_out_1, MSiReader_out_2]
  ComPIL_04:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: MSiReader_03/MSiReader_out_2
    out: [ComPIL_out_1]
  isobar_05:
    run: add-path-to-the-implementation/isobar.cwl 
    in:
      isobar_in_1: DeconMSn_01/DeconMSn_out_1
      isobar_in_2: ComPIL_04/ComPIL_out_1
    out: [isobar_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: isobar_05/isobar_out_1
