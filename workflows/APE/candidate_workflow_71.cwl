# WorkflowNo_70
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_70
doc: A workflow including the tool(s) CPM, nontarget, Xtractor, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3758" # SEQUEST .out file
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3691" # BEL
steps:
  CPM_01:
    run: add-path-to-the-implementation/CPM.cwl 
    in:
      CPM_in_1: input_1
      CPM_in_2: input_1
    out: [CPM_out_1, CPM_out_2]
  nontarget_02:
    run: add-path-to-the-implementation/nontarget.cwl 
    in:
      nontarget_in_1: input_3
      nontarget_in_2: input_1
      nontarget_in_3: input_3
    out: [nontarget_out_1, nontarget_out_2, nontarget_out_3]
  Xtractor_03:
    run: add-path-to-the-implementation/Xtractor.cwl 
    in:
      Xtractor_in_1: input_1
      Xtractor_in_2: CPM_01/CPM_out_2
      Xtractor_in_3: input_3
    out: [Xtractor_out_1, Xtractor_out_2, Xtractor_out_3]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_2
      OpenSWATH_in_2: nontarget_02/nontarget_out_3
    out: [OpenSWATH_out_1]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_04/OpenSWATH_out_1
      Mascot Server_in_2: Xtractor_03/Xtractor_out_3
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3157" # EBI Application Result XML
    outputSource: Mascot Server_05/Mascot Server_out_1
