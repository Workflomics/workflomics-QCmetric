# WorkflowNo_51
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_51
doc: A workflow including the tool(s) MS-Fit, OpenMS, PChopper, esimsa, esimsa.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1741" # OSCAR format
  input_2:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
  input_3:
    type: File
    format: "http://edamontology.org/format_3652" # dta
steps:
  MS-Fit_01:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: input_1
    out: [MS-Fit_out_1]
  OpenMS_02:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_3
      OpenMS_in_3: MS-Fit_01/MS-Fit_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  PChopper_03:
    run: add-path-to-the-implementation/PChopper.cwl 
    in:
      PChopper_in_1: OpenMS_02/OpenMS_out_2
    out: [PChopper_out_1]
  esimsa_04:
    run: add-path-to-the-implementation/esimsa.cwl 
    in:
      esimsa_in_1: input_2
      esimsa_in_2: PChopper_03/PChopper_out_1
      esimsa_in_3: PChopper_03/PChopper_out_1
    out: [esimsa_out_1, esimsa_out_2, esimsa_out_3]
  esimsa_05:
    run: add-path-to-the-implementation/esimsa.cwl 
    in:
      esimsa_in_1: input_2
      esimsa_in_2: esimsa_04/esimsa_out_1
      esimsa_in_3: PChopper_03/PChopper_out_1
    out: [esimsa_out_1, esimsa_out_2, esimsa_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_1948" # nbrf/pir
    outputSource: esimsa_05/esimsa_out_1
