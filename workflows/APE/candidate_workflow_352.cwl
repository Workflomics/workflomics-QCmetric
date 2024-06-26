# WorkflowNo_351
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_351
doc: A workflow including the tool(s) CrosstalkDB, nontarget, PRIDE Toolsuite, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_2:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
  input_3:
    type: File
    format: "http://edamontology.org/format_1948" # nbrf/pir
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  nontarget_02:
    run: add-path-to-the-implementation/nontarget.cwl 
    in:
      nontarget_in_1: input_2
      nontarget_in_2: input_2
      nontarget_in_3: input_3
    out: [nontarget_out_1, nontarget_out_2, nontarget_out_3]
  PRIDE Toolsuite_03:
    run: add-path-to-the-implementation/PRIDE Toolsuite.cwl 
    in:
      PRIDE Toolsuite_in_1: CrosstalkDB_01/CrosstalkDB_out_3
    out: [PRIDE Toolsuite_out_1]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: PRIDE Toolsuite_03/PRIDE Toolsuite_out_1
      OpenSWATH_in_2: nontarget_02/nontarget_out_3
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
