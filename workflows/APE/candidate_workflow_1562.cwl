# WorkflowNo_1561
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1561
doc: A workflow including the tool(s) MassWiz, PEAKS Q, CrosstalkDB, msmsEDA, ComplexBrowser.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3653" # pkl
  input_2:
    type: File
    format: "http://edamontology.org/format_3702" # MSF
  input_3:
    type: File
    format: "http://edamontology.org/format_3330" # PO
steps:
  MassWiz_01:
    run: add-path-to-the-implementation/MassWiz.cwl 
    in:
      MassWiz_in_1: input_1
    out: [MassWiz_out_1]
  PEAKS Q_02:
    run: add-path-to-the-implementation/PEAKS Q.cwl 
    in:
      PEAKS Q_in_1: MassWiz_01/MassWiz_out_1
    out: [PEAKS Q_out_1]
  CrosstalkDB_03:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: PEAKS Q_02/PEAKS Q_out_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  msmsEDA_04:
    run: add-path-to-the-implementation/msmsEDA.cwl 
    in:
      msmsEDA_in_1: input_2
    out: [msmsEDA_out_1, msmsEDA_out_2, msmsEDA_out_3]
  ComplexBrowser_05:
    run: add-path-to-the-implementation/ComplexBrowser.cwl 
    in:
      ComplexBrowser_in_1: msmsEDA_04/msmsEDA_out_2
      ComplexBrowser_in_2: CrosstalkDB_03/CrosstalkDB_out_1
    out: [ComplexBrowser_out_1, ComplexBrowser_out_2, ComplexBrowser_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3508" # PDF
    outputSource: ComplexBrowser_05/ComplexBrowser_out_1
