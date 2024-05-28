# WorkflowNo_1112
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1112
doc: A workflow including the tool(s) msConvert, idconvert, PeptideProphet, mzRecal, ProteinProphet, StPeter.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
steps:
  msConvert_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/msConvert/msConvert.cwl
    in:
      msConvert_in_1: input_1
    out: [msConvert_out_1]
  idconvert_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/idconvert/idconvert_to_pepXML.cwl
    in:
      idconvert_in_1: input_3
    out: [idconvert_out_1]
  PeptideProphet_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: idconvert_02/idconvert_out_1
      PeptideProphet_in_2: msConvert_01/msConvert_out_1
      PeptideProphet_in_3: input_2
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  mzRecal_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: msConvert_01/msConvert_out_1
      mzRecal_in_2: input_3
    out: [mzRecal_out_1]
  ProteinProphet_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_03/PeptideProphet_out_1
      ProteinProphet_in_2: input_2
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  StPeter_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/StPeter/StPeter.cwl
    in:
      StPeter_in_1: ProteinProphet_05/ProteinProphet_out_1
      StPeter_in_2: idconvert_02/idconvert_out_1
      StPeter_in_3: mzRecal_04/mzRecal_out_1
    out: [StPeter_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: StPeter_06/StPeter_out_1
