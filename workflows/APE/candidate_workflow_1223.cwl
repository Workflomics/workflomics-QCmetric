# WorkflowNo_1222
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1222
doc: A workflow including the tool(s) InDigestion, CCdigest, OpenSWATH, PeptideProphet, OpenMS.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
  input_2:
    type: File
    format: "http://edamontology.org/format_3702" # MSF
  input_3:
    type: File
    format: "http://edamontology.org/format_3609" # qualillumina
steps:
  InDigestion_01:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_3
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  CCdigest_02:
    run: add-path-to-the-implementation/CCdigest.cwl 
    in:
      CCdigest_in_1: InDigestion_01/InDigestion_out_1
    out: [CCdigest_out_1]
  OpenSWATH_03:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_2
    out: [OpenSWATH_out_1]
  PeptideProphet_04:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: CCdigest_02/CCdigest_out_1
    out: [PeptideProphet_out_1]
  OpenMS_05:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: OpenSWATH_03/OpenSWATH_out_1
      OpenMS_in_2: input_1
      OpenMS_in_3: PeptideProphet_04/PeptideProphet_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenMS_05/OpenMS_out_1
