# WorkflowNo_5
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_5
doc: A workflow including the tool(s) msConvert, MassAI, X Hunter, XTandemPipeline, Libra.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_3:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
steps:
  msConvert_01:
    run: add-path-to-the-implementation/msConvert.cwl 
    in:
      msConvert_in_1: input_1
    out: [msConvert_out_1]
  MassAI_02:
    run: add-path-to-the-implementation/MassAI.cwl 
    in:
      MassAI_in_1: input_1
    out: [MassAI_out_1, MassAI_out_2]
  X Hunter_03:
    run: add-path-to-the-implementation/X Hunter.cwl 
    in:
      X Hunter_in_1: msConvert_01/msConvert_out_1
      X Hunter_in_2: MassAI_02/MassAI_out_2
      X Hunter_in_3: input_2
    out: [X Hunter_out_1]
  XTandemPipeline_04:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: X Hunter_03/X Hunter_out_1
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  Libra_05:
    run: add-path-to-the-implementation/Libra.cwl 
    in:
      Libra_in_1: XTandemPipeline_04/XTandemPipeline_out_1
    out: [Libra_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3655" # pepXML
    outputSource: Libra_05/Libra_out_1
