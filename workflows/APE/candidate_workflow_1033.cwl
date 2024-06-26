# WorkflowNo_1032
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1032
doc: A workflow including the tool(s) CrosstalkDB, esimsa, MSiReader, ComPIL, IsobariQ.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1216" # unambiguous pure rna sequence
  input_2:
    type: File
    format: "http://edamontology.org/format_3752" # CSV
  input_3:
    type: File
    format: "http://edamontology.org/format_2001" # EMBOSS simple format
steps:
  CrosstalkDB_01:
    run: add-path-to-the-implementation/CrosstalkDB.cwl 
    in:
      CrosstalkDB_in_1: input_2
    out: [CrosstalkDB_out_1, CrosstalkDB_out_2, CrosstalkDB_out_3, CrosstalkDB_out_4]
  esimsa_02:
    run: add-path-to-the-implementation/esimsa.cwl 
    in:
      esimsa_in_1: input_1
      esimsa_in_2: input_3
      esimsa_in_3: input_3
    out: [esimsa_out_1, esimsa_out_2, esimsa_out_3]
  MSiReader_03:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: esimsa_02/esimsa_out_2
      MSiReader_in_2: CrosstalkDB_01/CrosstalkDB_out_3
    out: [MSiReader_out_1, MSiReader_out_2]
  ComPIL_04:
    run: add-path-to-the-implementation/ComPIL.cwl 
    in:
      ComPIL_in_1: MSiReader_03/MSiReader_out_2
    out: [ComPIL_out_1]
  IsobariQ_05:
    run: add-path-to-the-implementation/IsobariQ.cwl 
    in:
      IsobariQ_in_1: ComPIL_04/ComPIL_out_1
    out: [IsobariQ_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
    outputSource: IsobariQ_05/IsobariQ_out_1
