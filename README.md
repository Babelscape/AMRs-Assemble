# AMR Assemble! Ensembling Models for AMR Graphs

This is the repo for [*AMRs Assemble*!](https://arxiv.org/abs/2306.10786), a novel approach to AMR ensembling, presented at ACL 2023. This repository provides resources and tools for ensemble modeling of Abstract Meaning Representation (AMR) graphs. 

## Features


1. **Graph Perplexity Extraction**: We have extended the SPRING model to extract the perplexity of a graph based on a given sentence and model. This facilitates the subsequent selection of the most suitable graph, as discussed in the paper.

2. **Structural Problem Detection**: Introduces an algorithm to identify structural issues in AMR graphs, ensuring the integrity and consistency of parsed representations.

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
- `src/`: Contains the source code for extracting perplexity.
- `spring/`: SPRING repo.
- `structural-problems/`: Contains the source code for identifying structural issues in AMR graphs.
- `docs/`: Documentation and supplementary material related to the project.

## Clone Spring Repo

Clone and install [*SPRING*](https://github.com/SapienzaNLP/spring) repo in the root folder.

## Extract Perplexity

```shell script
python src/extract_perplexity.py \
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
python structural-problems/check_graphs.py \
    --input path/to/input_file
```

Replace path/to/input_file with the path to the file containing AMR graphs. The script will validate each graph and create separate files for correct and incorrect graphs in the same folder as the input file.

## Ensemble benchmark: Training, Validation, and Test Sets

Inside the benchmark folder, you will find separate files for training, validation, and test sets of predictions. These sets are pre-processed and labeled for evaluation purposes. You can use these sets to evaluate the performance of the AMR Graph Validator on different datasets.


## Extract best AMR graph  

The script select_best_graph.py is provided to extract the best AMR graph based on a specified score from multiple input files. This can be useful when you have multiple versions of AMR graphs and want to select the one with the highest score.

```shell script
python structural-problems/select_best_graph.py --path path/to/pred-amr1.txt path/to/pred-amr2.txt ... \
    --output data/tmp/amr3.0/best.amr.txt \ 
    --score-name perplexity \ 
```

## License
This project is released under the CC-BY-NC-SA 4.0 license (see `LICENSE`). If you use AMRs-Assemble!, please reference the paper and put a link to this repo.

## Contributing

We welcome contributions to the Cross-lingual AMR Aligner project. If you have any ideas, bug fixes, or improvements, feel free to open an issue or submit a pull request.

## Contact

For any questions or inquiries, please contact Abelardo Carlos Martínez Lorenzo at martines@babelscape.com or Pere-Lluís Huguet Cabot at huguetcabot@bablescape.com
