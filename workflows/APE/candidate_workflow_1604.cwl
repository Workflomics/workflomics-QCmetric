# WorkflowNo_1603
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1603
doc: A workflow including the tool(s) PeptideProphet, Multi-Q, MSiReader, msaccess, esimsa.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_2:
    type: File
    format: "http://edamontology.org/format_3655" # pepXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3785" # BioNLP Shared Task format
steps:
  PeptideProphet_01:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: input_2
    out: [PeptideProphet_out_1]
  Multi-Q_02:
    run: add-path-to-the-implementation/Multi-Q.cwl 
    in:
      Multi-Q_in_1: input_1
      Multi-Q_in_2: input_2
    out: [Multi-Q_out_1]
  MSiReader_03:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: input_1
      MSiReader_in_2: Multi-Q_02/Multi-Q_out_1
    out: [MSiReader_out_1, MSiReader_out_2]
  msaccess_04:
    run: add-path-to-the-implementation/msaccess.cwl 
    in:
      msaccess_in_1: input_1
      msaccess_in_2: PeptideProphet_01/PeptideProphet_out_1
    out: [msaccess_out_1, msaccess_out_2, msaccess_out_3]
  esimsa_05:
    run: add-path-to-the-implementation/esimsa.cwl 
    in:
      esimsa_in_1: input_3
      esimsa_in_2: msaccess_04/msaccess_out_1
      esimsa_in_3: MSiReader_03/MSiReader_out_2
    out: [esimsa_out_1, esimsa_out_2, esimsa_out_3]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3881" # AMBER top
    outputSource: esimsa_05/esimsa_out_1
