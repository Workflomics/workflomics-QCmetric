# WorkflowNo_1502
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1502
doc: A workflow including the tool(s) XTandem, mzRecal, XTandem, PeptideProphet, ProteinProphet, StPeter.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
  input_3:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
steps:
  XTandem_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/XTandem/XTandem.cwl
    in:
      XTandem_in_1: input_3
      XTandem_in_2: input_1
    out: [XTandem_out_1]
  mzRecal_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: input_3
      mzRecal_in_2: input_2
    out: [mzRecal_out_1]
  XTandem_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/XTandem/XTandem.cwl
    in:
      XTandem_in_1: input_3
      XTandem_in_2: input_1
    out: [XTandem_out_1]
  PeptideProphet_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: XTandem_01/XTandem_out_1
      PeptideProphet_in_2: input_3
      PeptideProphet_in_3: input_1
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_04/PeptideProphet_out_1
      ProteinProphet_in_2: input_1
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  StPeter_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/StPeter/StPeter.cwl
    in:
      StPeter_in_1: ProteinProphet_05/ProteinProphet_out_1
      StPeter_in_2: XTandem_03/XTandem_out_1
      StPeter_in_3: mzRecal_02/mzRecal_out_1
    out: [StPeter_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: StPeter_06/StPeter_out_1
