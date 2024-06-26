# WorkflowNo_345
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_345
doc: A workflow including the tool(s) PEAKS DB, OpenMS, ASAPRatio, OpenSWATH, DeconMSn.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  PEAKS DB_01:
    run: add-path-to-the-implementation/PEAKS DB.cwl 
    in:
      PEAKS DB_in_1: input_3
      PEAKS DB_in_2: input_1
    out: [PEAKS DB_out_1, PEAKS DB_out_2]
  OpenMS_02:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: input_1
      OpenMS_in_3: PEAKS DB_01/PEAKS DB_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  ASAPRatio_03:
    run: add-path-to-the-implementation/ASAPRatio.cwl 
    in:
      ASAPRatio_in_1: OpenMS_02/OpenMS_out_1
    out: [ASAPRatio_out_1, ASAPRatio_out_2]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: ASAPRatio_03/ASAPRatio_out_2
    out: [OpenSWATH_out_1]
  DeconMSn_05:
    run: add-path-to-the-implementation/DeconMSn.cwl 
    in:
      DeconMSn_in_1: input_2
      DeconMSn_in_2: OpenSWATH_04/OpenSWATH_out_1
    out: [DeconMSn_out_1, DeconMSn_out_2, DeconMSn_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
    outputSource: DeconMSn_05/DeconMSn_out_1
