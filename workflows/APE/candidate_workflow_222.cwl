# WorkflowNo_221
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_221
doc: A workflow including the tool(s) Comet, PeptideProphet, ProteinProphet, idconvert, msConvert, StPeter.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
steps:
  Comet_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/Comet/Comet.cwl
    in:
      Comet_in_1: input_1
      Comet_in_2: input_2
    out: [Comet_out_1, Comet_out_2]
  PeptideProphet_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: Comet_01/Comet_out_1
      PeptideProphet_in_2: input_1
      PeptideProphet_in_3: input_2
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_02/PeptideProphet_out_1
      ProteinProphet_in_2: input_2
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  idconvert_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/idconvert/idconvert_to_pepXML.cwl
    in:
      idconvert_in_1: Comet_01/Comet_out_2
    out: [idconvert_out_1]
  msConvert_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/msConvert/msConvert.cwl
    in:
      msConvert_in_1: input_3
    out: [msConvert_out_1]
  StPeter_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/StPeter/StPeter.cwl
    in:
      StPeter_in_1: ProteinProphet_03/ProteinProphet_out_1
      StPeter_in_2: idconvert_04/idconvert_out_1
      StPeter_in_3: msConvert_05/msConvert_out_1
    out: [StPeter_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: StPeter_06/StPeter_out_1
