# Engine Versioning


The engine versioning is a key component of the BudConnect service. It is responsible for storing the engine versions, model compatibilities, and other engine related resources.

For the vllm engine, the build will be done from the forked version of the vllm repo with required changes to support the bud stack. The versioning will not be same as the vllm repo. But the versoning will be done based on the releases of Bud. 

The engine versions will be pushed to budstudio docker hub with respective tags.

| Device Architecture | Image Name | Version |
| ------------------- | ---------- | ------- |
| cuda                | budstudio/vllm-cuda | 0.1.0   |
| cpu                 | budstudio/vllm-cpu | 0.1.0   |
| rocm                | budstudio/vllm-rocm | 0.1.0   |
| hpu                 | budstudio/vllm-hpu | 0.1.0   |
