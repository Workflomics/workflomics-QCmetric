# WorkflowNo_1125
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1125
doc: A workflow including the tool(s) msmsEDA, PPIExp, Graph Extract, MS-Fit, Quant.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3911" # msh
  input_2:
    type: File
    format: "http://edamontology.org/format_3702" # MSF
  input_3:
    type: File
    format: "http://edamontology.org/format_3652" # dta
steps:
  msmsEDA_01:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_2
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  PPIExp_02:
    run: add-path-to-the-implementation/PPIExp.cwl 
    in:
      PPIExp_in_1: msmsEDA_01/msmsEDA_out_3
    out: [PPIExp_out_1, PPIExp_out_2]
  Graph Extract_03:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: PPIExp_02/PPIExp_out_2
    out: [Graph Extract_out_1]
  MS-Fit_04:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: Graph Extract_03/Graph Extract_out_1
    out: [MS-Fit_out_1]
  Quant_05:
    run: add-path-to-the-implementation/Quant.cwl 
    in:
      Quant_in_1: input_3
      Quant_in_2: MS-Fit_04/MS-Fit_out_1
    out: [Quant_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: Quant_05/Quant_out_1
