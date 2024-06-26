# WorkflowNo_1150
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1150
doc: A workflow including the tool(s) MassWiz, PEAKS Q, InDigestion, CrosstalkDB, DIA-Umpire.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3687" # ISA-TAB
  input_2:
    type: File
    format: "http://edamontology.org/format_3913" # Loom
  input_3:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
steps:
  MassWiz_01:
    run: add-path-to-the-implementation/MassWiz.cwl 
    in:
      MassWiz_in_1: input_3
    out: [MassWiz_out_1]
  PEAKS Q_02:
    run: add-path-to-the-implementation/PEAKS Q.cwl 
    in:
      PEAKS Q_in_1: MassWiz_01/MassWiz_out_1
    out: [PEAKS Q_out_1]
  InDigestion_03:
    run: add-path-to-the-implementation/InDigestion.cwl 
    in:
      InDigestion_in_1: input_1
    out: [InDigestion_out_1, InDigestion_out_2, InDigestion_out_3]
  CrosstalkDB_04:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: PEAKS Q_02/PEAKS Q_out_1
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  DIA-Umpire_05:
    run: add-path-to-the-implementation/DIA-Umpire.cwl 
    in:
      DIA-Umpire_in_1: input_3
      DIA-Umpire_in_2: CrosstalkDB_04/CrosstalkDB_out_3
      DIA-Umpire_in_3: InDigestion_03/InDigestion_out_3
    out: [DIA-Umpire_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
    outputSource: DIA-Umpire_05/DIA-Umpire_out_1
