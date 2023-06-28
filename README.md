# AMR Assemble! Ensembling Models for AMR Graphs

This is the repo for [*{AMR}s {A}ssemble*!](https://arxiv.org/abs/2306.10786), a novel approach to AMR ensembling, presented at ACL 2023. This repository provides resources and tools for ensemble modeling of Abstract Meaning Representation (AMR) graphs. 

## Features


1. **Graph Perplexity Extraction**: "We have extended the SPRING model to extract the perplexity of a graph based on a given sentence and model. This facilitates the subsequent selection of the most suitable graph, as discussed in the paper.

2. **Structural Problem Detection**: Introduces an algorithm to identify structural issues in AMR graphs, ensuring integrity and consistency of parsed representations.

3. **Corpus Release**: Provides a training, validation, and test corpus of predictions for training AMR ensemble models and establishing a standardized benchmark.

If you use the code, please reference this work in your paper:

```
@inproceedings{martinez-etal-2023-assemble,
    title = {{AMR}s {A}ssemble! {L}earning to {E}nsemble with {A}utoregressive {M}odels for {AMR} parsing},
    author = {Martínez Lorenzo, Abelardo Carlos and Huguet Cabot, Pere-Lluís and Navigli, Roberto},
    booktitle = {Proceedings of ACL},
    year = {2023}
}
```


## Contents

The repository is organized as follows:

- `benchmark/`: Contains the datasets for establishing a standardized benchmark to evaluate AMR ensembling models, ensuring fair comparisons.
- `bin/`: Contains the source code for training  the SPRING model, conducting inference, and extracting perplexity.
- `config/`: Contains configuration files for training the SPRING model.
- `data/`: should contain the training, validation, and test corpora, along with the necessary vocab of SPRING.
- `structural-problems/`: Contains the source code for identifying structural issues in AMR graphs.
- `spring_amr/`: Contains the SPRING model code.
- `docs/`: Documentation and supplementary material related to the project.

## Pretrained Checkpoints

Here we releasea SPRING model.

### Text-to-AMR Parsing
- Model trained in the AMR 3.0 training set: [AMR3.parsing-1.0.tar.bz2](http://nlp.uniroma1.it/AMR/AMR3.parsing-1.0.tar.bz2)

If you need the checkpoints of other experiments in the paper, please send us an email.

## Installation
```shell script
cd spring
pip install -r requirements.txt
pip install -e .
```

The code only works with `transformers` < 3.0 because of a disrupting change in positional embeddings.
The code works fine with `torch` 1.5. We recommend the usage of a new `conda` env.


## Extract Perplexity

```shell script
python python bin/extract_perplexity.py \
    --pred-path data/tmp/amr3.0/pred.amr.txt \
    --perplexity-path data/tmp/amr3.0/pred.perplexity.amr.txt \ 
    --checkpoint  runs/<checkpoint>.pt  \
    --batch-size 500 \
    --device cuda \
    --penman-linearization --use-pointer-tokens
```

## Validate AMR graphs

To check the correctness of AMR graphs and generate files for incorrect graphs, use the following command:

```shell script
python python bin/extract_perplexity.py \
    --input path/to/input_file
```

Replace path/to/input_file with the path to the file containing AMR graphs. The script will validate each graph and create separate files for correct and incorrect graphs in the same folder as the input file.

## Ensemble benchmark: Training, Validation, and Test Sets

Inside the benchmark folder, you will find separate files for training, validation, and test sets of predictions. These sets are pre-processed and labeled for evaluation purposes. You can use these sets to evaluate the performance of the AMR Graph Validator on different datasets.


## Extract best AMR graph  

The script select_best_graph.py is provided to extract the best AMR graph based on a specified score from multiple input files. This can be useful when you have multiple versions of AMR graphs and want to select the one with the highest score.

```shell script
python select_best_graph.py --path path/to/pred-amr1.txt path/to/pred-amr2.txt ... \
    --output data/tmp/amr3.0/best.amr.txt \ 
    --score-name perplexity \ 
```

## Previous SPRING code

### Train
Modify `sweeped.yaml` in `configs`. Instructions in comments within the file. Also see the [appendix](docs/appendix.pdf).

#### Text-to-AMR
```shell script
python bin/train.py --config configs/config.yaml --direction amr
```
Results in `runs/`

#### AMR-to-Text
```shell script
python bin/train.py --config configs/config.yaml --direction text
```
Results in `runs/`

### Evaluate
#### Text-to-AMR
```shell script
python bin/predict_amrs.py \
    --datasets <AMR-ROOT>/data/amrs/split/test/*.txt \
    --gold-path data/tmp/amr2.0/gold.amr.txt \
    --pred-path data/tmp/amr2.0/pred.amr.txt \
    --checkpoint runs/<checkpoint>.pt \
    --beam-size 5 \
    --batch-size 500 \
    --device cuda \
    --penman-linearization --use-pointer-tokens
```
`gold.amr.txt` and `pred.amr.txt` will contain, respectively, the concatenated gold and the predictions.

To reproduce our paper's results, you will also need need to run the [BLINK](https://github.com/facebookresearch/BLINK) 
entity linking system on the prediction file (`data/tmp/amr2.0/pred.amr.txt` in the previous code snippet). 
To do so, you will need to install BLINK, and download their models:
```shell script
git clone https://github.com/facebookresearch/BLINK.git
cd BLINK
pip install -r requirements.txt
sh download_blink_models.sh
cd models
wget http://dl.fbaipublicfiles.com/BLINK//faiss_flat_index.pkl
cd ../..
```
Then, you will be able to launch the `blinkify.py` script:
```shell
python bin/blinkify.py \
    --datasets data/tmp/amr2.0/pred.amr.txt \
    --out data/tmp/amr2.0/pred.amr.blinkified.txt \
    --device cuda \
    --blink-models-dir BLINK/models
```
To have comparable Smatch scores you will also need to use the scripts available at https://github.com/mdtux89/amr-evaluation, which provide
results that are around ~0.3 Smatch points lower than those returned by `bin/predict_amrs.py`.

#### AMR-to-Text
```shell script
python bin/predict_sentences.py \
    --datasets <AMR-ROOT>/data/amrs/split/test/*.txt \
    --gold-path data/tmp/amr2.0/gold.text.txt \
    --pred-path data/tmp/amr2.0/pred.text.txt \
    --checkpoint runs/<checkpoint>.pt \
    --beam-size 5 \
    --batch-size 500 \
    --device cuda \
    --penman-linearization --use-pointer-tokens
```
`gold.text.txt` and `pred.text.txt` will contain, respectively, the concatenated gold and the predictions.
For BLEU, chrF++, and Meteor in order to be comparable you will need to tokenize both gold and predictions using [JAMR tokenizer](https://github.com/redpony/cdec/blob/master/corpus/tokenize-anything.sh).
To compute BLEU and chrF++, please use `bin/eval_bleu.py`. For METEOR, use https://www.cs.cmu.edu/~alavie/METEOR/ .
For BLEURT don't use tokenization and run the eval with `https://github.com/google-research/bleurt`. Also see the [appendix](docs/appendix.pdf).

### Linearizations
The previously shown commands assume the use of the DFS-based linearization. To use BFS or PENMAN decomment the relevant lines in `configs/config.yaml` (for training). As for the evaluation scripts, substitute the `--penman-linearization --use-pointer-tokens` line with `--use-pointer-tokens` for BFS or with `--penman-linearization` for PENMAN.

### License
This project is released under the CC-BY-NC-SA 4.0 license (see `LICENSE`). If you use AMRs-Assemble!, please put a link to this repo.

