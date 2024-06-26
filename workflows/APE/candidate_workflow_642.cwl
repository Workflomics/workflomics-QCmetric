# WorkflowNo_641
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_641
doc: A workflow including the tool(s) Graph Extract, nontarget, lutefisk, MyriMatch, Libra.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3710" # WIFF format
  input_2:
    type: File
    format: "http://edamontology.org/format_3551" # nrrd
  input_3:
    type: File
    format: "http://edamontology.org/format_1963" # UniProtKB format
steps:
  Graph Extract_01:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: input_2
    out: [Graph Extract_out_1]
  nontarget_02:
    run: add-path-to-the-implementation/nontarget.cwl 
    in:
      nontarget_in_1: input_2
      nontarget_in_2: input_2
      nontarget_in_3: input_3
    out: [nontarget_out_1, nontarget_out_2, nontarget_out_3]
  lutefisk_03:
    run: add-path-to-the-implementation/lutefisk.cwl 
    in:
      lutefisk_in_1: nontarget_02/nontarget_out_3
      lutefisk_in_2: Graph Extract_01/Graph Extract_out_1
    out: [lutefisk_out_1]
  MyriMatch_04:
    run: add-path-to-the-implementation/MyriMatch.cwl 
    in:
      MyriMatch_in_1: input_1
      MyriMatch_in_2: lutefisk_03/lutefisk_out_1
    out: [MyriMatch_out_1]
  Libra_05:
    run: add-path-to-the-implementation/Libra.cwl 
    in:
      Libra_in_1: MyriMatch_04/MyriMatch_out_1
    out: [Libra_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: Libra_05/Libra_out_1
