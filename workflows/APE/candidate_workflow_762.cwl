# WorkflowNo_761
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_761
doc: A workflow including the tool(s) MSiReader, MSiReader, Xtractor, MS-Fit, Libra.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
  input_2:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_3:
    type: File
    format: "http://edamontology.org/format_1504" # aaindex
steps:
  MSiReader_01:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_3
      MSiReader_in_2: input_2
    out: [MSiReader_out_1, MSiReader_out_2]
  MSiReader_02:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: MSiReader_01/MSiReader_out_2
      MSiReader_in_2: input_2
    out: [MSiReader_out_1, MSiReader_out_2]
  Xtractor_03:
    run: add-path-to-the-implementation/Xtractor.cwl 
    in:
      Xtractor_in_1: MSiReader_02/MSiReader_out_2
      Xtractor_in_2: input_3
      Xtractor_in_3: MSiReader_01/MSiReader_out_2
    out: [Xtractor_out_1, Xtractor_out_2, Xtractor_out_3]
  MS-Fit_04:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: Xtractor_03/Xtractor_out_2
    out: [MS-Fit_out_1]
  Libra_05:
    run: add-path-to-the-implementation/Libra.cwl 
    in:
      Libra_in_1: MS-Fit_04/MS-Fit_out_1
    out: [Libra_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: Libra_05/Libra_out_1
