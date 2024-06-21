# ml-training-pipeline

This repository provides a comprehensive template for the management of reproducible data engineering pipelines in the context of audio neural network trainings. 

## Features

The configurable dataset pipeline includes modules for the following operations:
1. **Downloading:** Automates the download of raw audio data from various cloud storage solutions and then verifies the data's correctness. 
  
2. **Preprocessing:** 
Chains multiple preprocessing steps to prepare audio data for neural network training. 
  
  <!-- This includes
   - **Sample Rate Conversion**: Adjusts the sampling rate of audio files to a standard value that matches the input requirements of the neural network, ensuring consistency across all data.
  
   - **Bit-depth Conversion**: Modifies the bit depth of audio files to match the neural network's expected input format, which can help in reducing file size or aligning data quality.
  
   - **Gain Normalization**: Applies normalization of audio levels to ensure uniform loudness, which is crucial for maintaining model performance across varied inputs.
  
   - **Silence Trimming**: Removes periods of silence from the beginning and end of audio clips to minimize non-informative data and improve model training efficiency.
  
   - **Silence Addition**: Intentionally adds periods of silence to the audio data, which can help the neural network better handle pauses in speech or other audio signals during practical application.
  
  - **Trimming**:

  - **Shuffle**:
  
-->
  
3. **Augmentation:** Chains multiple data augmentation steps to increase the dataset size and introduce variability, essential for training robust neural network models.

<!--
  - **Stereo Split**
  - **Time Stretching**
  - **Pitch Shifting**
  - **Noise Injection**
  - **Reverberation**
 -->
   
4. **Analysis:** Provides tools for detailed analysis of audio data to assess quality and suitability for training purposes. 
   
5. **Database export:** Structures preprocessed and augmented data into a database format suitable for efficient querying and retrieval during model training.

____________________________________

The repository is used as a submodule in the repository [hpc-nn-template](https://github.com/tu-studio/hpc-nn-template), which is a main pipeline for the efficient and reproducible training of audio neural networks on the [HPC cluster of the Technical University of Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc).

## Install

```
git clone https://github.com/tu-studio/dataset-pipeline-template
```

## Usage



## Contributors

- [Michael Witte](https://github.com/michaelwitte)
- [Fares Schulz](https://github.com/faressc)

## License

