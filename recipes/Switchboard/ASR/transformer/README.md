# Switchboard ASR with Transformers.
This folder contains the scripts to train a Transformer-based speech recognizer
using the Switchboard corpus.

You can download the Switchboard data at https://catalog.ldc.upenn.edu/LDC97S62.

The eval2000/Hub5 English test set can be found at:
- Speech data: https://catalog.ldc.upenn.edu/LDC2002S09
- Transcripts: https://catalog.ldc.upenn.edu/LDC2002T43

Part 1 and part 2 of the Fisher corpus are available at:
- https://catalog.ldc.upenn.edu/LDC2004T19
- https://catalog.ldc.upenn.edu/LDC2005T19


# How to run
`python train.py hparams/<hparam_file>.yaml`

# Results

| Release | hyperparams file | Swbd WER | Callhome WER | Full Eval2000 | HuggingFace link | Model link | GPUs | Comment
|:-------------:|:---------------------------:| :-----:| :-----:| :-----:| :-----:| :-----:| :--------:|:--------:|
| 21-05-22 | transformer.yaml | 22.00 | 30.12 | -  | n.a. | n.a. | 1xA100 40GB | This model uses Tokenizer+LM pretrained on LibriSpeech|
| 21-05-22 | transformer.yaml | - | - | -  | n.a. | n.a. | 1xA100 40GB | This model uses the LibriSpeech LM but finetuned on Swbd+Fisher data (see ../../LM/hparams/transformer_finetune.yaml)|
| 01-07-22 | transformer_small_lm.yaml| 9.64 | 17.97 | 13.99  | n.a. | n.a. | 1xA100 40GB | This model uses an LM trained on Swbd+Fisher data (see ../../LM/hparams/transformer_finetune.yaml)|

# Training Time
It takes about 45 minutes for each epoch on 1 NVIDIA A100 (40GB).


# **About SpeechBrain**
- Website: https://speechbrain.github.io/
- Code: https://github.com/speechbrain/speechbrain/
- HuggingFace: https://huggingface.co/speechbrain/


# **Citing SpeechBrain**
Please, cite SpeechBrain if you use it for your research or business.

```bibtex
@misc{speechbrain,
  title={{SpeechBrain}: A General-Purpose Speech Toolkit},
  author={Mirco Ravanelli and Titouan Parcollet and Peter Plantinga and Aku Rouhe and Samuele Cornell and Loren Lugosch and Cem Subakan and Nauman Dawalatabad and Abdelwahab Heba and Jianyuan Zhong and Ju-Chieh Chou and Sung-Lin Yeh and Szu-Wei Fu and Chien-Feng Liao and Elena Rastorgueva and François Grondin and William Aris and Hwidong Na and Yan Gao and Renato De Mori and Yoshua Bengio},
  year={2021},
  eprint={2106.04624},
  archivePrefix={arXiv},
  primaryClass={eess.AS},
  note={arXiv:2106.04624}
}
```
