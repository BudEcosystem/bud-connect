Phase 0:
- Check if architectures.md exit. If so move to Phase 1
- In not exist Refer the archtiectures in budconnect/seeders/data/model_architectures.json and Create a checklist in architectures.md file to process each of the architecture. Each architecture name and task emtpy completion mark [ ]


Phase 1:
- Go through each architecture in architectures.md which is not marked completed.
- Take the one architecture and fill the details like tool_calling_parser_type, reasoning_parser_type, supports_lora, supports_pipeline_parallelism
- To get details of the architecture use deepwiki tool and serach vllm-project/vllm repo
- From the details received update the detail of the architecture and update task as completed [x]

EACH ITERATION:
- Make ONE architecture update
- If no task are pending output completion

OUTPUT <promise>FEATURE_READY</promise> when all task are marked completed
