# WorkflowNo_1055
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1055
doc: A workflow including the tool(s) nontarget, DeconMSn, mMass, PeptideProphet, Libra.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
  input_2:
    type: File
    format: "http://edamontology.org/format_1972" # NCBI format
  input_3:
    type: File
    format: "http://edamontology.org/format_2568" # completely unambiguous pure nucleotide
steps:
  nontarget_01:
    run: add-path-to-the-implementation/nontarget.cwl 
    in:
      nontarget_in_1: input_3
      nontarget_in_2: input_2
      nontarget_in_3: input_3
    out: [nontarget_out_1, nontarget_out_2, nontarget_out_3]
  DeconMSn_02:
    run: add-path-to-the-implementation/DeconMSn.cwl 
    in:
      DeconMSn_in_1: input_1
      DeconMSn_in_2: input_1
    out: [DeconMSn_out_1, DeconMSn_out_2, DeconMSn_out_3]
  mMass_03:
    run: add-path-to-the-implementation/mMass.cwl 
    in:
      mMass_in_1: DeconMSn_02/DeconMSn_out_2
      mMass_in_2: nontarget_01/nontarget_out_2
    out: [mMass_out_1]
  PeptideProphet_04:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: mMass_03/mMass_out_1
    out: [PeptideProphet_out_1]
  Libra_05:
    run: add-path-to-the-implementation/Libra.cwl 
    in:
      Libra_in_1: PeptideProphet_04/PeptideProphet_out_1
    out: [Libra_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: Libra_05/Libra_out_1
