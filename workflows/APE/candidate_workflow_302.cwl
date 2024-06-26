# WorkflowNo_301
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_301
doc: A workflow including the tool(s) CrosstalkDB, CrosstalkDB, mspire_mspire-sequest, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_2:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
  input_3:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  CrosstalkDB_02:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: CrosstalkDB_01/CrosstalkDB_out_3
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  mspire_mspire-sequest_03:
    run: add-path-to-the-implementation/mspire_mspire-sequest.cwl 
    in:
      mspire_mspire-sequest_in_1: CrosstalkDB_02/CrosstalkDB_out_4
    out: [mspire_mspire-sequest_out_1]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: mspire_mspire-sequest_03/mspire_mspire-sequest_out_1
      OpenSWATH_in_2: input_3
    out: [OpenSWATH_out_1]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_04/OpenSWATH_out_1
      Mascot Server_in_2: input_3
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
    outputSource: Mascot Server_05/Mascot Server_out_1
