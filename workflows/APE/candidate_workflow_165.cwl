# WorkflowNo_164
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_164
doc: A workflow including the tool(s) msConvert, XTandem, mzRecal, PeptideProphet, ProteinProphet.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
  input_3:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
steps:
  msConvert_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/msConvert/msConvert.cwl
    in:
      msConvert_in_1: input_2
    out: [msConvert_out_1]
  XTandem_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/XTandem/XTandem.cwl
    in:
      XTandem_in_1: msConvert_01/msConvert_out_1
      XTandem_in_2: input_1
    out: [XTandem_out_1]
  mzRecal_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: msConvert_01/msConvert_out_1
      mzRecal_in_2: input_3
    out: [mzRecal_out_1]
  PeptideProphet_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: XTandem_02/XTandem_out_1
      PeptideProphet_in_2: mzRecal_03/mzRecal_out_1
      PeptideProphet_in_3: input_1
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_04/PeptideProphet_out_1
      ProteinProphet_in_2: input_1
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
    outputSource: ProteinProphet_05/ProteinProphet_out_1
