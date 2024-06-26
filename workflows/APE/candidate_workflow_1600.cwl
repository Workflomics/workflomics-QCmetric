# WorkflowNo_1577
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1577
doc: A workflow including the tool(s) DeconMSn, PEAKS DB, OpenMS, msaccess, Mayu.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
steps:
  DeconMSn_01:
    run: add-path-to-the-implementation/DeconMSn.cwl 
    in:
      DeconMSn_in_1: input_1
      DeconMSn_in_2: input_1
    out: [DeconMSn_out_1, DeconMSn_out_2, DeconMSn_out_3]
  PEAKS DB_02:
    run: add-path-to-the-implementation/PEAKS DB.cwl 
    in:
      PEAKS DB_in_1: DeconMSn_01/DeconMSn_out_3
      PEAKS DB_in_2: input_2
    out: [PEAKS DB_out_1, PEAKS DB_out_2]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: input_2
      OpenMS_in_3: PEAKS DB_02/PEAKS DB_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  msaccess_04:
    run: add-path-to-the-implementation/msaccess.cwl 
    in:
      msaccess_in_1: DeconMSn_01/DeconMSn_out_2
      msaccess_in_2: OpenMS_03/OpenMS_out_1
    out: [msaccess_out_1, msaccess_out_2, msaccess_out_3]
  Mayu_05:
    run: add-path-to-the-implementation/Mayu.cwl 
    in:
      Mayu_in_1: input_2
      Mayu_in_2: msaccess_04/msaccess_out_2
    out: [Mayu_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3728" # LocARNA PP
    outputSource: Mayu_05/Mayu_out_1
