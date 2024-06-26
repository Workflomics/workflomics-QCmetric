# WorkflowNo_1414
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1414
doc: A workflow including the tool(s) CrosstalkDB, CrosstalkDB, MS-Fit, OpenMS, ComplexBrowser.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_2549" # OBO
  input_2:
    type: File
    format: "http://edamontology.org/format_3604" # SVG
  input_3:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_3
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: CrosstalkDB_01/CrosstalkDB_out_3
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  MS-Fit_03:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: input_1
    out: [MS-Fit_out_1]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_2
      OpenMS_in_3: MS-Fit_03/MS-Fit_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  ComplexBrowser_05:
    run: add-path-to-the-implementation/ComplexBrowser.cwl 
    in:
      ComplexBrowser_in_1: OpenMS_04/OpenMS_out_2
      ComplexBrowser_in_2: CrosstalkDB_02/CrosstalkDB_out_4
    out: [ComplexBrowser_out_1, ComplexBrowser_out_2, ComplexBrowser_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: ComplexBrowser_05/ComplexBrowser_out_1
