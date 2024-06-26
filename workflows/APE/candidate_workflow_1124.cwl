# WorkflowNo_1123
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1123
doc: A workflow including the tool(s) InDigestion, XTandem, msaccess, XTandemPipeline, Quant.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_1631" # EXP
  input_3:
    type: File
    format: "http://edamontology.org/format_3652" # dta
steps:
  InDigestion_01:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_2
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  XTandem_02:
    run: add-path-to-the-implementation/XTandem.cwl 
    in:
      XTandem_in_1: input_1
      XTandem_in_2: InDigestion_01/InDigestion_out_3
    out: [XTandem_out_1]
  msaccess_03:
    run: add-path-to-the-implementation/msaccess.cwl 
    in:
      msaccess_in_1: input_1
      msaccess_in_2: XTandem_02/XTandem_out_1
    out: [msaccess_out_1, msaccess_out_2, msaccess_out_3]
  XTandemPipeline_04:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: msaccess_03/msaccess_out_2
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  Quant_05:
    run: add-path-to-the-implementation/Quant.cwl 
    in:
      Quant_in_1: input_3
      Quant_in_2: XTandemPipeline_04/XTandemPipeline_out_1
    out: [Quant_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: Quant_05/Quant_out_1
