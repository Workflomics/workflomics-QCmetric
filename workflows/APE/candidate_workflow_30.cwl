# WorkflowNo_27
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_27
doc: A workflow including the tool(s) PChopper, esimsa2D, ComPIL, multiplierz, ICPLQuant.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1937" # genpept
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
steps:
  PChopper_01:
    run: add-path-to-the-implementation/PChopper.cwl 
    in:
      PChopper_in_1: input_2
    out: [PChopper_out_1]
  esimsa2D_02:
    run: add-path-to-the-implementation/esimsa2D.cwl 
    in:
      esimsa2D_in_1: input_2
      esimsa2D_in_2: PChopper_01/PChopper_out_1
      esimsa2D_in_3: input_1
    out: [esimsa2D_out_1, esimsa2D_out_2, esimsa2D_out_3]
  ComPIL_03:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: input_1
    out: [ComPIL_out_1]
  multiplierz_04:
    run: add-path-to-the-implementation/multiplierz.cwl 
    in:
      multiplierz_in_1: esimsa2D_02/esimsa2D_out_2
      multiplierz_in_2: input_3
    out: [multiplierz_out_1]
  ICPLQuant_05:
    run: add-path-to-the-implementation/ICPLQuant.cwl 
    in:
      ICPLQuant_in_1: esimsa2D_02/esimsa2D_out_2
      ICPLQuant_in_2: multiplierz_04/multiplierz_out_1
      ICPLQuant_in_3: ComPIL_03/ComPIL_out_1
    out: [ICPLQuant_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3468" # xls
    outputSource: ICPLQuant_05/ICPLQuant_out_1
