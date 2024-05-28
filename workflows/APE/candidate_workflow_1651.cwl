# WorkflowNo_1650
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1650
doc: A workflow including the tool(s) Comet, mzRecal, idconvert, PeptideProphet, ProteinProphet, protXml2IdList.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_3:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
steps:
  Comet_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/Comet/Comet.cwl
    in:
      Comet_in_1: input_2
      Comet_in_2: input_1
    out: [Comet_out_1, Comet_out_2]
  mzRecal_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: input_2
      mzRecal_in_2: Comet_01/Comet_out_2
    out: [mzRecal_out_1]
  idconvert_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/idconvert/idconvert_to_pepXML.cwl
    in:
      idconvert_in_1: input_3
    out: [idconvert_out_1]
  PeptideProphet_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: idconvert_03/idconvert_out_1
      PeptideProphet_in_2: mzRecal_02/mzRecal_out_1
      PeptideProphet_in_3: input_1
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_04/PeptideProphet_out_1
      ProteinProphet_in_2: input_1
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  protXml2IdList_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/protXml2IdList/protXml2IdList.cwl
    in:
      protXml2IdList_in_1: ProteinProphet_05/ProteinProphet_out_1
    out: [protXml2IdList_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
    outputSource: protXml2IdList_06/protXml2IdList_out_1
