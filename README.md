# HPC-Cluster-ML-Workflow 

A structured workflow template for audio ML research on the [HPC Cluster of ZECM - TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc). This template integrates state-of-the-art tools, including DVC, Docker and TensorBoard, to provide comprehensive development and managment capabilities for audio machine learning experiments. The workflow is ideally suited for projects that involve managing multiple experiments over an extended period. 

## Features
- **Reproducible Experiments**: 
  - Comprehensive versioning of dependencies, pipelines, and artifacts.
  - Containerized execution environments ensure consistent and repeatable results across different systems.
- **Resource Optimization**: Efficient storage management through a shared cache system of DVC, optimizing resource utilization across experiments.
- **Automation**: Streamlined workflows for builds, data pipelines, parallel execution, and remote syncing, minimizing manual intervention and enhancing productivity.
- **HPC Integration**: 
   - Custom implementation enabling parallel DVC experiments across multiple nodes, extending DVC's native single-node parallel execution capabilities.
   - Utilizes Singularity's Docker support for convenient container conversion, simplifying the process of creating and deploying Singularity images in HPC contexts.
- **Tensorboard Integration**: Comprehensive overview of DVC experiments within TensorBoard, allowing comparison and analysis of results while having TensorBoard's ability to log audio samples.
- **Real-time Monitoring**: Offer live tracking and visualization of experiment metrics, enabling immediate insights and possible termination of flawed experiments.

## Overview

The following table summarizes the key tools involved in the HPC-Cluster-ML-Workflow, along with their primary roles and links to their official documentation for further reference.

<table align="center" style="width: 60%; border-collapse: collapse;">
  <tr>
    <th>Tool</th>
    <th>Role</th>
    <th>Documentation</th>
  </tr>
  <tr>
    <td><b>Git</b></td>
    <td>Version control for code and configuration management.</td>
    <td><a href="https://git-scm.com/doc">Git Docs</a></td>
  </tr>
  <tr>
    <td><b>DVC</b></td>
    <td>Data version control and pipeline management.</td>
    <td><a href="https://dvc.org/doc">DVC Docs</a></td>
  </tr>
  <tr>
    <td><b>TensorBoard</b></td>
    <td>ML experiment visualization and monitoring.</td>
    <td><a href="https://www.tensorflow.org/tensorboard">TensorBoard Docs</a></td>
  </tr>
  <tr>
    <td><b>Docker</b></td>
    <td>Containerization tool, used for conversion to Singularity images.</td>
    <td><a href="https://docs.docker.com">Docker Docs</a></td>
  </tr>
  <tr>
    <td><b>Singularity</b></td>
    <td>HPC-compatible containerization tool.</td>
    <td><a href="https://docs.sylabs.io">Singularity Docs</a></td>
  </tr>
  <tr>
    <td><b>SLURM</b></td>
    <td>Job scheduling and workload management on the HPC-Cluster.</td>
    <td><a href="https://slurm.schedmd.com/documentation.html">SLURM Docs</a></td>
  </tr>
</table>

### System Transfer
The figure below provides a simplified overview of how data is transferred between systems in this workflow. Some of the commands shown are automated with the provided scripts, so the visualization is for comprehension, not direct usage reference.
        <p align="center">
        <img src="docs/graphics/Dependency_Transfer_Simplified.png" alt="Simplified diagram of dependency transfer between systems" width="690">
        </p>

## Prerequisites
- macOS or Linux operating system.
- Access to the HPC Cluster.
- Local Python installation.
- Familiarity with Git, DVC, and Docker.
- Docker Hub account.

## Setup and Usage

The template includes a simple PyTorch example project (a neural guitar amp simulation), which can be edited and reused, or just used as a reference. 

- [Setup Instructions](docs/SETUP.md)
- [User Guide](docs/USAGE.md)

## Contributors

- [Michael Witte](https://github.com/michaelwitte)
- [Fares Schulz](https://github.com/faressc)

## License

This project is licensed under the terms of the [MIT License](LICENSE.md). 

## References

**Faressc. (n.d.). *Guitar LSTM* [pytorch-version]. GitHub. [Link](https://github.com/faressc/GuitarLSTM/tree/main/pytorch-version)**

