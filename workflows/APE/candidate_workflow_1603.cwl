# WorkflowNo_1602
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1602
doc: A workflow including the tool(s) msmsEDA, PPIExp, Graph Extract, MS-Fit, OpenMS.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_2:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
  input_3:
    type: File
    format: "http://edamontology.org/format_3652" # dta
steps:
  msmsEDA_01:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_1
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  PPIExp_02:
    run: add-path-to-the-implementation/PPIExp.cwl 
    in:
      PPIExp_in_1: msmsEDA_01/msmsEDA_out_2
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
  OpenMS_05:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_3
      OpenMS_in_3: MS-Fit_04/MS-Fit_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenMS_05/OpenMS_out_1
