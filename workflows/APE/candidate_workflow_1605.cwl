# WorkflowNo_1604
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1604
doc: A workflow including the tool(s) massXpert, MZmine, Graph Extract, ComPIL, OpenMS.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_2:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
  input_3:
    type: File
    format: "http://edamontology.org/format_3155" # SBRML
steps:
  massXpert_01:
    run: add-path-to-the-implementation/massXpert.cwl 
    in:
      massXpert_in_1: input_2
      massXpert_in_2: input_3
    out: [massXpert_out_1, massXpert_out_2]
  MZmine_02:
    run: add-path-to-the-implementation/MZmine.cwl 
    in:
      MZmine_in_1: input_1
    out: [MZmine_out_1, MZmine_out_2, MZmine_out_3]
  Graph Extract_03:
    run: add-path-to-the-implementation/Graph Extract.cwl 
    in:
      Graph Extract_in_1: MZmine_02/MZmine_out_3
    out: [Graph Extract_out_1]
  ComPIL_04:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: Graph Extract_03/Graph Extract_out_1
    out: [ComPIL_out_1]
  OpenMS_05:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: massXpert_01/massXpert_out_2
      OpenMS_in_3: ComPIL_04/ComPIL_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenMS_05/OpenMS_out_1
