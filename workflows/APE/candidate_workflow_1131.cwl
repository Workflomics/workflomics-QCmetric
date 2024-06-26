# WorkflowNo_1130
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1130
doc: A workflow including the tool(s) CrosstalkDB, CrosstalkDB, XTandemPipeline, Multi-Q, ComplexBrowser.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_2:
    type: File
    format: "http://edamontology.org/format_3711" # X!Tandem XML
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
  XTandemPipeline_03:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_2
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  Multi-Q_04:
    run: add-path-to-the-implementation/Multi-Q.cwl 
    in:
      Multi-Q_in_1: input_1
      Multi-Q_in_2: XTandemPipeline_03/XTandemPipeline_out_1
    out: [Multi-Q_out_1]
  ComplexBrowser_05:
    run: add-path-to-the-implementation/ComplexBrowser.cwl 
    in:
      ComplexBrowser_in_1: Multi-Q_04/Multi-Q_out_1
      ComplexBrowser_in_2: CrosstalkDB_02/CrosstalkDB_out_4
    out: [ComplexBrowser_out_1, ComplexBrowser_out_2, ComplexBrowser_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: ComplexBrowser_05/ComplexBrowser_out_1
